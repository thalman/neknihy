import os.path
import configparser
from gi.repository import GLib


class Settings():
    def _file_name(self):
        return os.path.join(GLib.get_user_config_dir(), "neknihy.conf")

    def load(self):
        config = configparser.ConfigParser();
        config.read(self._file_name())
        self.email = config.get("settings", "email", fallback="")
        self.password = config.get("settings", "password", fallback="")
        self.workdir = config.get("settings", "workdir", fallback="")

    def save(self):
        config = configparser.ConfigParser();
        config["settings"] = {
            "email": self.email,
            "password": self.password,
            "workdir": self.workdir,
        }
        with open(self._file_name(), "w") as cf:
            config.write(cf)

    def update(self, email, password, workdir):
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
        if change:
            self.save()

    def configured(self):
        return not (
            self.email == "" or
            self.password == "" or
            self.workdir == ""
        )
