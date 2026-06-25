import sys
from loguru import logger
from utils.config import get_settings

settings = get_settings()

# Remove default handler
logger.remove()

# Console handler — clean and colored
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    colorize=True,
)

# File handler — full debug log, rotates at 5MB
logger.add(
    "vera.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="5 MB",
    retention="7 days",
    encoding="utf-8",
)


def get_logger(name: str):
    """
    Returns a logger bound to a module name.
    Usage: log = get_logger(__name__)
    """
    return logger.bind(name=name)
