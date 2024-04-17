from loguru import logger

logger.add(
    "./running_log.log",
    level="INFO",
    rotation="10days"
)