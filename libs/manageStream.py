import json
import os
from .wireguard import wireguardControl
import logging


def deployStream(stream):
    try:
        if os.path.exists("/etc/wireguard/{}.conf".format(stream["stream_id"])):
            wireguardControl("down", stream)
        with open("/etc/wireguard/{}.conf".format(stream["stream_id"]), "w") as wgconf:
            wgconf.write(stream["config"])
        error, status = wireguardControl("up", stream)
        return error, status
    except Exception as error:
        raise error


def removeStream(ws, stream):
    error = wireguardControl("down", stream)
    if error == "":
        try:
            os.remove("/etc/wireguard/{}.conf".format(stream["stream_id"]))
            ws.send(json.dumps(
                {"cmd": "delete", "id": stream["stream_id"]}))
        except Exception as error:
            return error, stream["status"]
    return error
