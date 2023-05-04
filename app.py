from os.path import exists
from uuid import UUID
from libs.logger import setup_logger
from libs.daemonise import Daemon
import libs.client as client
import logging
import argparse

parser = argparse.ArgumentParser(
    "Watershed Daemon", description="A daemon that automatically deploys your SD-WANs.", epilog="This is the end of the help message.")

parser.add_argument(
    "-s", "--stop", help="Stop the daemon", action="store_true")
parser.add_argument("-r", "--restart",
                    help="Restart the daemon", action="store_true")

parser.add_argument("-v", "--verbose",
                    help="Increase output verbosity in logs", action="store_true")

parser.add_argument(
    "-d", "--daemon", help="Run as a daemon", action="store_true")

parser.add_argument("-u", "--url", help="Set API URL")

parser.add_argument("-k", "--key", help="Set API key")


def checkAPIParms():
    key = ""
    url = ""

    logger.debug("Checking login credentials")
    if args.url:
        url = args.url
        logger.debug("Using API URL from command line")
    if args.key:
        try:
            uuid = UUID(args.key, version=4)
            logger.debug("Using API key from command line")
            key = args.key
        except ValueError:
            pass
    if len(url) == 0:
        if exists("api_url.txt"):
            with open("api_key.txt", "r") as file:
                lines = file.readlines()
                for line in lines:
                    url = line.strip("\n")
                    logger.debug("Using API URL from file")
        else:
            logger.critical("Valid API URL not found")
    if len(key) == 0:
        if exists("api_key.txt"):
            with open("api_key.txt", "r") as file:
                lines = file.readlines()
                for line in lines:
                    try:
                        uuid = UUID(line.strip("\n"), version=4)
                        logger.debug("Using API key from file")
                        key = line.strip("\n")
                    except ValueError:
                        pass
        else:
            logger.critical("Valid API key not found")
    return key, url


class daemon(Daemon):
    def run(self):
        api_key, api_url = checkAPIParms()
        if len(api_key) == 0:
            logger.critical(
                "A valid API key is required to run this program. Please correctly set it somewhere in the api_key.txt file.")
        elif len(api_url) == 0:
            logger.critical(
                "A valid API URL is required to run this program. Please correctly set it somewhere in the api_url.txt file.")
        else:
            logger.info("Valid API key found.")
            logger.info("Starting daemon")
            try:
                # while True:
                # logger.debug("Daemon running")
                client.start(api_key, api_url)

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
