#  Copyright 2022 Google LLC.
#
#  This software is provided as is, without warranty or representation for
#  any use or purpose. Your use of it is subject to your agreement with Google.
#
# This is not an official Google product.

import contextlib
import logging
import requests
from http.client import HTTPConnection
from .util import print_err, _DEBUG
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

BASE_API_URL = "https://app.searchstax.com/api/rest/v2"

# We consider these HTTP status codes 'good' responses, any other ones will trigger an error.
# This list may be incomplete, but has been tested and confirmed to be working as expected.
# This could also be handled using the `.ok` result method with something like: `if result.ok == True:``,
# but that uses too broad set of allowable codes (anything < 400), which adds debugging complexity and ambiguity for automation purposes
SUCCESS_HTTP_CODES = [ 200, 201, 203, 301, 302 ]

# A timeout of 30 will result in a timeout on creating users
DEFAULT_TIMEOUT = 60 # seconds

# common server errors: 500, 502, 503, 504
# rate limit exceeded: 429

# Backoff algo:
#   {backoff factor} * (2 ** ({number of total retries} - 1))

# 10 second backoff factor - 5, 10, 20, 40, 80, 160, 320, 640, 1280, 2560
retry_strategy = Retry(
    total=10,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["DELETE", "POST", "GET"],
    backoff_factor=10
)

if _DEBUG > 0:
    HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

def make_request(headers={"Content-Type": "application/json"}, base_url=BASE_API_URL, endpoint='', method='get', data={}, allow_errors=False, file={}):
    # Utility function to streamline making API requests using the `requests` library, only GET and POST methods are needed and supported.

    url = base_url + "/" + endpoint

    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    if data == {} and method == 'post' and file == {}:
        print_err("No POST data passed to make_request()", "Warning")

    if method == 'post':
        if file != {}:
            r = http.post(url, headers=headers, files=file, timeout=DEFAULT_TIMEOUT)
        else:
            r = http.post(url, data=data, headers=headers, timeout=DEFAULT_TIMEOUT)
    elif method == 'get':
        r = requests.get(url, data=data, headers=headers, timeout=DEFAULT_TIMEOUT)
    elif method == 'delete':
        r = http.delete(url, data=data, headers=headers, timeout=DEFAULT_TIMEOUT)
    elif method == 'patch':
        r = http.patch(url, data=data, headers=headers, timeout=DEFAULT_TIMEOUT)

    if not allow_errors and r.status_code not in SUCCESS_HTTP_CODES:
        if _DEBUG > 0:
            logging.debug(url)
            logging.debug(headers)
            logging.debug(data)
            logging.debug(file)
            try:
                logging.debug(r.json())
            except:
                pass

        print_err(F"Call to endpoint: '{endpoint}' returned unsupported response, with status code: {r.status_code}. Exiting.", "Error", r.text)
    else:
        return r