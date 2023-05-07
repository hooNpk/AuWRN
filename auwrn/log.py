import os
import sys

MODULE_PATH = os.path.dirname(__file__)

class LogConfig(object):
    DEBUG=False
    LOGURU_SETTINGS={}

class ProductionLogConfig(LogConfig):
    LOGURU_SETTINGS = {
        "handlers": [
            dict(
                sink=f"{MODULE_PATH}/log/{{time:YYYY-MM-DD}}.log",
                format="[{level.name}] {message} ---- {time}",
                enqueue=True,
                serialize=False,
                rotation="00:00",
                retention=10,
                compression="zip"
            ),
        ],
        "levels" : []
    }

class DevelopmentLogConfig(LogConfig):
    DEBUG = True
    LOGURU_SETTINGS = {
        "handlers": [
            dict(
                sink=f"{MODULE_PATH}/log/{{time:YYYY-MM-DD}}.log",
                format="[{level.name}] {message} ---- {time}",
                enqueue=True,
                serialize=False,
                rotation="00:00",
                retention=10,
                compression="zip"
            ),
            dict(
                sink=sys.stdout,
                format="[{level.name}] {message} ---- {time}",
                enqueue=True,
                serialize=True
            ),
        ],
        "levels" : []
    }