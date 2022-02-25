#!/home/roman/dash_test/bin/python3
import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,".")

from FlaskApp import server as application
