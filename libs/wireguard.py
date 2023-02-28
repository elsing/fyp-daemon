import subprocess
import logging


def setOnBoot(status, streamName):
    logging.debug(subprocess.run(["systemctl", "{}".format(status), "wg-quick@{}".format(
        streamName)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode("utf-8"))


def deleteConfig(streamName):
    logging.debug(subprocess.run(["rm", "-f", "/etc/wireguard/{}.conf".format(
        streamName)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode("utf-8"))


def cleanUp(streamName):
    setOnBoot("disable", streamName)
    deleteConfig(streamName)


def wireguardControl(status, stream):
    result = subprocess.run(
        ["wg-quick", status, "/etc/wireguard/{}.conf".format(stream["name"])], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    logging.debug("Wireguard CMD code: {} result: {}".format(
        result.returncode, result.stdout.decode("utf-8")))
    if result.returncode == 0:
        try:
            if status == "up":
                setOnBoot("enabled", stream["name"])
                logging.info(
                    "Deployed stream '{}' successfully".format(stream["name"]))
                return "", "up"
            elif status == "down":
                cleanUp(stream["name"])
                logging.info(
                    "Downed stream '{}' successfully".format(stream["name"]))
                return ""  # No status to return
        except Exception as error:
            raise error
    else:
        # Handle status error
        logging.error(
            "Failed to bring stream '{}' {}".format(stream["name"], status))
        logging.debug("Change failed: {}".format(
            result.stdout.decode("utf-8")))
        # Return error and status
        error = result.stdout.decode("utf-8")
        return error, "error"
