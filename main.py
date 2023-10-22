from modules.exceptions import ExceptionHandler
from modules.log import SameLogger
from modules.directories import ProjectDirs
from modules.arguments import Arguments
from modules.server import Server
from modules.client import Client

import os
import sys
import json
import argparse
import threading

# Exception handler
exc = ExceptionHandler()
sys.excepthook = exc.global_handler

DEFAULT_CONFIGS = {
    "arguments": {
        "args_priority": "config",

        "max_logs":-1,
        "log_level":"INFO",
    }
}

# Project directories (/home/USER/.local/share, /home/USER/.config/)
dirs = ProjectDirs("SecureDataTransfer")

# SameLogger, un intento de que todos los loggers del proyecto tengan el mismo nivel
logging = SameLogger("Main", DEFAULT_CONFIGS["arguments"], dirs.log_dir)
console = logging.init_log()[1]

logger = logging.getLogger("Main")

# Arguments initialization
args_obj = Arguments()
# Global parameters update
logging.set_params(args_obj.parse_args().__dict__)

logger.info('Reading configuration...')

# Config read
conf_path = os.path.join(dirs.config_dir, "config.json")
if os.path.exists(conf_path) is False:
    logger.warning("Configuration file not found!")
    logger.info("Creating configuration file...")

    file = os.path.join(dirs.config_dir, 'config.json')

    with open(file, 'w') as f:
        json.dump(DEFAULT_CONFIGS, f, indent=4)

    logger.info("Config file created!")
else:
    with open(conf_path) as f:
        confs = json.load(f)

# If priority is config then patch arguments with config values
if confs["arguments"]["priority"] == "config":
    args_obj.patch_args_from_config(confs)
    # Global parameters update
    logging.set_params(confs["arguments"])

# Apply changes to objects
args_obj.apply_changes()
args = args_obj.get_args()
logger.info("%s", args)

if args.server:
    server = Server(dirs.cert_dir, args)
elif args.client:
    client = Client(dirs.cert_dir, args)
else:
    logger.warning("No operation has specified")
    logger.info("You can define an operation in the configuration or by passing an argument")