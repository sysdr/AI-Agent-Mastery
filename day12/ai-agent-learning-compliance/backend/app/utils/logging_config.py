import logging
import sys
from pathlib import Path

def setup_logging():
    """Setup structured logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/app.log', mode='a')
        ]
    )
    
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
