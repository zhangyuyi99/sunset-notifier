"""Entry point for sunset-notifier."""
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from notifier.scheduler import run_loop

if __name__ == "__main__":
    logging.getLogger(__name__).info("Sunset notifier started.")
    run_loop(config)
