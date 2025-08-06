"""Einfache GUI zur Verwaltung von Gruppen-Kalendern."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

from start_cli import (
    add_event,
    edit_event,
    _load_groups,
    sync_caldav,
    remove_event,
    close,
)


def run() -> None:
    """Starte die GUI."""

    root = tk.Tk()
    root.title("Kalender")

    group_var = tk.StringVar(value="default")
    tk.Label(root, text="Gruppe").grid(row=0, column=0)
    tk.Entry(root, textvariable=group_var).grid(row=0, column=1)

    listbox = tk.Listbox(root, width=40)
    listbox.grid(row=1, column=0, columnspan=2, pady=5)

    tk.Label(root, text="Titel").grid(row=2, column=0)
    title_var = tk.StringVar()
    tk.Entry(root, textvariable=title_var).grid(row=2, column=1)

    tk.Label(root, text="Datum (JJJJ-MM-TT)").grid(row=3, column=0)
    date_var = tk.StringVar()
    tk.Entry(root, textvariable=date_var).grid(row=3, column=1)

    tk.Label(root, text="Alarm (Minuten)").grid(row=4, column=0)
    alarm_var = tk.StringVar()
    tk.Entry(root, textvariable=alarm_var).grid(row=4, column=1)

    def refresh() -> None:
        groups, _ = _load_groups()
        events = groups.get(group_var.get(), [])
        listbox.delete(0, tk.END)
        for ev in events:
            txt = f"{ev['date']}: {ev['title']}"
            if ev.get("alarm"):
                txt += f" (Alarm {ev['alarm']} min)"
            listbox.insert(tk.END, txt)

    def on_select(event: tk.Event) -> None:  # pragma: no cover - GUI-Interaktion
        sel = listbox.curselection()
        if not sel:
            return
        groups, _ = _load_groups()
        ev = groups.get(group_var.get(), [])[sel[0]]
        title_var.set(ev["title"])
        date_var.set(ev["date"][:10])
        alarm_var.set(str(ev.get("alarm", "")))

    def add_cb() -> None:
        if not title_var.get().strip():
            messagebox.showerror("Fehler", "Titel angeben")
            return
        try:
            datetime.fromisoformat(date_var.get())
        except ValueError:
            messagebox.showerror("Fehler", "Datum im Format JJJJ-MM-TT angeben")
            return
        try:
            alarm = int(alarm_var.get()) if alarm_var.get() else None
            if alarm is not None and alarm < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Fehler", "Alarm muss eine positive Zahl sein")
            return
        add_event(title_var.get(), date_var.get(), alarm, group_var.get())
        refresh()

    def sync_cb() -> None:
        url = simpledialog.askstring("CalDAV", "URL")
        if not url:
            return
        user = simpledialog.askstring("CalDAV", "Benutzername")
        if user is None:
            return
        password = simpledialog.askstring("CalDAV", "Passwort", show="*")
        if password is None:
            return
        ok = sync_caldav(url, user, password, group_var.get())
        messagebox.showinfo(
            "CalDAV",
            "Synchronisation erfolgreich" if ok else "Synchronisation fehlgeschlagen",
        )

    def delete_cb() -> None:
        sel = listbox.curselection()
        if not sel:
            messagebox.showerror("Fehler", "Bitte Termin auswählen")
            return
        remove_event(sel[0], group_var.get())
        refresh()

    def edit_cb() -> None:
        sel = listbox.curselection()
        if not sel:
            messagebox.showerror("Fehler", "Bitte Termin auswählen")
            return
        if not title_var.get().strip():
            messagebox.showerror("Fehler", "Titel angeben")
            return
        try:
            datetime.fromisoformat(date_var.get())
        except ValueError:
            messagebox.showerror("Fehler", "Datum im Format JJJJ-MM-TT angeben")
            return
        try:
            alarm = int(alarm_var.get()) if alarm_var.get() else None
            if alarm is not None and alarm < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Fehler", "Alarm muss eine positive Zahl sein")
            return
        edit_event(sel[0], title_var.get(), date_var.get(), alarm, group_var.get())
        refresh()

    listbox.bind("<<ListboxSelect>>", on_select)
    tk.Button(root, text="Aktualisieren", command=refresh).grid(row=5, column=0)
    tk.Button(root, text="Speichern", command=add_cb).grid(row=5, column=1)
    tk.Button(root, text="Ändern", command=edit_cb).grid(row=6, column=0)
    tk.Button(root, text="Löschen", command=delete_cb).grid(row=6, column=1)
    tk.Button(root, text="Synchronisieren", command=sync_cb).grid(
        row=7, column=0, columnspan=2
    )

    refresh()
    root.mainloop()
    close()
