import json
import os
from .wireguard import wireguardControl
import logging


def updateField(ws, stream_id, field, value):
    try:
        ws.send(json.dumps(
            {"cmd": "patch", "id": stream_id, "field": field, "value": value}))
    except Exception as error:
        raise error


def updateStream(ws, stream, error, status):
    updateField(ws, stream["stream_id"], "error", error)
    updateField(ws, stream["stream_id"], "status", status)


def deployStream(ws, stream):
    try:
        if os.path.exists("/etc/wireguard/{}.conf".format(stream["name"])):
            wireguardControl("down", stream)
        with open("/etc/wireguard/{}.conf".format(stream["name"]), "w") as wgconf:
            wgconf.write(stream["config"])
        error, status = wireguardControl("up", stream)
        updateStream(ws, stream, error, status)
        logging.info("Added stream '{}'".format(stream["name"]))
    except Exception as error:
        logging.error("Failed to deploy stream: \n{}".format(error))
        raise error


def downStream(ws, stream):
    try:
        error, status = wireguardControl("down", stream)
        updateStream(ws, stream, error, status)
        logging.info("Downed stream '{}'".format(stream["name"]))
    except Exception as error:
        logging.error("Failed to down stream: \n{}".format(error))
        raise error


def removeStream(ws, stream):
    error, status = wireguardControl("down", stream)
    updateStream(ws, stream, error, status)
    if error == "":
        try:
            ws.send(json.dumps(
                {"cmd": "delete", "id": stream["stream_id"]}))
            logging.info("Deleted stream '{}'".format(stream["name"]))
        except Exception as error:
            logging.error("WS Failed to delete stream: \n{}".format(error))
            raise error
    else:
        raise Exception("Problem: {}".format(error))
