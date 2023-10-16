import os
import sys
import json
import argparse
import threading
import logging

from modules.exceptions import ExceptionHandler
from modules.log import init_log, delete_logs
from modules.directories import ProjectDirs
from modules.arguments import Arguments
from modules.server import Server
from modules.client import Client

exc = ExceptionHandler()
# sys.excepthook = exc.global_handler

confs = {
    "arguments": {
        "priority": "config",

        "max_logs":-1,
        "log_level":"INFO",
        
        "address":"localhost",
        "port":8080
    }
}

dirs = ProjectDirs("SecureDataTransfer")

console = init_log("SecureDataTransfer", dirs.log_dir)[1]
logging.debug("Getting main logger...")

logger = logging.getLogger("Main()")

args_obj = Arguments(console)

logger.info("Configuration values have higher priority than arguments")
logger.info("You can disable this in the config file by setting the config 'args_priority' to 'console'")
logger.info("Reading configuration...")

console.setLevel(args_obj.parse_args().log_level)

conf_path = os.path.join(dirs.config_dir, "config.json")
if os.path.exists(conf_path) is False:
    logger.warning("Configuration file not found!")
    logger.info("Creating a new configuration file...")

    file = os.path.join(dirs.config_dir, 'config.json')

    logger.debug(f"Config file path: {file}")

    with open(file, 'w') as f:
        json.dump(confs, f, indent=4)

    logger.info("Config file created!")
else:
    with open(conf_path) as f:
        confs = json.load(f)


if confs["arguments"]["priority"] == "config":
    args_obj.patch_args_from_config(confs)

args_obj.apply_changes()

args = args_obj.get_args()

if args.server is False and args.client is False:
    logger.error("No action selected! Specify --client or --server")
    logger.debug("Exiting...")
    sys.exit(1)

if args.server:
    server = Server(dirs.cert_dir, args)

if args.client:
    client = Client(dirs.cert_dir, args)
    client.sendFile("test/big.file")