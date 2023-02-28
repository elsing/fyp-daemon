from os.path import exists
from uuid import UUID
from libs.logger import setup_logger
from libs.daemonise import Daemon
import libs.client as client
import logging
import argparse

# logger.basicConfig(filename="logs.log",
#                     format="%(asctime)s - %(levelname)s --> %(message)s", level=logger.DEBUG)

parser = argparse.ArgumentParser(
    "Watershed Daemon", description="A daemon that automatically deploys your SD-WANs.", epilog="This is the end of the help message.")

# parser.add_argument("start", help="Start the daemon")
parser.add_argument(
    "-s", "--stop", help="Stop the daemon", action="store_true")
parser.add_argument("-r", "--restart",
                    help="Restart the daemon", action="store_true")
# parser.add_argument(
# "-l", "--login", help="Login to Watershed API", action="store_true")

parser.add_argument("-v", "--verbose",
                    help="Increase output verbosity in logs", action="store_true")

parser.add_argument(
    "-d", "--daemon", help="Run as a daemon", action="store_true")

parser.add_argument("-k", "--key", help="Set API key")


def checkLogin():
    logger.debug("Checking login credentials")
    if args.key:
        try:
            uuid = UUID(args.key, version=4)
            logger.debug("Using API key from command line")
            return args.key
        except ValueError:
            pass
    if exists("api_key.txt"):
        with open("api_key.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                try:
                    uuid = UUID(line.strip("\n"), version=4)
                    logger.debug("Using API key from file")
                    return line
                except ValueError:
                    pass
    logger.critical("Valid API key not found")
    return False


class daemon(Daemon):
    def run(self):
        api_key = checkLogin()
        if not api_key:
            logger.critical(
                "A valid API key is required to run this program. Please correctly set it somewhere in the api_key.txt file.")
            # with
        else:
            logger.info("Valid API key found.")
            logger.info("Starting daemon")
            try:
                # while True:
                # logger.debug("Daemon running")
                client.start(api_key)

            except KeyboardInterrupt:
                logger.debug("Keyboard interrupt detected")
            except Exception as e:
                logger.debug("Exception: {}".format(e))
                logger.critical("Unexpected error")
            finally:
                logger.info("Stopped daemon")


if __name__ == "__main__":
    args = parser.parse_args()
    daemon = daemon("daemon.pid")
    if args.verbose:
        logger = setup_logger("log.log", level=logging.DEBUG)
        logger.info("Verbosity turned on")
    else:
        logger = setup_logger("log.log")
    if args.stop:
        logger.info("Stopping daemon")
        daemon.stop()
    elif args.restart:
        logger.info("Restarting daemon")
        daemon.restart()
    elif args.daemon:
        logger.info("Running as a daemon")
        daemon.start()
    else:
        daemon.run()
