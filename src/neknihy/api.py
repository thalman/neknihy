import requests
import json
import urllib
import os.path
from http.client import HTTPConnection


class API():
    def __init__(self, debug=False):
        self._url = "https://prodapp.palmknihy.cz"
        self._login = None
        self._rents = None
        if debug:
            HTTPConnection.debuglevel = 1

    def login(self, email, password):
        if self._login:
            return
        data = {"email": email, "password": password}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        response = requests.post(self._url + "/users/login/",
                                 data=json.dumps(data),
                                 headers=headers)
        if response.status_code >= 300:
            raise RuntimeError("Nepodařilo se přihlásit, zkontrolujte jméno a heslo\n(%s)" %
                               response.text)
        self._login = json.loads(response.text)

    def logout(self):
        self._login = None
        self._rents = None

    def refreshListOfRentedBooks(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + self._login["token"]
        }
        response = requests.get(self._url + "/rents/?refresh", headers=headers)
        if response.status_code >= 300:
            raise RuntimeError("Nepodařilo se načíst seznam zapůjčených knih\n(%s)" %
                               response.text)
        self._rents = json.loads(response.text)
        return self._rents["results"]

    def getListOfRentedBooks(self):
        if self._rents:
            return self._rents["results"]
        return self.refreshListOfRentedBooks()

    def getRentDownloadInfo(self, book):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + self._login["token"]
        }
        url = (self._url + "/v3/books/file/" + str(book["palm_id"]) + "/" +
               str(book["variant_palm_id"]) + "/")
        response = requests.get(url, headers=headers)
        if response.status_code >= 300:
            raise RuntimeError("Nepodařilo se získat odkaz ke stažení výpujčky\n(%s)" %
                               response.text)
        return json.loads(response.text)

    def downloadBook(self, workdir, book):
        downloadInfo = self.getRentDownloadInfo(book)
        if not downloadInfo["status"]:
            book["neknihy"] = {"status": "pending", "filename": ""}
            return
        info = downloadInfo["file"]
        params = urllib.parse.parse_qs(info.split('?', 1)[1])

        ext = ".unknown"
        if book["item_type"] == "ebook":
            ext = ".epub"

        filename = params["filename"][0] + ext
        fullpath = os.path.join(workdir, filename)
        url = params["url"][0]
        response = requests.get(url, stream=True)
        with open(fullpath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=10240):
                if chunk:
                    f.write(chunk)
        if response.status_code >= 300:
            raise RuntimeError("Nepodařilo se stáhnout knihu %s\n(%s)" %
                               (filename, response.text))
        book["neknihy"] = {"status": "ok", "filename": filename}
