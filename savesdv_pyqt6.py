from __future__ import annotations

import sys
import webbrowser
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QComboBox, QDialog, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPushButton, QSpinBox, QVBoxLayout, QWidget

from savesdv.core import SaveEditor, SaveEditorError
from savesdv.i18n import LANGUAGES, tr

ROOT = Path(__file__).resolve().parent


class BackupDialog(QDialog):
    def __init__(self, editor, lang, parent=None):
        super().__init__(parent)
        self.editor, self.lang = editor, lang
        self.setWindowTitle(tr(lang, "backups_window"))
        self.resize(760, 430)
        layout = QVBoxLayout(self)
        self.list = QListWidget(); layout.addWidget(self.list)
        row = QHBoxLayout()
        restore = QPushButton(tr(lang, "restore")); back = QPushButton(tr(lang, "cancel"))
        restore.clicked.connect(self.restore_selected); back.clicked.connect(self.reject)
        row.addWidget(restore); row.addWidget(back); layout.addLayout(row)
        self.reload()

    def reload(self):
        self.list.clear(); backups = self.editor.list_backups()
        for path in backups: self.list.addItem(QListWidgetItem(path.name))
        if not backups: self.list.addItem(QListWidgetItem(tr(self.lang, "no_backups")))

    def restore_selected(self):
        item = self.list.currentItem()
        if not item or item.text() == tr(self.lang, "no_backups"): return
        try: out = self.editor.restore_backup(self.editor.backups_dir / item.text())
        except SaveEditorError as exc:
            QMessageBox.critical(self, tr(self.lang, "invalid"), str(exc)); return
        QMessageBox.information(self, tr(self.lang, "restore"), tr(self.lang, "restore_done", path=out))


class EditorDialog(QDialog):
    def __init__(self, editor, path, lang, parent=None):
        super().__init__(parent)
        self.editor, self.path, self.lang = editor, Path(path), lang
        self.data, mods = editor.load(self.path)
        self.setWindowTitle(tr(lang, "editing_title", name=self.data.player_name))
        self.resize(560, 320)
        root = QVBoxLayout(self)
        note = QLabel(tr(lang, "backup_confirm")); note.setWordWrap(True); root.addWidget(note)
        form = QFormLayout()
        self.player = QLineEdit(self.data.player_name); self.farm = QLineEdit(self.data.farm_name)
        self.money = QSpinBox(); self.money.setRange(-2147483648, 2147483647); self.money.setValue(self.data.money)
        form.addRow(tr(lang, "player_name"), self.player); form.addRow(tr(lang, "farm_name"), self.farm); form.addRow(tr(lang, "money"), self.money); root.addLayout(form)
        row = QHBoxLayout(); save = QPushButton(tr(lang, "save_changes")); cancel = QPushButton(tr(lang, "cancel"))
        save.clicked.connect(self.save); cancel.clicked.connect(self.reject); row.addWidget(save); row.addWidget(cancel); root.addLayout(row)
        if mods:
            QMessageBox.warning(self, tr(lang, "mods_title"), tr(lang, "mods_warning") + "\n\nDetected: " + ", ".join(mods))

    def save(self):
        try:
            backup = self.editor.edit(self.path, self.player.text(), self.farm.text(), self.money.value())
        except SaveEditorError as exc:
            QMessageBox.critical(self, tr(self.lang, "invalid"), str(exc)); return
        QMessageBox.information(self, tr(self.lang, "saved"), tr(self.lang, "backup_created", path=backup)); self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.editor = SaveEditor(); self.lang = "English"; self.setMinimumSize(800, 520); self.build()

    def build(self):
        self.setWindowTitle(tr(self.lang, "main_title"))
        central = QWidget(); self.setCentralWidget(central); outer = QVBoxLayout(central)
        top = QHBoxLayout(); top.addStretch()
        self.lang_box = QComboBox(); self.lang_box.addItems(LANGUAGES); self.lang_box.setCurrentText(self.lang); self.lang_box.currentTextChanged.connect(self.language_changed)
        top.addWidget(QLabel(tr(self.lang, "language"))); top.addWidget(self.lang_box)
        github = QPushButton(tr(self.lang, "github")); github.setIcon(QIcon(str(ROOT / "assets" / "github.svg"))); github.clicked.connect(lambda: webbrowser.open("https://github.com/rlFedotovDev/SaveSDV")); top.addWidget(github); outer.addLayout(top)
        title = QLabel("SaveSDV"); title.setAlignment(Qt.AlignmentFlag.AlignCenter); title.setStyleSheet("font-size: 34px; font-weight: 700;")
        outer.addStretch(); outer.addWidget(title, 0, Qt.AlignmentFlag.AlignHCenter)
        edit = QPushButton(tr(self.lang, "edit_save")); edit.setMinimumHeight(54); edit.clicked.connect(self.open_editor); outer.addWidget(edit)
        backups = QPushButton(tr(self.lang, "view_backups")); backups.setMinimumHeight(54); backups.clicked.connect(self.open_backups); outer.addWidget(backups)
        outer.addStretch(); footer = QLabel(tr(self.lang, "footer")); footer.setWordWrap(True); footer.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom); outer.addWidget(footer)

    def language_changed(self, lang): self.lang = lang; self.build()

    def open_editor(self):
        path, _ = QFileDialog.getOpenFileName(self, tr(self.lang, "choose_file"), "", "Stardew Valley save (*);;All files (*)")
        if not path: return
        try: EditorDialog(self.editor, Path(path), self.lang, self).exec()
        except SaveEditorError as exc: QMessageBox.critical(self, tr(self.lang, "invalid"), str(exc))

    def open_backups(self): BackupDialog(self.editor, self.lang, self).exec()


def main():
    app = QApplication(sys.argv); window = MainWindow(); window.show(); sys.exit(app.exec())


if __name__ == "__main__": main()
