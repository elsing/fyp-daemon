import subprocess
import logging
import os


def setOnBoot(status, streamName):
    logging.debug(subprocess.run(["systemctl", "{}".format(status), "wg-quick@{}".format(
        streamName)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode("utf-8"))


def deleteConfig(streamName):
    try:
        os.remove("/etc/wireguard/{}.conf".format(streamName))
    except Exception as error:
        logging.error("Failed to remove old file: {}".format(error))
        raise error


def cleanUp(streamName):
    setOnBoot("disable", streamName)
    deleteConfig(streamName)


def wireguardControl(status, stream):
    result = subprocess.run(
        ["wg-quick", status, "/etc/wireguard/{}.conf".format(stream["name"])], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    logging.debug("Wireguard CMD code: {} result: \n{}".format(
        result.returncode, result.stdout.decode("utf-8")))
    if result.returncode == 0:
        try:
            if status == "up":
                setOnBoot("enable", stream["name"])
                logging.info(
                    "Deployed stream '{}' successfully".format(stream["name"]))
                return "", "up"
            elif status == "down":
                cleanUp(stream["name"])
                logging.info(
                    "Downed stream '{}' successfully".format(stream["name"]))
                return "", "down"  # No status to return
        except Exception as error:
            logging.error("Error during attempted removal: \n{}".format(error))
            raise error
    else:
        # Handle status error
        logging.error(
            "Failed to bring stream '{}' {}".format(stream["name"], status))
        # Return error and status
        error = result.stdout.decode("utf-8")
        if status == "down":
            return error, "pendingDelete"
        return error, "error"
