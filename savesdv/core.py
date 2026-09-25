from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET


APP_NAME = "SaveSDV"
VERSION = "1.0"


@dataclass
class SaveData:
    path: Path
    player_name: str
    farm_name: str
    money: int


class SaveEditorError(Exception):
    pass


class SaveEditor:
    """Safe shared save-editing logic used by all Python UIs."""

    def __init__(self, backups_dir: Path | None = None):
        self.backups_dir = backups_dir or (Path(__file__).resolve().parent.parent / "backups")
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _find_player(root: ET.Element) -> ET.Element:
        for elem in root.iter():
            if elem.tag.rsplit("}", 1)[-1] == "player":
                return elem
        raise SaveEditorError("Could not find the <player> element in this save.")

    @staticmethod
    def _child_text(parent: ET.Element, name: str, default: str = "") -> str:
        for child in parent:
            if child.tag.rsplit("}", 1)[-1] == name:
                return child.text or default
        return default

    @staticmethod
    def _set_child_text(parent: ET.Element, name: str, value: str) -> None:
        for child in parent:
            if child.tag.rsplit("}", 1)[-1] == name:
                child.text = value
                return
        child = ET.SubElement(parent, name)
        child.text = value

    @staticmethod
    def detect_mods(root: ET.Element, raw_xml: str = "") -> list[str]:
        """Heuristic only: modded saves are not universally identifiable from XML alone."""
        found: list[str] = []
        lower = raw_xml.lower()

        signals = (
            ("modData", "moddata"),
            ("SMAPI", "smapi"),
            ("spacechase0", "spacechase0"),
            ("Pathoschild", "pathoschild"),
        )
        for label, needle in signals:
            if needle in lower:
                found.append(label)

        for elem in root.iter():
            tag = elem.tag.rsplit("}", 1)[-1]
            if tag.lower() == "moddata" and "modData" not in found:
                found.append("modData")
            for attr in elem.attrib:
                if "mod" in attr.lower() and f"attribute:{attr}" not in found:
                    found.append(f"attribute:{attr}")

        return found

    def load(self, path: str | Path) -> tuple[SaveData, list[str]]:
        path = Path(path)
        if not path.exists() or not path.is_file():
            raise SaveEditorError(f"Save file does not exist: {path}")

        try:
            raw = path.read_text(encoding="utf-8")
            root = ET.fromstring(raw)
        except (OSError, UnicodeError, ET.ParseError) as exc:
            raise SaveEditorError(f"Could not read or parse the save: {exc}") from exc

        player = self._find_player(root)
        player_name = self._child_text(player, "name")
        farm_name = self._child_text(player, "farmName")
        try:
            money = int(self._child_text(player, "money", "0"))
        except ValueError:
            money = 0

        self._cached_tree = root
        self._cached_path = path
        return SaveData(path, player_name, farm_name, money), self.detect_mods(root, raw)

    def create_backup(self, save_path: Path) -> Path:
        """Backup the entire save folder before modifying it."""
        save_path = save_path.resolve()
        save_dir = save_path.parent
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", save_path.name)[:80]
        backup = self.backups_dir / f"{safe_name}_{timestamp}.zip"

        with zipfile.ZipFile(backup, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for item in save_dir.rglob("*"):
                if item.is_file():
                    zf.write(item, item.relative_to(save_dir))
        return backup

    def edit(self, path: str | Path, player_name: str, farm_name: str, money: int) -> Path:
        path = Path(path)
        _, _ = self.load(path)
        root = self._cached_tree
        player = self._find_player(root)

        # Never overwrite the original before the backup exists.
        backup = self.create_backup(path)

        self._set_child_text(player, "name", player_name)
        self._set_child_text(player, "farmName", farm_name)
        self._set_child_text(player, "money", str(int(money)))

        try:
            ET.indent(root, space="  ")
        except AttributeError:
            pass

        temp_path = path.with_name(path.name + ".savesdv-tmp")
        try:
            ET.ElementTree(root).write(temp_path, encoding="utf-8", xml_declaration=True)
            temp_path.replace(path)
        except OSError as exc:
            temp_path.unlink(missing_ok=True)
            raise SaveEditorError(f"Could not write the save: {exc}") from exc

        return backup

    def list_backups(self) -> list[Path]:
        return sorted(self.backups_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)

    def restore_backup(self, backup_path: str | Path, destination_dir: str | Path | None = None) -> Path:
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise SaveEditorError("Backup does not exist.")

        if destination_dir is None:
            destination_dir = self.backups_dir / f"{backup_path.stem}_restored"
        destination_dir = Path(destination_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(backup_path, "r") as zf:
                members = [m for m in zf.infolist() if not m.is_dir()]
                if not members:
                    raise SaveEditorError("The backup is empty.")
                # Avoid Zip Slip when restoring a backup.
                root = destination_dir.resolve()
                for member in members:
                    target = (destination_dir / member.filename).resolve()
                    if root not in target.parents and target != root:
                        raise SaveEditorError("The backup contains an unsafe path.")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as src, target.open("wb") as dst:
                        dst.write(src.read())
        except zipfile.BadZipFile as exc:
            raise SaveEditorError(f"Invalid backup archive: {exc}") from exc

        return destination_dir
