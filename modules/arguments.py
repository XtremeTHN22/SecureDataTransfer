import argparse

from modules.directories import ProjectDirs
from modules.exceptions import DebugErrors
from modules.log import SameLogger

class Arguments:
    def __init__(self):
        # SameLogger initialization
        self.logging = SameLogger()
        self.logger = self.logging.getLogger("Arguments()")

        self.logger.debug("Initializing argumentparser class...")
        self.parser = argparse.ArgumentParser()

        self.logger.debug("Adding arguments...")
        log_opts = self.parser.add_argument_group("Logger options")
        log_opts.add_argument("--max-logs", type=int, help="Sets maximum number of logs (Default: -1)", default=-1)
        log_opts.add_argument("--log-level", type=str, help="Sets log level (Default: INFO)", default="INFO")

        server_opts = self.parser.add_argument_group("Server options")
        server_opts.add_argument("-s", "--server", action="store_true", help="Creates server (Default: False)", default=False)

        client_opts = self.parser.add_argument_group("Client options")
        client_opts.add_argument("-c", "--client", action="store_true", help="Creates client (Default: False)", default=False)

        general_opt = self.parser.add_argument_group("General options")
        server_opts.add_argument("-a", "--address", type=str, help="Sets server address (Default: Current IP)", default="")
        server_opts.add_argument("-p", "--port", type=int, help="Sets server port (Default: 8080)", default=8080)

        self.parser.add_argument("--traceback", action="store_true", help="Displays traceback (Default: False)", default=False)
        
        self.args = None
    def apply_changes(self):
        if self.args is None:
            self.logger.error("Arguments are not initialized!")
            raise DebugErrors.ArgumentsNotInitialized("Arguments.args is None")
            
        dirs = ProjectDirs("SecureDataTransfer")

        self.logger.info("Applying arguments/configuration...")

        # Applies configs
        self.logger.debug("Changing log level to %s", self.args.log_level)
        
        # Copying params and updating log level
        new_params = SameLogger.params.copy()
        new_params["log_level"] = self.args.log_level.upper()
        self.logging.set_params(new_params)

        self.logger.debug("Checking if log have reached the file limit...")
        self.logging.delete_logs(self.args.max_logs)

    def parse_args(self):
        self.args = self.parser.parse_args()
        return self.args
    
    def get_args(self):
        return self.args
    
    def patch_args_from_config(self, confs):
        self.logger.debug("Patching arguments from config...")
        for key, value in confs["arguments"].items():
            if key in self.args.__dict__:
                self.logger.debug(f"Setting args.{key} to {value}")
                setattr(self.args, key, value)