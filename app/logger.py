import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s %(asctime)s - %(name)s -%(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)


def get_logger(file_name: str) -> logging.Logger:
    """Returns a logger instance for the specified file."""
    return logging.getLogger(file_name)