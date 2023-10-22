#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, WARNING
from tkinter.constants import DISABLED, NORMAL
import tkinter.filedialog

import threading
import subprocess
import sys

from pprint import pprint

from neknihy.app import App


class Neknihy():
    def __init__(self):
        self.createGUI()

        self.app = App()
        self.app.updateStatus()
        self.background_task = None
        self.error = None
        self._email.set(self.app.settings.email)
        self._password.set(self.app.settings.password)
        self._workdir.set(self.app.settings.workdir)
        self.updateBookList()

    def createGUI(self):
        self._window = tk.Tk()
        self._window.title("Neknihy")
        self._window.geometry("800x600")
        self._window.minsize(600,400)
        # self._window.iconbitmap("./neknihy.ico")

        # https://stackoverflow.com/questions/284234/notebook-widget-in-tkinter
        nb = ttk.Notebook(self._window)

        p1 = ttk.Frame(nb)
        p2 = ttk.Frame(nb)

        nb.add(p1, text="Knihy")
        nb.add(p2, text="Nastavení")

        nb.pack(expand=1, fill="both")
        nb.bind("<<NotebookTabChanged>>", self.onTabSwitch)

        toolbar = ttk.Frame(p1)
        toolbar.pack(fill=tk.X)

        self._img_cancel = tk.PhotoImage(file="./resources/cancel.png")
        self._img_refresh = tk.PhotoImage(file="./resources/refresh.png")
        self._img_download = tk.PhotoImage(file="./resources/download.png")
        self._img_return = tk.PhotoImage(file="./resources/return.png")
        self._img_open = tk.PhotoImage(file="./resources/open.png")
        self._img_open_small = self._img_open.subsample(2,2)

        self._toolbarButtons = []
        button = ttk.Button(toolbar, image=self._img_cancel)
        button.pack(side="right", padx=5, pady=5)
        button['state'] = DISABLED
        self._toolbarButtons.append(button)
        button = ttk.Button(toolbar, image=self._img_refresh, command=self.onRefreshBooks)
        button.pack(side="left", padx=5, pady=5)
        self._toolbarButtons.append(button)
        button = ttk.Button(toolbar, image=self._img_download, command=self.onDownloadBooks)
        button.pack(side="left", padx=5, pady=5)
        self._toolbarButtons.append(button)
        button = ttk.Button(toolbar, image=self._img_return, command=self.onReturnBooks)
        button.pack(side="left", padx=5, pady=5)
        self._toolbarButtons.append(button)
        button = ttk.Button(toolbar, image=self._img_open, command=self.onShowBooks)
        button.pack(side="left", padx=5, pady=5)
        self._toolbarButtons.append(button)

        # https://www.pythontutorial.net/tkinter/tkinter-treeview/
        columns = ("author", "book", "rent", "status")
        tree = ttk.Treeview(p1, columns=columns, show='headings')
        tree.pack(fill=tk.BOTH, expand=True)
        tree.heading("author", text='Autor')
        tree.heading("book", text='Kniha')
        tree.heading("rent", text='Výpůjčka do')
        tree.heading("status", text='Stav')
        self._tree = tree

        # settings
        p2.columnconfigure(0, weight=1)
        p2.columnconfigure(1, weight=100)
        p2.columnconfigure(2, weight=1)
        label = ttk.Label(p2, text="Email")
        label.grid(column=0, row=0, sticky=tk.EW, padx=5, pady=5)
        label = ttk.Label(p2, text="Heslo")
        label.grid(column=0, row=1, sticky=tk.EW, padx=5, pady=5)
        label = ttk.Label(p2, text="Pracovní složka")
        label.grid(column=0, row=2, sticky=tk.EW, padx=5, pady=5)

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

    def onSelectFolder(self):
        dir = self._workdir.get()
        name = tk.filedialog.askdirectory(title="Vyberte složku pro knihy", initialdir=dir, mustexist=True)
        if name != "":
            self._workdir.set(name)
    def sensitiveToolbar(self, sensitive):
        self._toolbarButtons[0]['state'] = DISABLED if sensitive else NORMAL
        for i in range(1, len(self._toolbarButtons)):
            self._toolbarButtons[i]['state'] = NORMAL if sensitive else DISABLED

    def updateBookList(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        for book in self.app.books:
            self._tree.insert(
                "",
                tk.END,
                values=(
                    book["author_full_name"] if book["author_full_name"] else "??",
                    book["title"],
                    book["end_time"].split("T")[0] if "end_time" in book else "",
                    book["neknihy"]["status"] if "neknihy" in book else ""
                ))

    def run(self):
        self._window.mainloop()

    def refreshBooks(self):
        try:
            self.app.refreshRents()
            self.error = None
        except Exception as e:
            self.error = str(e)

    def backgroundTaskMonitor(self):
        if self.background_task is None:
            self.sensitiveToolbar(True)
            return
        if self.background_task.is_alive():
            self._window.after(100, self.backgroundTaskMonitor)
        else:
            self.sensitiveToolbar(True)
            self.updateBookList()
            self.background_task = None
            if self.error:
                showinfo(
                    title='Chyba',
                    icon=WARNING,
                    message=self.error)

            self.error = None

    def onRefreshBooks(self):
        self.sensitiveToolbar(False)
        self.background_task = threading.Thread(target=self.refreshBooks)
        self.background_task.start()
        self.backgroundTaskMonitor()

    def downloadBooks(self):
        try:
            self.app.downloadBooks()
            self.error = None
        except Exception as e:
            self.error = str(e)

    def onDownloadBooks(self):
        self.sensitiveToolbar(False)
        self.background_task = threading.Thread(target=self.downloadBooks)
        self.background_task.start()
        self.backgroundTaskMonitor()

    def onReturnBooks(self):
        self.app.returnBooks()
        self.updateBookList()

    def onShowBooks(self):
        wd = self._workdir.get()
        if sys.platform == "win32":
            os.startfile(wd)
        else:
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, wd])

    def onTabSwitch(self, data):
        self.app.updateSettings(
            self._email.get(),
            self._password.get(),
            self._workdir.get()
        )

    def onCancelJob(self, button):
        pass

if __name__ == '__main__':
    Neknihy().run()
