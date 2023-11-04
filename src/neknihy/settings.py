import os.path
import configparser

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

    def _file_name(self):
        try:
            return os.path.join(GLib.get_user_config_dir(), "neknihy.conf")
        except NameError:
            pass
        try:
            return os.path.join(platformdirs.user_config_dir(), "neknihy.conf")
        except NameError:
            return os.path.join(os.path.expanduser('~'), ".neknihy.conf")

    def load(self):
        config = configparser.ConfigParser()
        config.read(self._config_file)
        self.email = config.get("settings", "email", fallback="")
        self.password = config.get("settings", "password", fallback="")
        self.workdir = config.get("settings", "workdir", fallback="")
        self.readerdir = config.get("settings", "readerdir", fallback="")

    def save(self):
        config = configparser.ConfigParser()
        config["settings"] = {
            "email": self.email if type(self.email) is str else "",
            "password": self.password if type(self.password) is str else "",
            "workdir": self.workdir if type(self.workdir) is str else "",
            "readerdir": self.readerdir if type(self.readerdir) is str else "",
        }
        with open(self._config_file, "w") as cf:
            config.write(cf)

    def update(self, email, password, workdir, readerdir):
        change = False
        if self.email != email:
            self.email = email
            change = True
        if self.password != password:
            self.password = password
            change = True
        if self.workdir != workdir:
            self.workdir = workdir
            change = True
        if self.readerdir != readerdir:
            self.readerdir = readerdir
            change = True
        if change:
            self.save()

    def configured(self):
        return not (
            self.email == "" or
            self.password == "" or
            self.workdir == ""
        )
