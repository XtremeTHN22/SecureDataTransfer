import glob, os, datetime, logging
from colorama import Fore, Style
from modules.exceptions import DebugErrors

# FancyLog formatter (colors in log messages)
class FancyLog(logging.Formatter):
    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: Fore.BLUE + Style.BRIGHT + self.fmt + Style.RESET_ALL,
            logging.INFO: Fore.GREEN + self.fmt + Style.RESET_ALL,
            logging.WARNING: Fore.LIGHTRED_EX + self.fmt + Style.RESET_ALL,
            logging.ERROR: Fore.RED + self.fmt + Style.RESET_ALL,
            logging.CRITICAL: Fore.RED + Style.BRIGHT + self.fmt + Style.RESET_ALL,
        }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class SameLogger:
    """
        Logger with same parameters for all instances.
    """
    params: dict = None
    log_dir: str = None
    log_file: str = None
    def __init__(self, name="SecureDataTransfer", parameters=None, log_dir="logs"):
        """
        Initializes a new instance of the class.

        Args:
            name (str): The name of the instance.
            max_logs (int): The maximum number of logs.
            parameters (dict, optional): The parameters of the instance. Defaults to None.
            log_dir (str, optional): The directory where logs are stored. Defaults to "logs".
        """
        self.name = name
        self.file_name = None
        self.current_logger_name = None

        if SameLogger.log_dir is None:
            SameLogger.log_dir = log_dir

        if parameters is not None or {}:
            if SameLogger.params is None:
                SameLogger.params = parameters

    def delete_logs(self, max_logs=None):
        """
        Delete all logs in the log directory.

        This function deletes all logs in the log directory specified by `self.log_dir`.
        It checks the number of logs in the directory and compares it with the maximum
        number of logs allowed (`max_logs`). If the number of logs exceeds the
        maximum limit, the function will delete the excess logs.

        Parameters:
            max_logs (int): The maximum number of logs.

        Returns:
            None
        """
        if max_logs is None:
            if SameLogger.params is not None:
                max_logs = SameLogger.params["max_logs"]
            else:
                raise DebugErrors.SameLog.ParamsNotDefined("delete_logs()")

        log_obj = SameLogger()
        logger = log_obj.getLogger("SameLogger.delete_logs()")
        if max_logs != -1:
            logs = glob.glob(os.path.join(self.log_dir,"*.log"))
            logs.pop(logs.index(SameLogger.log_file))
            if len(logs) > max_logs:
                logger.debug("Log limit reached!. Deleting logs...")
                logger.info("%d", len(logs))
                try:
                    for x in logs:
                        os.remove(x)
                except Exception as e:
                    print("Removal of logs has failed!")
                    print(e)
            logger.debug("There were %d logs", len(logs))
    
    # Update parameters globally (not functional yet)
    def set_params(self, params):
        SameLogger.params = params
        self.params = params
        self._update_logger()

    def _update_logger(self):
        self.current_logger.setLevel(SameLogger.params["log_level"])

    def getLogger(self, name=None):
        """
        Get a logger with the specified name.
        
        Args:
            name (str): The name of the logger (optional).
        
        Returns:
            logging.Logger: The logger object.
        """
        logger = logging.getLogger(name)
        self.current_logger = logger

        if SameLogger.params is not None:
            self._update_logger()
        return logger
        
    def init_log(self) -> list[str, logging.Handler]:
        """
        Initializes the log for the class.

        Returns:
            list[str, logging.Handler]: The log file name and a console handler.
        """
        log_name = os.path.join(self.log_dir, datetime.datetime.today().strftime(f"%d-%m-%Y_%H-%M-%S_{self.name}.log"))
        logging.basicConfig(filename=log_name,
                    filemode='w',
                    format='%(asctime)s:%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M',
                    level=logging.DEBUG)
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = FancyLog('[ %(name)s ][%(levelname)s] %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        
        SameLogger.log_file = getattr(logging.getLoggerClass().root.handlers[0], 'baseFilename', "Null")
        return [
            SameLogger.log_file,
            console,
        ]