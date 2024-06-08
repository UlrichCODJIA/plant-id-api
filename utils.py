import logging


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in [
        "jpg",
        "jpeg",
        "png",
    ]


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
