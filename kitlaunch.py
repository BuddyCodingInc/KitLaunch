#!/usr/bin/env python3
"""
KitLaunch - a cozy little app shelf, named for the kit fox (the small
desert fox with the enormous ears).

Keep your favourite programs and scripts on one shelf and launch them with
a click: Buddy, Den, your own Python scripts, or any program/shortcut on
your computer.

Only the Python standard library is used.

Start it with:  python kitlaunch.py      (or double-click start_kitlaunch.bat)
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import time
import tkinter as tk
import uuid
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

APP_NAME = "KitLaunch"
IS_WIN = sys.platform == "win32"
HERE = Path(__file__).resolve().parent
SETTINGS_FILE = Path.home() / ".kitlaunch_settings.json"

# ---------------------------------------------------------------- palette
# Same family as Buddy and Den, but sandy and pale for the kit fox.
CREAM = "#FFF6EA"
PAPER = "#FFFDF9"
CARAMEL = "#F2A65A"
CARAMEL_DARK = "#E08E3C"
COCOA = "#5C4033"
EYE = "#8A5A2B"
SOFT = "#B49A80"
FUR = "#E9C79A"
FUR_EDGE = "#C9A06C"
WHITE_FUR = "#FFFDF9"
NOSE = "#2B1B14"
ERR = "#B5483A"
OK = "#4F8A4B"
BUBBLE_EDGE = "#EBD3B8"
CARD_BORDER = "#EADFC8"

EXT_BADGE = {
    ".py": ("PY", "#3B6EA5"), ".pyw": ("PY", "#3B6EA5"),
    ".exe": ("EXE", "#6B6B6B"), ".lnk": ("GO", "#8B5A2B"),
    ".bat": ("BAT", "#A3762E"), ".cmd": ("CMD", "#A3762E"),
    ".txt": ("TXT", "#7FB069"), ".pdf": ("PDF", "#B5483A"),
    ".url": ("WEB", "#3B8EA5"),
}
DEFAULT_BADGE = ("APP", "#9C8574")


# ----------------------------------------------------------------- settings
def load_settings() -> dict:
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_settings(data: dict) -> None:
    try:
        SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


def default_entries() -> list:
    """Auto-add Buddy and Den if they live next to this file - no setup needed."""
    entries = []
    for name, fname, blurb in (("Buddy", "buddy.py", "your cozy coding companion"),
                               ("Den", "den.py", "a cozy code editor")):
        p = HERE / fname
        if p.is_file():
            entries.append({"id": str(uuid.uuid4()), "name": name, "path": str(p),
                            "args": "", "cwd": "", "console": False, "note": blurb})
    return entries


# ------------------------------------------------------------- launching
def _python_paths() -> tuple[str, str]:
    """(console python, windowed pythonw) next to the interpreter running us."""
    d = Path(sys.executable).parent
    console = d / "python.exe"
    gui = d / "pythonw.exe"
    return (str(console) if console.exists() else sys.executable,
            str(gui) if gui.exists() else sys.executable)


def launch(entry: dict) -> None:
    path = entry.get("path", "")
    if not path or not Path(path).exists():
        raise FileNotFoundError(f"I can't find:\n{path}")
    args = (entry.get("args") or "").strip()
    cwd = entry.get("cwd") or str(Path(path).parent)
    ext = Path(path).suffix.lower()
    arglist = shlex.split(args) if args else []

    if ext in (".py", ".pyw"):
        console_py, gui_py = _python_paths()
        exe = console_py if entry.get("console") else gui_py
        kwargs = {}
        if IS_WIN and entry.get("console"):
            kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
        subprocess.Popen([exe, path, *arglist], cwd=cwd, **kwargs)
        return

    if IS_WIN:
        if args:
            os.startfile(path, arguments=args, cwd=cwd)  # noqa: S606 (Windows only)
        else:
            os.startfile(path)
        return

    subprocess.Popen([path, *arglist], cwd=cwd)


# -------------------------------------------------------------- kit fox art
class KitFoxPanel:
    """The mascot: a kit fox, famous for ears bigger than its whole head."""

    SIZE = 160

    def __init__(self, parent: tk.Widget):
        self.frame = tk.Frame(parent, bg=CREAM, width=190)
        self.frame.pack_propagate(False)

        tk.Label(self.frame, text="Kit", font=("Georgia", 15, "bold italic"),
                 fg=COCOA, bg=CREAM).pack(pady=(10, 0))
        tk.Label(self.frame, text="your app shelf fox", font=("Georgia", 9, "italic"),
                 fg=SOFT, bg=CREAM).pack()

        self.canvas = tk.Canvas(self.frame, width=self.SIZE, height=self.SIZE, bg=CREAM, highlightthickness=0)
        self.canvas.pack(pady=(4, 6))

        bubble = tk.Frame(self.frame, bg="white", highlightbackground=BUBBLE_EDGE, highlightthickness=2)
        bubble.pack(fill="x", padx=12)
        self.said = tk.StringVar(value="Pick something from the shelf, or add something new!")
        tk.Label(bubble, textvariable=self.said, font=("Segoe UI", 9), fg=COCOA, bg="white",
                 wraplength=160, justify="left", anchor="nw", height=6, padx=8, pady=8).pack(fill="x")

        self.mood = "idle"
        self.draw()

    def say(self, text: str, mood: str = "idle") -> None:
        self.mood = mood
        self.said.set(text)
        self.draw()

    def draw(self) -> None:
        c = self.canvas
        c.delete("all")
        cx, cy = self.SIZE // 2, 92
        mood = self.mood

        # the enormous ears - a kit fox's signature feature
        for side in (-1, 1):
            bx, by = cx + side * 20, cy - 40
            tip = (bx + side * 20, by - 56)
            c.create_polygon(bx - side * 17, by + 10, bx + side * 20, by - 10, tip,
                              fill=FUR, outline=FUR_EDGE, width=2)
            inner_tip = (bx + side * 11, by - 32)
            c.create_polygon(bx - side * 8, by + 2, bx + side * 9, by - 8, inner_tip,
                              fill=WHITE_FUR, outline="")

        # head
        c.create_oval(cx - 48, cy - 38, cx + 48, cy + 42, fill=FUR, outline=FUR_EDGE, width=2)
        c.create_oval(cx - 30, cy + 2, cx + 30, cy + 38, fill=WHITE_FUR, outline="")

        # eyes
        for side in (-1, 1):
            ex, ey = cx + side * 18, cy - 2
            if mood == "happy":
                c.create_arc(ex - 7, ey - 5, ex + 7, ey + 9, start=0, extent=180, style=tk.ARC, outline=EYE, width=3)
            else:
                c.create_oval(ex - 5, ey - 6, ex + 5, ey + 6, fill=EYE, outline="")
                c.create_oval(ex - 3.5, ey - 4.5, ex - 0.5, ey - 1.5, fill="white", outline="")
                if mood == "worried":
                    if side < 0:
                        c.create_line(ex - 7, ey - 9, ex + 5, ey - 13, fill=EYE, width=2, capstyle=tk.ROUND)
                    else:
                        c.create_line(ex - 5, ey - 13, ex + 7, ey - 9, fill=EYE, width=2, capstyle=tk.ROUND)

        # nose + mouth
        c.create_polygon(cx - 5, cy + 7, cx + 5, cy + 7, cx, cy + 13, fill=NOSE, outline="")
        if mood == "happy":
            c.create_arc(cx - 8, cy + 11, cx + 8, cy + 26, start=180, extent=180, style=tk.CHORD,
                         fill="#E8808A", outline=EYE, width=2)
        elif mood == "worried":
            c.create_arc(cx - 7, cy + 16, cx + 7, cy + 25, start=0, extent=180, style=tk.ARC, outline=EYE, width=2)
        else:
            c.create_line(cx, cy + 13, cx, cy + 16, fill=EYE, width=2)


# ----------------------------------------------------------------- dialogs
class AppDialog:
    """Add or edit one shelf entry. Blocks until Save or Cancel."""

    def __init__(self, parent: tk.Tk, title: str, entry: dict | None = None):
        self.result: dict | None = None
        self.win = tk.Toplevel(parent)
        self.win.title(title)
        self.win.configure(bg=CREAM)
        self.win.resizable(False, False)
        self.win.transient(parent)
        self.win.grab_set()

        entry = entry or {}
        pad = {"padx": 8, "pady": 6}

        tk.Label(self.win, text="Name:", bg=CREAM, fg=COCOA).grid(row=0, column=0, sticky="e", **pad)
        self.name_e = tk.Entry(self.win, width=36)
        self.name_e.grid(row=0, column=1, columnspan=2, sticky="w", **pad)
        self.name_e.insert(0, entry.get("name", ""))

        tk.Label(self.win, text="Path:", bg=CREAM, fg=COCOA).grid(row=1, column=0, sticky="e", **pad)
        self.path_e = tk.Entry(self.win, width=36)
        self.path_e.grid(row=1, column=1, sticky="w", **pad)
        self.path_e.insert(0, entry.get("path", ""))
        tk.Button(self.win, text="Browse...", command=self.browse_path,
                 bg=CARAMEL, fg="white", relief="flat", bd=0).grid(row=1, column=2, sticky="w", **pad)

        tk.Label(self.win, text="Arguments:", bg=CREAM, fg=COCOA).grid(row=2, column=0, sticky="e", **pad)
        self.args_e = tk.Entry(self.win, width=36)
        self.args_e.grid(row=2, column=1, columnspan=2, sticky="w", **pad)
        self.args_e.insert(0, entry.get("args", ""))

        tk.Label(self.win, text="Start in:", bg=CREAM, fg=COCOA).grid(row=3, column=0, sticky="e", **pad)
        self.cwd_e = tk.Entry(self.win, width=36)
        self.cwd_e.grid(row=3, column=1, sticky="w", **pad)
        self.cwd_e.insert(0, entry.get("cwd", ""))
        tk.Button(self.win, text="Browse...", command=self.browse_cwd,
                 bg=CARAMEL, fg="white", relief="flat", bd=0).grid(row=3, column=2, sticky="w", **pad)

        self.console_v = tk.BooleanVar(value=entry.get("console", False))
        tk.Checkbutton(self.win, text="Open a console window (for scripts that print or ask questions)",
                       variable=self.console_v, bg=CREAM, fg=COCOA, activebackground=CREAM,
                       selectcolor="white").grid(row=4, column=0, columnspan=3, sticky="w", **pad)

        btns = tk.Frame(self.win, bg=CREAM)
        btns.grid(row=5, column=0, columnspan=3, pady=(4, 10))
        tk.Button(btns, text="Save", command=self.on_save, bg=CARAMEL, fg="white",
                 relief="flat", bd=0, padx=14, pady=4).pack(side="left", padx=6)
        tk.Button(btns, text="Cancel", command=self.win.destroy, bg=SOFT, fg="white",
                 relief="flat", bd=0, padx=14, pady=4).pack(side="left", padx=6)

        self.win.bind("<Return>", lambda _e: self.on_save())
        self.win.bind("<Escape>", lambda _e: self.win.destroy())
        self.name_e.focus_set()
        self.win.wait_window()

    def browse_path(self) -> None:
        chosen = filedialog.askopenfilename(
            parent=self.win, title="Which program or script?",
            filetypes=[("Programs and scripts", "*.py *.pyw *.exe *.bat *.cmd *.lnk"), ("All files", "*.*")])
        if chosen:
            self.path_e.delete(0, "end")
            self.path_e.insert(0, chosen)
            if not self.name_e.get().strip():
                self.name_e.insert(0, Path(chosen).stem)

    def browse_cwd(self) -> None:
        chosen = filedialog.askdirectory(parent=self.win, title="Start in which folder?")
        if chosen:
            self.cwd_e.delete(0, "end")
            self.cwd_e.insert(0, chosen)

    def on_save(self) -> None:
        name = self.name_e.get().strip()
        path = self.path_e.get().strip()
        if not name or not path:
            messagebox.showwarning(APP_NAME, "A name and a path are both needed.", parent=self.win)
            return
        self.result = {
            "name": name, "path": path, "args": self.args_e.get().strip(),
            "cwd": self.cwd_e.get().strip(), "console": self.console_v.get(), "note": "",
        }
        self.win.destroy()


class ScanDialog:
    """Find .py files in a folder and let the person pick which to add."""

    def __init__(self, parent: tk.Tk, folder: Path):
        self.result: list[Path] = []
        self.folder = folder
        self.win = tk.Toplevel(parent)
        self.win.title("Scan for Python files")
        self.win.configure(bg=CREAM)
        self.win.resizable(False, False)
        self.win.transient(parent)
        self.win.grab_set()

        self.folder_v = tk.StringVar(value=str(folder))
        top = tk.Frame(self.win, bg=CREAM)
        top.pack(fill="x", padx=10, pady=(10, 4))
        tk.Label(top, textvariable=self.folder_v, bg=CREAM, fg=COCOA, anchor="w").pack(side="left", fill="x", expand=True)
        tk.Button(top, text="Change folder...", command=self.change_folder,
                 bg=CARAMEL, fg="white", relief="flat", bd=0).pack(side="right")

        self.list_frame = tk.Frame(self.win, bg=PAPER, highlightbackground=CARD_BORDER, highlightthickness=1)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=4)
        self.vars: dict[Path, tk.BooleanVar] = {}
        self.rescan()

        btns = tk.Frame(self.win, bg=CREAM)
        btns.pack(pady=(4, 10))
        tk.Button(btns, text="Add selected", command=self.on_add, bg=CARAMEL, fg="white",
                 relief="flat", bd=0, padx=14, pady=4).pack(side="left", padx=6)
        tk.Button(btns, text="Cancel", command=self.win.destroy, bg=SOFT, fg="white",
                 relief="flat", bd=0, padx=14, pady=4).pack(side="left", padx=6)
        self.win.wait_window()

    def rescan(self) -> None:
        for child in self.list_frame.winfo_children():
            child.destroy()
        self.vars.clear()
        try:
            found = sorted(self.folder.glob("*.py"))
        except OSError:
            found = []
        if not found:
            tk.Label(self.list_frame, text="No .py files found here.", bg=PAPER, fg=SOFT).pack(padx=10, pady=10)
            return
        for p in found:
            v = tk.BooleanVar(value=False)
            self.vars[p] = v
            tk.Checkbutton(self.list_frame, text=p.name, variable=v, bg=PAPER, fg=COCOA,
                          activebackground=PAPER, selectcolor="white", anchor="w"
                          ).pack(fill="x", padx=10, pady=2)

    def change_folder(self) -> None:
        chosen = filedialog.askdirectory(parent=self.win, title="Scan which folder?")
        if chosen:
            self.folder = Path(chosen)
            self.folder_v.set(chosen)
            self.rescan()

    def on_add(self) -> None:
        self.result = [p for p, v in self.vars.items() if v.get()]
        self.win.destroy()


# ------------------------------------------------------------------ the app
class KitLaunchApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title(APP_NAME)
        root.configure(bg=CREAM)
        root.geometry("760x560")
        root.minsize(480, 360)

        self.settings = load_settings()
        self.entries: list[dict] = self.settings.get("apps")
        if self.entries is None:
            self.entries = default_entries()
            self.save()

        self.build_ui()
        self.refresh_list()
        self.root.after(300, self.greet)

    def greet(self) -> None:
        hour = time.localtime().tm_hour
        if hour < 12:
            self.fox.say("Morning! What shall we launch first?", "happy")
        elif hour < 18:
            self.fox.say("Hi! Pick something from the shelf.", "happy")
        else:
            self.fox.say("Evening coding session? I'm ready when you are.", "happy")

    # ------------------------------------------------------------- building
    def build_ui(self) -> None:
        top = tk.Frame(self.root, bg=CARAMEL_DARK)
        top.pack(side="top", fill="x")
        tk.Button(top, text="+ Add app", command=self.add_app, bg=CARAMEL, fg="white",
                 activebackground=CARAMEL_DARK, activeforeground="white", relief="flat", bd=0,
                 font=("Segoe UI", 10, "bold"), cursor="hand2", padx=10, pady=5
                 ).pack(side="left", padx=(8, 4), pady=6)
        tk.Button(top, text="Scan for Python files", command=self.scan_folder, bg=CARAMEL, fg="white",
                 activebackground=CARAMEL_DARK, activeforeground="white", relief="flat", bd=0,
                 font=("Segoe UI", 10, "bold"), cursor="hand2", padx=10, pady=5
                 ).pack(side="left", padx=4, pady=6)

        self.search_v = tk.StringVar()
        self.search_v.trace_add("write", lambda *_a: self.refresh_list())
        search = tk.Entry(top, textvariable=self.search_v, width=24)
        search.pack(side="right", padx=8, pady=6)
        tk.Label(top, text="Search:", bg=CARAMEL_DARK, fg="white").pack(side="right", pady=6)

        main = tk.Frame(self.root, bg=CREAM)
        main.pack(side="top", fill="both", expand=True)

        self.fox = KitFoxPanel(main)
        self.fox.frame.pack(side="right", fill="y")

        shelf_outer = tk.Frame(main, bg=CREAM)
        shelf_outer.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(shelf_outer, bg=CREAM, highlightthickness=0)
        vsb = ttk.Scrollbar(shelf_outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.inner = tk.Frame(self.canvas, bg=CREAM)
        self.inner_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.inner_window, width=e.width))

        for widget in (self.canvas, self.inner):
            widget.bind("<Enter>", lambda _e: self.canvas.bind_all("<MouseWheel>", self._wheel))
            widget.bind("<Leave>", lambda _e: self.canvas.unbind_all("<MouseWheel>"))

        self.status_v = tk.StringVar(value="Ready")
        bar = tk.Frame(self.root, bg=CARAMEL_DARK)
        bar.pack(side="bottom", fill="x")
        tk.Label(bar, textvariable=self.status_v, bg=CARAMEL_DARK, fg="white", anchor="w",
                font=("Segoe UI", 9)).pack(side="left", padx=10, pady=3)

    def _wheel(self, event) -> None:
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ----------------------------------------------------------------- data
    def save(self) -> None:
        self.settings["apps"] = self.entries
        save_settings(self.settings)

    def matching(self) -> list[dict]:
        q = self.search_v.get().strip().lower()
        if not q:
            return self.entries
        return [e for e in self.entries if q in e["name"].lower() or q in e.get("path", "").lower()]

    # ---------------------------------------------------------------- shelf
    def refresh_list(self) -> None:
        for child in self.inner.winfo_children():
            child.destroy()

        shown = self.matching()
        if not shown:
            msg = "Nothing here yet - add your first app!" if not self.entries else "No apps match that search."
            tk.Label(self.inner, text=msg, bg=CREAM, fg=SOFT, font=("Segoe UI", 10, "italic")
                    ).pack(pady=30)
            return

        for entry in shown:
            self.build_row(entry)

    def build_row(self, entry: dict) -> None:
        row = tk.Frame(self.inner, bg=PAPER, highlightbackground=CARD_BORDER, highlightthickness=1)
        row.pack(fill="x", pady=4, padx=2)

        ext = Path(entry.get("path", "")).suffix.lower()
        label, color = EXT_BADGE.get(ext, DEFAULT_BADGE)
        badge = tk.Canvas(row, width=42, height=42, bg=PAPER, highlightthickness=0)
        badge.pack(side="left", padx=10, pady=8)
        badge.create_rectangle(2, 2, 40, 40, fill=color, outline="")
        badge.create_text(21, 21, text=label, fill="white", font=("Segoe UI", 8, "bold"))

        text_col = tk.Frame(row, bg=PAPER)
        text_col.pack(side="left", fill="x", expand=True, pady=6)
        tk.Label(text_col, text=entry["name"], bg=PAPER, fg=COCOA, font=("Segoe UI", 11, "bold"),
                anchor="w").pack(fill="x")
        sub = entry.get("note") or entry.get("path", "")
        tk.Label(text_col, text=sub, bg=PAPER, fg=SOFT, font=("Segoe UI", 8), anchor="w"
                ).pack(fill="x")

        btns = tk.Frame(row, bg=PAPER)
        btns.pack(side="right", padx=8)
        self.small_button(btns, "Launch", lambda e=entry: self.do_launch(e), CARAMEL)
        self.small_button(btns, "Edit", lambda e=entry: self.do_edit(e), SOFT)
        self.small_button(btns, "Remove", lambda e=entry: self.do_remove(e), ERR)

        for widget in (row, text_col, badge):
            widget.bind("<Double-Button-1>", lambda _e, e=entry: self.do_launch(e))

    @staticmethod
    def small_button(parent, text, command, color) -> None:
        tk.Button(parent, text=text, command=command, bg=color, fg="white", relief="flat", bd=0,
                 font=("Segoe UI", 9), cursor="hand2", padx=8, pady=3).pack(side="left", padx=3)

    # -------------------------------------------------------------- actions
    def add_app(self) -> None:
        dlg = AppDialog(self.root, "Add an app")
        if dlg.result:
            dlg.result["id"] = str(uuid.uuid4())
            self.entries.append(dlg.result)
            self.save()
            self.refresh_list()
            self.fox.say(f"Got it! '{dlg.result['name']}' is on the shelf.", "happy")

    def do_edit(self, entry: dict) -> None:
        dlg = AppDialog(self.root, "Edit app", entry)
        if dlg.result:
            dlg.result["id"] = entry["id"]
            idx = self.entries.index(entry)
            self.entries[idx] = dlg.result
            self.save()
            self.refresh_list()
            self.fox.say(f"Updated '{dlg.result['name']}'.", "happy")

    def do_remove(self, entry: dict) -> None:
        if messagebox.askyesno(APP_NAME, f"Remove '{entry['name']}' from the shelf?"):
            self.entries.remove(entry)
            self.save()
            self.refresh_list()
            self.fox.say("Tidied that off the shelf.", "idle")

    def do_launch(self, entry: dict) -> None:
        try:
            launch(entry)
        except Exception as e:
            self.fox.say(f"Hmm, I couldn't start '{entry['name']}'. {e}", "worried")
            self.status_v.set(f"Couldn't launch {entry['name']}.")
            return
        self.fox.say(f"Zoom! Off goes '{entry['name']}'.", "happy")
        self.status_v.set(f"Launched {entry['name']}.")

    def scan_folder(self) -> None:
        dlg = ScanDialog(self.root, HERE)
        if dlg.result:
            added = 0
            existing_paths = {e["path"] for e in self.entries}
            for p in dlg.result:
                if str(p) in existing_paths:
                    continue
                self.entries.append({"id": str(uuid.uuid4()), "name": p.stem, "path": str(p),
                                     "args": "", "cwd": "", "console": True, "note": ""})
                added += 1
            self.save()
            self.refresh_list()
            if added:
                self.fox.say(f"Added {added} script{'s' if added != 1 else ''} to the shelf!", "happy")
            else:
                self.fox.say("Those were already on the shelf.", "idle")


def main() -> None:
    root = tk.Tk()
    KitLaunchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
