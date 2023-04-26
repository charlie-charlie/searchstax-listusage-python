#  Copyright 2022 Google LLC.
#
#  This software is provided as is, without warranty or representation for
#  any use or purpose. Your use of it is subject to your agreement with Google.
#
# This is not an official Google product.

import json
import logging
import time
import urllib
import yaml
from pprint import pformat

from .api import BASE_API_URL, SUCCESS_HTTP_CODES, make_request
from .util import print_err, _DEBUG


def get_auth_token(username, password):
    # Retrieves an authentication token valid for 24 hours from SearchStax account
    # The params described below should be passed via export to environment, as described where the credentials are imported from your system's environment, at the top of this script
    # Params:
    #   username - username with Admin or Owner privileges on SearchStax account
    #   password - password with Admin or Owner privileges on SearchStax account
    # Returns:
    #   r - JSON-formatted HTTP headers with a token for making token-authenticated API calls

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    endpoint = "obtain-auth-token/"
    data = {
        "username": username,
        "password": password
    }

    r = make_request(headers, BASE_API_URL, endpoint, 'post', data)

    r_json = r.json()
    token = r_json["token"]

    if _DEBUG > 0:
        logging.debug(pformat(r_json))
        logging.debug(token)

    if len(token) > 0:
        logging.debug("Received SSX token.")
        auth_headers = {
            "Content-Type": "application/json",
            "Authorization": "Token " + token + ""
        }
        return auth_headers
    else:
        print_err("Invalid token received: '" + token + "'. Exiting.", "Error", r.json())


def solr_deployments(account_api_url, auth_headers):
    """
    Params:
    Returns:
        json return all deployments in solr account
    """
    endpoint = "deployment/"
    resp = make_request(auth_headers, account_api_url, endpoint, 'get').json()

    if _DEBUG == 7:
        logging.debug(pformat(resp))
    
    return resp


def solr_account_usage(account_api_url, auth_headers, year, month):
    """
    Params
        year: calendar year, like 2023
        month: month in number, like 04, 11
    Return:
        json return usages of solr account
    """
    endpoint = F"usage/{year}/{month}/"

    resp = make_request(auth_headers, account_api_url, endpoint, 'get').json()

    if _DEBUG == 7:
        logging.debug(pformat(resp))
    
    return resp
