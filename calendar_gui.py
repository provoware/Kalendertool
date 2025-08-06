"""Einfache GUI zur Verwaltung von Gruppen-Kalendern."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime, timedelta
import calendar

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
    group_entry = tk.Entry(root, textvariable=group_var)
    group_entry.grid(row=0, column=1)

    listbox = tk.Listbox(root, width=40)
    listbox.grid(row=1, column=0, columnspan=2, pady=5)

    tk.Label(root, text="Titel").grid(row=2, column=0)
    title_var = tk.StringVar()
    title_entry = tk.Entry(root, textvariable=title_var)
    title_entry.grid(row=2, column=1)

    tk.Label(root, text="Datum (JJJJ-MM-TT)").grid(row=3, column=0)
    date_var = tk.StringVar()
    date_entry = tk.Entry(root, textvariable=date_var)
    date_entry.grid(row=3, column=1)

    tk.Label(root, text="Alarm (Minuten)").grid(row=4, column=0)
    alarm_var = tk.StringVar()
    alarm_entry = tk.Entry(root, textvariable=alarm_var)
    alarm_entry.grid(row=4, column=1)

    def create_tooltip(widget: tk.Widget, text: str) -> None:
        """Zeige Text beim Überfahren des Widgets an."""
        tip: tk.Toplevel | None = None

        def on_enter(event: tk.Event) -> None:  # pragma: no cover - GUI
            nonlocal tip
            tip = tk.Toplevel(widget)
            tip.wm_overrideredirect(True)
            x = event.x_root + 10
            y = event.y_root + 10
            tip.wm_geometry(f"+{x}+{y}")
            tk.Label(
                tip,
                text=text,
                background="#ffffe0",
                relief=tk.SOLID,
                borderwidth=1,
            ).pack()

        def on_leave(_: tk.Event) -> None:  # pragma: no cover - GUI
            nonlocal tip
            if tip:
                tip.destroy()
                tip = None

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def refresh() -> None:
        if not group_var.get().strip():
            messagebox.showerror("Fehler", "Gruppe angeben")
            return
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
        if not group_var.get().strip():
            messagebox.showerror("Fehler", "Gruppe angeben")
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
        add_event(title_var.get(), date_var.get(), alarm, group_var.get())
        refresh()

    def sync_cb() -> None:
        if not group_var.get().strip():
            messagebox.showerror("Fehler", "Gruppe angeben")
            return
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
        if not group_var.get().strip():
            messagebox.showerror("Fehler", "Gruppe angeben")
            return
        remove_event(sel[0], group_var.get())
        refresh()

    def edit_cb() -> None:
        sel = listbox.curselection()
        if not sel:
            messagebox.showerror("Fehler", "Bitte Termin auswählen")
            return
        if not group_var.get().strip():
            messagebox.showerror("Fehler", "Gruppe angeben")
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

    def month_view_cb() -> None:
        if not group_var.get().strip():
            messagebox.showerror("Fehler", "Gruppe angeben")
            return
        current = datetime.now().replace(day=1)
        win = tk.Toplevel(root)

        def draw() -> None:
            for widget in win.grid_slaves():
                widget.destroy()
            weeks = calendar.monthcalendar(current.year, current.month)
            groups, _ = _load_groups()
            events = groups.get(group_var.get(), [])
            days = {
                int(ev["date"][8:10])
                for ev in events
                if ev["date"].startswith(f"{current.year:04d}-{current.month:02d}")
            }
            win.title(f"{calendar.month_name[current.month]} {current.year}")
            for col, name in enumerate(["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]):
                tk.Label(win, text=name, font=("Arial", 10, "bold")).grid(
                    row=0, column=col
                )
            for r, week in enumerate(weeks, start=1):
                for c, day in enumerate(week):
                    txt = "" if day == 0 else str(day)
                    lbl = tk.Label(win, text=txt)
                    if day in days:
                        lbl.configure(background="lightblue")
                    lbl.grid(row=r, column=c, padx=2, pady=2)
            btn_prev = tk.Button(win, text="<", command=prev_month)
            btn_prev.grid(row=len(weeks) + 1, column=0, columnspan=3, sticky="w")
            btn_next = tk.Button(win, text=">", command=next_month)
            btn_next.grid(row=len(weeks) + 1, column=4, columnspan=3, sticky="e")
            create_tooltip(btn_prev, "Vorherigen Monat anzeigen")
            create_tooltip(btn_next, "Nächsten Monat anzeigen")

        def prev_month() -> None:
            nonlocal current
            current = (current - timedelta(days=1)).replace(day=1)
            draw()

        def next_month() -> None:
            nonlocal current
            current = (current + timedelta(days=31)).replace(day=1)
            draw()

        draw()

    listbox.bind("<<ListboxSelect>>", on_select)
    btn_refresh = tk.Button(root, text="Aktualisieren", command=refresh)
    btn_refresh.grid(row=5, column=0)
    btn_save = tk.Button(root, text="Speichern", command=add_cb)
    btn_save.grid(row=5, column=1)
    btn_edit = tk.Button(root, text="Ändern", command=edit_cb)
    btn_edit.grid(row=6, column=0)
    btn_delete = tk.Button(root, text="Löschen", command=delete_cb)
    btn_delete.grid(row=6, column=1)
    btn_sync = tk.Button(root, text="Synchronisieren", command=sync_cb)
    btn_sync.grid(row=7, column=0, columnspan=2)
    btn_month = tk.Button(root, text="Monat", command=month_view_cb)
    btn_month.grid(row=8, column=0, columnspan=2)

    create_tooltip(group_entry, "Gruppe für den Termin (z. B. familie)")
    create_tooltip(title_entry, "Titel des Termins")
    create_tooltip(date_entry, "Datum im Format JJJJ-MM-TT")
    create_tooltip(alarm_entry, "Alarm in Minuten (leer für keinen Alarm)")
    create_tooltip(btn_refresh, "Liste neu laden")
    create_tooltip(btn_save, "Neuen Termin speichern")
    create_tooltip(btn_edit, "Markierten Termin ändern")
    create_tooltip(btn_delete, "Markierten Termin löschen")
    create_tooltip(btn_sync, "Termine mit CalDAV-Server abgleichen")
    create_tooltip(btn_month, "Monatsübersicht anzeigen")

    refresh()
    root.mainloop()
    close()
