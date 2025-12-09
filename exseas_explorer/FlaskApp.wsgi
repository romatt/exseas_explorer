import sys
import logging

logging.basicConfig(stream=sys.stderr)

from exseas_explorer.app import server as application  # noqa: F401
