import glob, os, datetime, logging
from pystyle import Colorate, Colors

def init_log(name, max_logs, log_dir="logs") -> str | None:
    if max_logs != -1:
        logs = glob.glob(os.path.join(log_dir,"*.log"))
        if len(logs) >= max_logs:
            try:
                for x in logs:
                    os.remove(x)
            except Exception as e:
                print("Removal of logs has failed!")
                print(e)
    log_name = os.path.join(log_dir, datetime.datetime.today().strftime(f"%d-%m-%Y_%H-%M-%S_{name}.log"))
    logging.basicConfig(filename=log_name,
                filemode='w',
                format='%(asctime)s:%(msecs)d %(name)s %(levelname)s %(message)s',
                datefmt='%H:%M',
                level=logging.DEBUG)
    
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(name)s][%(levelname)s] %(message)s')
    console.setFormatter(formatter)
    console.setFormatter
    logging.getLogger('').addHandler(console)
    return [
        getattr(logging.getLoggerClass().root.handlers[0], 'baseFilename', "Null"),
        console,
    ]