"""
Centralized Application Logger.
Configures stream and file logging with standardized formatting.
"""

import logging
import sys
from app.config.settings import LOG_FILE_PATH, ensure_directories

def setup_logger(name: str = "resume_builder") -> logging.Logger:
    """Configures and returns a logger instance."""
    ensure_directories()
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger
        
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # File Handler
    try:
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
    except Exception as e:
        console_handler.emit(
            logging.LogRecord(
                name, logging.WARNING, __file__, 0,
                f"Could not initialize log file: {e}", (), None
            )
        )
        
    return logger

logger = setup_logger()
