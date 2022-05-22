import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/exseas_explorer/exseas_explorer/")

from app import server as application
