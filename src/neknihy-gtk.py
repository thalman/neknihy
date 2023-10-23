#!/usr/bin/env python

import gi
import threading
import subprocess
import sys
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

from neknihy.app import App


class Neknihy():
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("neknihy.glade")
        self.builder.connect_signals(self)

        self.app = App()
        self.app.updateStatus()
        self.setup()
        self.background_task = None
        self.error = None

        self._window = self.builder.get_object("mainWindow")
        self._window.show_all()

    def setup(self):
        self._email = self.builder.get_object("settingsEmail")
        self._email.set_text(self.app.settings.email)
        self._password = self.builder.get_object("settingsPassword")
        self._password.set_text(self.app.settings.password)
        self._workdir = self.builder.get_object("settingsWorkDir")
        self._workdir.set_current_folder(self.app.settings.workdir)
        self._bookTreeView = self.builder.get_object("bookTreeView")

        self._toolbarButtons = []
        for btn in ["progressButton", "refreshButton", "returnButton", "downloadButton"]:
            self._toolbarButtons.append(self.builder.get_object(btn))

        self._store = Gtk.ListStore(int, str, str, str, str)
        for i, column_title in enumerate(
            ["Autor", "Kniha", "Výpůjčka do", "Stav"]
        ):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i+1)
            column.set_resizable(True)
            self._bookTreeView.append_column(column)
        self._bookTreeView.set_model(self._store)
        self.updateBookList()
        # self._model.append([1, "Alois Jirasek", "Temno", "2023-11-19", "ok")

    def sensitiveToolbar(self, sensitive):
        self._toolbarButtons[0].set_sensitive(not sensitive)
        for i in range(1, len(self._toolbarButtons)):
            self._toolbarButtons[i].set_sensitive(sensitive)

    def updateBookList(self):
        self._store.clear()
        for book in self.app.books:
            self._store.append(
                [
                    book["palm_id"],
                    book["author_full_name"] if book["author_full_name"] else "??",
                    book["title"],
                    book["end_time"].split("T")[0] if "end_time" in book else "",
                    book["neknihy"]["status"] if "neknihy" in book else ""
                ])

    def run(self):
        Gtk.main()

    def onDestroy(self, *args):
        self.app.updateSettings(
            self._email.get_text(),
            self._password.get_text(),
            self._workdir.get_current_folder()
        )
        Gtk.main_quit()

    def refreshBooks(self):
        try:
            self.app.refreshRents()
            self.error = None
        except Exception as e:
            self.error = str(e)
        GLib.idle_add(self.refreshBooksDone)

    def refreshBooksDone(self):
        self.sensitiveToolbar(True)
        self.background_task = None
        self.updateBookList()
        if self.error:
            dialog = Gtk.MessageDialog(
                transient_for=self._window,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Nastala chyba",
            )
            dialog.format_secondary_text(
                self.error
            )
            dialog.run()
            dialog.destroy()
            self.error = None

    def onRefreshBooks(self, button):
        self.sensitiveToolbar(False)
        self.background_task = threading.Thread(target=self.refreshBooks)
        self.background_task.start()

    def downloadBooks(self):
        try:
            self.app.downloadBooks()
        except Exception as e:
            self.error = str(e)
        GLib.idle_add(self.refreshBooksDone)

    def onDownloadBooks(self, button):
        self.sensitiveToolbar(False)
        self.background_task = threading.Thread(target=self.downloadBooks)
        self.background_task.start()

    def onReturnBooks(self, button):
        self.app.returnBooks()
        self.updateBookList()

    def onShowBooks(self, button):
        wd = self._workdir.get_current_folder()
        if sys.platform == "win32":
            os.startfile(wd)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, wd])

    def onTabSwitch(self, *notused):
        self.app.updateSettings(
            self._email.get_text(),
            self._password.get_text(),
            self._workdir.get_current_folder()
        )

    def onCancelJob(self, button):
        pass


if __name__ == '__main__':
    Neknihy().run()
