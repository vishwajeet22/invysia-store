import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_path = Path(__file__).parent.parent.parent / "invysia-store.log"
    
    # Create a root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Check if handlers are already configured to avoid duplicate logs
    if not logger.handlers:
        # Create RotatingFileHandler
        # Max size 5MB, keep 3 backup files
        handler = RotatingFileHandler(
            log_path, 
            maxBytes=5*1024*1024, 
            backupCount=3,
            encoding='utf-8'
        )
        
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
        # Also add a stream handler to print to console if needed, 
        # but for now we stick to file as per original intent, 
        # maybe adding a basic console handler for critical errors is good practice,
        # but the user request specifically focused on rotation vs deletion.
        # We'll stick to the file handler as the primary output to match previous behavior but better.

    print(f"✅ Logging configured at {log_path}")

# Initialize logging on import
setup_logging()