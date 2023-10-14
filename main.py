import os
import json
import argparse
import threading
import logging

from modules.directories import ProjectDirs
from modules.log import init_log, delete_logs

confs = {
    "arguments": {
        "args_priority": "config",

        "max_logs":-1,
        "log_level":"INFO",
    }
}

dirs = ProjectDirs("SecureDataTransfer")

console = init_log("SecureDataTransfer", dirs.log_dir)[1]
logging.debug("Getting main logger...")

logger = logging.getLogger("SDT")
logger.info("Parsing arguments...")

parser = argparse.ArgumentParser()
log_opts = parser.add_argument_group("Logger options")
log_opts.add_argument("--max-logs", type=int, help="Sets maximum number of logs (Default: -1)", default=-1)
log_opts.add_argument("--log-level", type=str, help="Sets log level (Default: INFO)", default="INFO")

server_opts = parser.add_argument_group("Server options")
client_opts = parser.add_argument_group("Client options")

args = parser.parse_args()

if args.log_level is not None:
    console.setLevel(args.log_level.upper())

logger.info("Configuration values have higher priority than arguments")
logger.info("You can disable this in the config file by setting the config 'args_priority' to 'console'")
logger.info("Reading configuration...")

conf_path = os.path.join(dirs.config_dir, "config.json")
if os.path.exists(conf_path) is False:
    logger.warning("Configuration file not found!")
    logger.info("Creating configuration file...")

    logger.debug(f"Config data: {confs}")
    file = os.path.join(dirs.config_dir, 'config.json')

    logger.debug(f"Config file path: {file}")

    with open(file, 'w') as f:
        json.dump(confs, f, indent=4)

    logger.info("Config file created!")
else:
    with open(conf_path) as f:
        confs = json.load(f)

args = parser.parse_args()
if confs["arguments"]["args_priority"] == "config":
    for key, value in confs["arguments"].items():
        if key in args.__dict__:
            logger.debug(f"Setting {key} to {value}")
            setattr(args, key, value)

logger.info("Applying arguments/configuration...")

# Applies configs
logger.debug("Changing log level to %s", args.log_level)
console.setLevel(args.log_level.upper())
logger.debug("Checking if log have reached the file limit...")
delete_logs(args.max_logs, dirs.log_dir)

