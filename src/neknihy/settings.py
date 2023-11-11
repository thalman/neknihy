import os.path
import configparser
import sys

try:
    import platformdirs
except ModuleNotFoundError:
    try:
        from gi.repository import GLib
    except ModuleNotFoundError:
        pass


class Settings():
    def __init__(self, config=None):
        self._config_file = config if config else self._file_name()
        self._data = {}
        self._changed = False

    def _file_name(self):
        try:
            return os.path.join(GLib.get_user_config_dir(), "neknihy.conf")
        except NameError:
            pass
        try:
            return os.path.join(platformdirs.user_config_dir(), "neknihy.conf")
        except NameError:
            return os.path.join(os.path.expanduser('~'), ".neknihy.conf")

    def _set_attr(self, attr, val):
        if attr in self._data:
            if self._data[attr] != val:
                self._data[attr] = val
                self._changed = True
        else:
            self._data[attr] = val
            self._changed = True

    def _get_attr(self, attr):
        return self._data[attr] if attr in self._data else None

    @property
    def email(self):
        return self._get_attr("email")

    @email.setter
    def email(self, value):
        return self._set_attr("email", value)

    @property
    def password(self):
        return self._get_attr("password")

    @password.setter
    def password(self, value):
        return self._set_attr("password", value)

    @property
    def workdir(self):
        return self._get_attr("workdir")

    @workdir.setter
    def workdir(self, value):
        return self._set_attr("workdir", value)

    @property
    def readerdir(self):
        return self._get_attr("readerdir")

    @readerdir.setter
    def readerdir(self, value):
        return self._set_attr("readerdir", value)

    @property
    def convert(self):
        return self._get_attr("convert")

    @convert.setter
    def convert(self, value):
        return self._set_attr("convert", value)

    @property
    def convertor(self):
        return self._get_attr("convertor")

    @convertor.setter
    def convertor(self, value):
        return self._set_attr("convertor", value)

    def load(self):
        config = configparser.ConfigParser()
        config.read(self._config_file)
        self.email = config.get("settings", "email", fallback="")
        self.password = config.get("settings", "password", fallback="")
        self.workdir = config.get("settings", "workdir", fallback="")
        self.readerdir = config.get("settings", "readerdir", fallback="")
        self.convert = config.get("settings", "convert", fallback="0")
        self.convertor = config.get("settings", "convertor", fallback="ebook-convert")
        if self.convertor == "":
            if sys.platform.startswith("win"):
                self.convertor = "ebook-convert.exe"
            else:
                self.convertor = "ebook-convert"
        self._changed = False

    def save(self):
        if not self._changed:
            return
        config = configparser.ConfigParser()
        config["settings"] = self._data
        with open(self._config_file, "w") as cf:
            config.write(cf)
        self._changed = False

    def update(self, email=None, password=None, workdir=None,
               readerdir=None, convert=None, convertor=None):
        if email is not None:
            self.email = email
        if password is not None:
            self.password = password
        if workdir is not None:
            self.workdir = workdir
        if readerdir is not None:
            self.readerdir = readerdir
        if convert is not None:
            self.convert = convert
        if convertor is not None:
            self.convertor = convertor
        self.save()

    def configured(self):
        return not (
            self.email == "" or
            self.password == "" or
            self.workdir == ""
        )
