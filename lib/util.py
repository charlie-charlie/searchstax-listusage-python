#  Copyright 2022 Google LLC.
#
#  This software is provided as is, without warranty or representation for
#  any use or purpose. Your use of it is subject to your agreement with Google.
#
# This is not an official Google product.

import logging
import sys
from pprint import pformat

# Set to any (int) > 0 to enable debug messages
_DEBUG = 8

def print_err(err, sev, dump={}):
    # Utility function to print consistent messages and fail fast on API errors

    logging.debug(F"{sev}: {err}")
    if dump != {}:
        logging.debug(pformat(dump))
    if sev == "Error":
        sys.exit(1)
