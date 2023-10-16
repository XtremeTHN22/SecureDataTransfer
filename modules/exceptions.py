import logging
import sys
import os
import traceback

class DebugErrors:
    class ArgumentsNotInitialized(Exception):
        pass

class ExceptionHandler():
    def __init__(self, cleanup_function=None, logger=logging.getLogger("ExceptionHandler")):
        self.logger = logger
        self.cleanup_func = cleanup_function

    def local_handler(self, func, exit=True):
        def decorator(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.logger.error("Fatal error ocurred! More information in the log file or passing the '--log-level debug' argument")
                exc = sys.exc_info()
                
                tb = traceback.extract_tb(exc[2]) # Obtiene la última línea de la traza
                _, lineno, _, line = tb[-1] # Obtiene los detalles de la última línea

                self.logger.critical("Error ocurred in line {}".format(lineno))
                try:
                    self.logger.info(f"Error Type: {type(e).__name__}")
                    self.logger.info(f"Error Line: {line}")
                    self.logger.info(f"Error Message: {' '.join(e.args)}")
                    if "--traceback" in sys.argv:
                        self.logger.info(f"Traceback:\n{''.join(traceback.format_tb(exc[2]))}")
                except:
                    self.logger.info("Cannot display Exception info, changing method of display (traceback)...")
                    self.logger.exception("Exception below: ", exc_info=True)
                self.logger.info("Report the error to the github page")
                if exit:
                    sys.exit(1)
        return decorator
    
    def global_handler(self, exc_type, value, traceback_obj):
        self.logger.error("Fatal error ocurred! More information in the log file or passing the '--log-level debug' argument")
        
        tb = traceback.extract_tb(traceback_obj) # Obtiene la última línea de la traza
        _, lineno, _, line = tb[-1] # Obtiene los detalles de la última línea
        self.logger.critical("Error ocurred in line {}".format(lineno))
        try:
            self.logger.debug("Error ocurred in file '%s'", os.path.split(tb[-1].filename)[1])
            self.logger.debug(f"Error Type: {exc_type}")
            self.logger.debug(f"Error Line: {line}")
            self.logger.debug(f"Error Message: {value}")
            if "--traceback" in sys.argv:
                self.logger.debug(f"Traceback:\n{''.join(traceback.format_tb(traceback_obj))}")
        except:
            self.logger.info("Cannot display Exception info, changing method of display (traceback)...")
            self.logger.exception("Exception below: ", exc_info=True)
        self.logger.info("Report the error to the github page")
        self.logger.info("If requiered, you can pass the --traceback argument to see the traceback")
        if self.cleanup_func:
            self.logger.info("Cleaning up objects...")
            self.cleanup_func()
        sys.exit(1)

