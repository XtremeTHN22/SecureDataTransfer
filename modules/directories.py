import os, sys, logging

class ProjectDirs:
    def __mkdirs(self):
        os.makedirs(self.share_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
    def __init__(self, proj_dir):
        logger = logging.getLogger("ProjectDirs()")
        if sys.platform == "win32":
            self.home = os.getenv("USERPROFILE")
            self.appdata = os.getenv("APPDATA")
            self.local = os.getenv("LOCALAPPDATA")

            self.share_dir = os.path.join(self.local, proj_dir)
            self.cert_dir = os.path.join(self.share_dir, "certs")
            self.log_dir = os.path.join(self.share_dir, "logs")
            self.config_dir = os.path.join(self.appdata, proj_dir, "config")

        elif sys.platform == "linux":
            self.home = os.getenv("HOME")
            self.share_dir = os.path.join(self.home, ".local", "share", proj_dir)
            self.cert_dir = os.path.join(self.share_dir, "certs")
            self.log_dir = os.path.join(self.share_dir, "logs")
            self.config_dir = os.path.join(self.home, ".config", proj_dir)

        elif sys.platform == "darwin":
            logger.error("MacOS is not implemented yet")
        
        self.__mkdirs()