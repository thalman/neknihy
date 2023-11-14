#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, WARNING, INFO
from tkinter.constants import DISABLED, NORMAL
import tkinter.filedialog

import threading
import subprocess
import sys
import os
import argparse

from neknihy.app import App


class Neknihy():
    def __init__(self, configfile):
        self.createGUI()

        self.app = App(configfile)
        self.app.updateStatus()
        self._background_task = None
        self._error = None
        self._message = None
        self._tooltip_job = None
        self._tooltip_window = None
        self._email.set(self.app.settings.email)
        self._password.set(self.app.settings.password)
        self._workdir.set(self.app.settings.workdir)
        self._readerdir.set(self.app.settings.readerdir)
        self._convert.set(self.app.settings.convert)
        self._convertor.set(self.app.settings.convertor)
        self.updateBookList()
        self.syncButtonMonitor()

    def _resourcesFolder(self):
        for resources in [
                os.path.join(os.path.abspath(os.path.dirname(__file__)), 'resources'),
                'resources',
                ]:
            if os.path.exists(resources):
                return resources
        raise RuntimeError("Resource directory not found")

    def _scheduleTooltip(self, event, tip):
        self._tooltip_job = self._window.after(1000, lambda: self._showTooltip(tip))

    def _showTooltip(self, tip):
        self._tooltip_window = tk.Toplevel(self._window)
        tooltip_label = tk.Label(self._tooltip_window,
                                 text=tip)
        tooltip_label.pack()
        self._tooltip_window.overrideredirect(True)
        x = self._window.winfo_pointerx() + 15
        y = self._window.winfo_pointery() + 15
        self._tooltip_window.geometry("+{}+{}".format(x, y))
        self._tooltip_job = None

    def _hideTooltip(self, event):
        if self._tooltip_job:
            self._window.after_cancel(self._tooltip_job)
            self._tooltip_job = None
        if self._tooltip_window:
            self._tooltip_window.destroy()
            self._tooltip_window = None

    def addTooltip(self, button, tip):
        button.bind("<Enter>", lambda x: self._scheduleTooltip(x, tip))
        button.bind("<Leave>", self._hideTooltip)

    def createGUI(self):
        resources = self._resourcesFolder()
        self._window = tk.Tk()
        self._window.title("Neknihy")
        self._window.geometry("800x600")
        self._window.minsize(600, 400)
        self._icon = tk.PhotoImage(file=os.path.join(resources, 'neknihy.png'))
        self._window.iconphoto(True, self._icon)
        nb = ttk.Notebook(self._window)

        p1 = ttk.Frame(nb)
        p2 = ttk.Frame(nb)

        nb.add(p1, text="Knihy")
        nb.add(p2, text="Nastavení")

        nb.pack(expand=1, fill="both")
        nb.bind("<<NotebookTabChanged>>", self.onTabSwitch)

        # application page
        toolbar = ttk.Frame(p1)
        toolbar.pack(fill=tk.X)

        self._img_cancel = tk.PhotoImage(file=os.path.join(resources, "cancel.png"))
        self._img_refresh = tk.PhotoImage(file=os.path.join(resources, "refresh.png"))
        self._img_download = tk.PhotoImage(file=os.path.join(resources, "download.png"))
        self._img_return = tk.PhotoImage(file=os.path.join(resources, "return.png"))
        self._img_open = tk.PhotoImage(file=os.path.join(resources, "open.png"))
        self._img_to_reader = tk.PhotoImage(file=os.path.join(resources, "toreader.png"))
        self._img_open_small = self._img_open.subsample(2, 2)

        self._toolbarButtons = []
        button = ttk.Button(toolbar, image=self._img_cancel)
        button.pack(side="right", padx=5, pady=5)
        button['state'] = DISABLED
        self._toolbarButtons.append(button)

        button = ttk.Button(toolbar, image=self._img_refresh, command=self.onRefreshBooks)
        button.pack(side="left", padx=5, pady=5)
        self.addTooltip(button, "Načíst nové výpůjčky")
        self._toolbarButtons.append(button)

        button = ttk.Button(toolbar, image=self._img_download, command=self.onDownloadBooks)
        button.pack(side="left", padx=5, pady=5)
        self.addTooltip(button, "Stáhnout nově zapůjčené knihy")
        self._toolbarButtons.append(button)

        button = ttk.Button(toolbar, image=self._img_return, command=self.onReturnBooks)
        button.pack(side="left", padx=5, pady=5)
        self.addTooltip(button, "Smazat knihy, u kterých\nvypršela výpůjční doba")
        self._toolbarButtons.append(button)

        self._sync_button = ttk.Button(toolbar,
                                       image=self._img_to_reader,
                                       command=self.onSyncReader)
        self._sync_button.pack(side="left", padx=5, pady=5)
        self.addTooltip(self._sync_button, "Synchronizovat výpůjčky s čtečkou")

        button = ttk.Button(toolbar, image=self._img_open, command=self.onShowBooks)
        button.pack(side="left", padx=5, pady=5)
        self.addTooltip(button, "Otevřít složku s knihami")

        columns = ("book", "rent", "status")
        tree = ttk.Treeview(p1, columns=columns, show='headings')
        tree.pack(fill=tk.BOTH, expand=True)
        tree.heading("book", text='Kniha')
        tree.column("book", minwidth=0, width=200)
        tree.heading("rent", text='Výpůjčka do')
        tree.column("rent", minwidth=0, width=100)
        tree.heading("status", text='Stav')
        tree.column("status", minwidth=0, width=400)
        self._tree = tree

        # settings page
        p2.columnconfigure(0, weight=1)
        p2.columnconfigure(1, weight=100)
        p2.columnconfigure(2, weight=1)
        label = ttk.Label(p2, text="Email")
        label.grid(column=0, row=0, sticky=tk.EW, padx=5, pady=5)
        label = ttk.Label(p2, text="Heslo")
        label.grid(column=0, row=1, sticky=tk.EW, padx=5, pady=5)
        label = ttk.Label(p2, text="Pracovní složka")
        label.grid(column=0, row=2, sticky=tk.EW, padx=5, pady=5)
        label = ttk.Label(p2, text="Složka ve čtečce")
        label.grid(column=0, row=3, sticky=tk.EW, padx=5, pady=5)

        self._email = tk.StringVar()
        entry = ttk.Entry(p2, textvariable=self._email)
        entry.grid(column=1, row=0, columnspan=2, sticky=tk.EW, padx=5, pady=10)
        self._password = tk.StringVar()
        entry = ttk.Entry(p2, textvariable=self._password, show="*")
        entry.grid(column=1, row=1, columnspan=2, sticky=tk.EW, padx=5, pady=10)
        self._workdir = tk.StringVar()
        entry = ttk.Entry(p2, textvariable=self._workdir)
        entry.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5)

        button = ttk.Button(p2, image=self._img_open_small, command=self.onSelectFolder)
        button.grid(column=2, row=2, padx=5, pady=0)

        self._readerdir = tk.StringVar()
        entry = ttk.Entry(p2, textvariable=self._readerdir)
        entry.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5)

        button = ttk.Button(p2, image=self._img_open_small, command=self.onSelectReaderFolder)
        button.grid(column=2, row=3, padx=5, pady=0)

        # mobi convertor
        self._convert = tk.StringVar()
        checkbox = ttk.Checkbutton(p2,
                                   text='Převádět na .mobi (pro Kindle)',
                                   variable=self._convert)
        checkbox.grid(column=1, row=4, columnspan=2, sticky=tk.EW, padx=5, pady=0)
        label = ttk.Label(p2, text="Cesta k ebook-convert")
        label.grid(column=0, row=5, sticky=tk.EW, padx=5, pady=5)
        self._convertor = tk.StringVar()
        entry = ttk.Entry(p2, textvariable=self._convertor)
        entry.grid(column=1, row=5, sticky=tk.EW, padx=5, pady=10)
        button = ttk.Button(p2, image=self._img_open_small, command=self.onSelectConvertor)
        button.grid(column=2, row=5, padx=5, pady=0)

    def onSelectFolder(self):
        dir = self._workdir.get()
        name = tk.filedialog.askdirectory(
            title="Vyberte složku pro knihy",
            initialdir=dir,
            mustexist=True)
        if name != "":
            self._workdir.set(name)

    def onSelectReaderFolder(self):
        dir = self._readerdir.get()
        name = tk.filedialog.askdirectory(
            title="Vyberte složku pro knihy",
            initialdir=dir,
            mustexist=False)
        if name != "":
            self._readerdir.set(name)

    def onSelectConvertor(self):
        dir = self._convertor.get()
        file = tk.filedialog.askopenfile(
            title="Aplikace pro konverzi knih",
            initialfile=dir)
        if file:
            self._convertor.set(file.name)

    def sensitiveSyncButton(self, sensitive):
        if self._background_task is not None:
            self._sync_button['state'] = DISABLED
            return
        if not os.path.exists(self.app.settings.readerdir):
            self._sync_button['state'] = DISABLED
            return
        current_state = self._sync_button['state']
        desired_state = NORMAL if sensitive else DISABLED
        if str(current_state) != str(desired_state):
            self._sync_button['state'] = desired_state

    def sensitiveToolbar(self, sensitive):
        self._toolbarButtons[0]['state'] = DISABLED if sensitive else NORMAL
        for i in range(1, len(self._toolbarButtons)):
            self._toolbarButtons[i]['state'] = NORMAL if sensitive else DISABLED
        self.sensitiveSyncButton(sensitive)

    def statusToText(self, status):
        if status == "new":
            return "Nová výpůjčka"
        if status == "pending":
            return "Připravuje se ke stažení"
        if status == "ok":
            return "Výpůjčka je připravená a stažená"
        if status == "expired":
            return "K vrácení"
        return "??"

    def updateBookList(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        for book in self.app.books:
            self._tree.insert(
                "",
                tk.END,
                values=(
                    book["title"],
                    book["end_time"].split("T")[0] if "end_time" in book else "",
                    self.statusToText(book["neknihy"]["status"] if "neknihy" in book else "")
                ))

    def run(self):
        self._window.mainloop()

    def refreshBooks(self):
        try:
            self.app.refreshRents()
            self._error = None
        except Exception as e:
            self._error = str(e)

    def syncButtonMonitor(self):
        self.sensitiveSyncButton(True)
        self._window.after(1000, self.syncButtonMonitor)

    def backgroundTaskMonitor(self):
        if self._background_task is None:
            self.sensitiveToolbar(True)
            return
        if self._background_task.is_alive():
            self._window.after(100, self.backgroundTaskMonitor)
        else:
            self._background_task = None
            self.sensitiveToolbar(True)
            self.updateBookList()
            if self._error:
                showinfo(
                    title='Chyba',
                    icon=WARNING,
                    message=self._error)
            self._error = None
            if self._message:
                showinfo(
                    title='Info',
                    icon=INFO,
                    message=self._message)
            self._message = None

    def onRefreshBooks(self):
        self.sensitiveToolbar(False)
        self._background_task = threading.Thread(target=self.refreshBooks)
        self._background_task.start()
        self.backgroundTaskMonitor()

    def downloadBooks(self):
        try:
            self.app.downloadBooks()
            self._error = None
        except Exception as e:
            self._error = str(e)

    def onDownloadBooks(self):
        self.sensitiveToolbar(False)
        self._background_task = threading.Thread(target=self.downloadBooks)
        self._background_task.start()
        self.backgroundTaskMonitor()

    def onReturnBooks(self):
        self.app.returnBooks()
        self.updateBookList()

    def syncReader(self):
        try:
            self._message = None
            self._error = None
            result = self.app.syncReader()
            if result is not None:
                self._message = (
                    "Přidáno/odstraněno/zůstává ve čtečce: %i/%i/%i" % (
                        len(result["added"]),
                        len(result["removed"]),
                        result["total"])
                )
        except Exception as e:
            self._error = str(e)

    def onSyncReader(self):
        self.sensitiveToolbar(False)
        self._background_task = threading.Thread(target=self.syncReader)
        self._background_task.start()
        self.backgroundTaskMonitor()

    def onShowBooks(self):
        wd = self._workdir.get()
        if sys.platform.startswith("win"):
            os.startfile(wd)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, wd])

    def onTabSwitch(self, data):
        self.app.updateSettings(
            self._email.get(),
            self._password.get(),
            self._workdir.get(),
            self._readerdir.get(),
            self._convert.get(),
            self._convertor.get()
        )

    def onCancelJob(self, button):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Aplikace neknihy spravuje výpůjčky z knihovny.')
    parser.add_argument('configfile',
                        nargs='?',
                        help='Konfigurační soubor')
    args = parser.parse_args()
    Neknihy(args.configfile).run()
