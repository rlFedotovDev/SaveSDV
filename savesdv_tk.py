from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import webbrowser

from savesdv.core import SaveEditor, SaveEditorError
from savesdv.i18n import LANGUAGES, tr


class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.editor = SaveEditor(); self.lang = "English"; self.geometry("820x540"); self.minsize(760, 500); self.build_main()

    def build_main(self):
        for child in self.winfo_children(): child.destroy()
        self.title(tr(self.lang, "main_title"))
        top = ttk.Frame(self); top.pack(fill="x", padx=16, pady=16)
        ttk.Label(top, text=tr(self.lang, "language")).pack(side="left")
        self.lang_var = tk.StringVar(value=self.lang)
        box = ttk.Combobox(top, textvariable=self.lang_var, values=LANGUAGES, state="readonly", width=18); box.pack(side="left", padx=8); box.bind("<<ComboboxSelected>>", lambda _e: self.change_language())
        ttk.Button(top, text=tr(self.lang, "github"), command=lambda: webbrowser.open("https://github.com/rlFedotovDev/SaveSDV")).pack(side="right")
        center = ttk.Frame(self); center.pack(expand=True)
        ttk.Label(center, text="SaveSDV", font=("TkDefaultFont", 28, "bold")).pack(pady=(30, 24))
        ttk.Button(center, text=tr(self.lang, "edit_save"), command=self.open_editor, width=34).pack(pady=8, ipady=8)
        ttk.Button(center, text=tr(self.lang, "view_backups"), command=self.open_backups, width=34).pack(pady=8, ipady=8)
        ttk.Label(self, text=tr(self.lang, "footer"), wraplength=760, justify="right").pack(side="bottom", anchor="e", padx=16, pady=12)

    def change_language(self): self.lang = self.lang_var.get(); self.build_main()

    def open_editor(self):
        path = filedialog.askopenfilename(title=tr(self.lang, "choose_file"))
        if not path: return
        try: data, mods = self.editor.load(path)
        except SaveEditorError as exc: messagebox.showerror(tr(self.lang, "invalid"), str(exc)); return
        win = tk.Toplevel(self); win.title(tr(self.lang, "editing_title", name=data.player_name)); win.geometry("560x330"); win.transient(self)
        if mods: messagebox.showwarning(tr(self.lang, "mods_title"), tr(self.lang, "mods_warning") + "\n\nDetected: " + ", ".join(mods), parent=win)
        ttk.Label(win, text=tr(self.lang, "backup_confirm"), wraplength=510).pack(padx=20, pady=14)
        form = ttk.Frame(win); form.pack(fill="x", padx=20, pady=6)
        ttk.Label(form, text=tr(self.lang, "player_name")).grid(row=0, column=0, sticky="w", pady=8); player = ttk.Entry(form); player.insert(0, data.player_name); player.grid(row=0, column=1, sticky="ew", padx=10)
        ttk.Label(form, text=tr(self.lang, "farm_name")).grid(row=1, column=0, sticky="w", pady=8); farm = ttk.Entry(form); farm.insert(0, data.farm_name); farm.grid(row=1, column=1, sticky="ew", padx=10)
        ttk.Label(form, text=tr(self.lang, "money")).grid(row=2, column=0, sticky="w", pady=8); money = tk.IntVar(value=data.money); ttk.Spinbox(form, from_=-2147483648, to=2147483647, textvariable=money).grid(row=2, column=1, sticky="ew", padx=10); form.columnconfigure(1, weight=1)
        buttons = ttk.Frame(win); buttons.pack(pady=14)
        def save():
            try: backup = self.editor.edit(path, player.get(), farm.get(), money.get())
            except (SaveEditorError, tk.TclError, ValueError) as exc: messagebox.showerror(tr(self.lang, "invalid"), str(exc), parent=win); return
            messagebox.showinfo(tr(self.lang, "saved"), tr(self.lang, "backup_created", path=backup), parent=win); win.destroy()
        ttk.Button(buttons, text=tr(self.lang, "save_changes"), command=save).pack(side="left", padx=8); ttk.Button(buttons, text=tr(self.lang, "cancel"), command=win.destroy).pack(side="left", padx=8)

    def open_backups(self):
        win = tk.Toplevel(self); win.title(tr(self.lang, "backups_window")); win.geometry("760x430")
        backups = self.editor.list_backups(); lst = tk.Listbox(win); lst.pack(fill="both", expand=True, padx=14, pady=14)
        for path in backups: lst.insert("end", path.name)
        if not backups: lst.insert("end", tr(self.lang, "no_backups"))
        def restore():
            idx = lst.curselection()
            if not idx or not backups: return
            try: out = self.editor.restore_backup(backups[idx[0]])
            except SaveEditorError as exc: messagebox.showerror(tr(self.lang, "invalid"), str(exc), parent=win); return
            messagebox.showinfo(tr(self.lang, "restore"), tr(self.lang, "restore_done", path=out), parent=win)
        bottom = ttk.Frame(win); bottom.pack(pady=8)
        ttk.Button(bottom, text=tr(self.lang, "restore"), command=restore).pack(side="left", padx=6); ttk.Button(bottom, text=tr(self.lang, "cancel"), command=win.destroy).pack(side="left", padx=6)


if __name__ == "__main__": App().mainloop()
