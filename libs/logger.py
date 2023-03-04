import logging


def setup_logger(fileName, instance="root", level=logging.INFO):
    """Setup logging configuration"""
    logFile = fileName

    # Set the logging format
    format = logging.Formatter("[%(asctime)s]-%(levelname)s--> %(message)s")

    # Handle file logging
    fileLog = logging.FileHandler(logFile, mode="w")
    fileLog.setFormatter(format)
    fileLog.setLevel(level)

    # Handle DEBUG logging
    debugFileLog = logging.FileHandler("DEBUG-"+logFile)
    debugFileLog.setFormatter(format)
    debugFileLog.setLevel(logging.DEBUG)

    # Handle console logging
    consoleLog = logging.StreamHandler()
    consoleLog.setFormatter(format)
    consoleLog.setLevel(level)

    # Create the new logger
    logger = logging.getLogger(instance)
    logger.setLevel(logging.DEBUG)

    # Add handlers to the logger
    logger.addHandler(fileLog)
    logger.addHandler(debugFileLog)
    logger.addHandler(consoleLog)

    return logger
