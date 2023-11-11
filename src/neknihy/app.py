from neknihy.api import API
from neknihy.settings import Settings

import os.path
import json
import re
import subprocess
from datetime import datetime, timezone
from shutil import copy


class App():
    def __init__(self, config=None):
        self.api = API()
        self.settings = Settings(config)
        self.settings.load()
        self.books = []
        self.loadBooks()

    def updateSettings(self, email, password, workdir, readerdir, convert, convertor):
        self.settings.update(email, password, workdir, readerdir, convert, convertor)
        self.api.logout()
        self.loadBooks()

    def saveBooks(self):
        if not self.settings.configured():
            return
        file = os.path.join(self.settings.workdir, '.data')
        with open(file, 'w') as f:
            json.dump(self.books, f, indent=2)

    def loadBooks(self):
        try:
            if not self.settings.configured():
                return
            file = os.path.join(self.settings.workdir, '.data')
            with open(file) as f:
                self.books = json.load(f)
            self.updateStatus()
        except Exception:
            self.books = []

    def refreshRents(self):
        if not self.settings.configured():
            return
        self.api.login(self.settings.email, self.settings.password)
        rents = self.api.getListOfRentedBooks()
        for rent in rents:
            if self.bookIndexByPalmId(rent["palm_id"]) is None:
                rent["neknihy"] = {"status": "new", "filename": ""}
                self.books.append(rent)
        self.saveBooks()
        self.updateStatus()

    def updateStatus(self):
        changed = False
        for book in self.books:
            try:
                if "end_time" in book:
                    time = datetime.fromisoformat(book["end_time"])
                    if time < datetime.now(timezone.utc) and book["neknihy"]["status"] != "expired":
                        book["neknihy"]["status"] = "expired"
                        changed = True
            except Exception:
                pass
        if changed:
            self.saveBooks()

    def bookIndexByPalmId(self, id):
        for i in range(len(self.books)):
            if self.books[i]["palm_id"] == id:
                return i
        return None

    def book(self, index):
        if index >= len(self.books):
            return None
        return self.books[index]

    def bookFile(self, index):
        filename = self.books[index]["neknihy"]["filename"]
        if filename == "":
            return None
        return os.path.join(self.settings.workdir, filename)

    def bookFileExists(self, index):
        path = self.bookFile(index)
        if path is None:
            return False
        return os.path.exists(path)

    def removeBookFile(self, index):
        if self.bookFileExists(index):
            os.remove(self.bookFile(index))

    def bookDownloaded(self, index):
        book = self.book(index)
        if book is None:
            return False
        if "neknihy" not in book:
            return False
        if book["neknihy"]["status"] in ["ok", "expired"]:
            return self.bookFileExists(index)
        return False

    def downloadBook(self, index):
        self.api.downloadBook(self.settings.workdir, self.books[index])

    def downloadBooks(self):
        if not self.settings.configured():
            return
        self.api.login(self.settings.email, self.settings.password)
        for i in range(len(self.books)):
            if not self.bookDownloaded(i):
                self.downloadBook(i)
        self.saveBooks()
        self.updateStatus()

    def returnBooks(self):
        books = []
        for i in range(len(self.books)):
            if self.books[i]["neknihy"]["status"] == "expired":
                self.removeBookFile(i)
            else:
                books.append(self.books[i])
        self.books = books
        self.saveBooks()

    def bookByFilename(self, filename):
        filename = re.sub(".mobi$", ".epub", filename)
        for i in range(len(self.books)):
            if filename == self.books[i]["neknihy"]["filename"]:
                return i
        return None

    def syncReader(self):
        if self.settings.readerdir == "":
            return None
        if not os.path.exists(self.settings.readerdir):
            return None
        result = {"added": [], "removed": [], "total": 0}
        for i in range(len(self.books)):
            if self.books[i]["neknihy"]["status"] == "ok":
                src = self.bookFile(i)
                filename = self.books[i]["neknihy"]["filename"]
                if self.settings.convert == "1":
                    filename = re.sub(".epub$", ".mobi", filename)
                dst = os.path.join(
                    self.settings.readerdir,
                    filename
                )
                if os.path.exists(src) and not os.path.exists(dst):
                    if self.settings.convert == "1":
                        subprocess.run([self.settings.convertor, src, dst])
                    else:
                        copy(src, dst)
                    result["added"].append(self.books[i]["neknihy"]["filename"])
                result["total"] += 1
        for fn in os.listdir(self.settings.readerdir):
            if fn.lower().endswith("-palmknihy.epub") or fn.lower().endswith("-palmknihy.mobi"):
                if self.bookByFilename(fn) is None:
                    os.remove(os.path.join(self.settings.readerdir, fn))
                    result["removed"].append(fn)
        return result
