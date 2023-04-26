#!/usr/bin/env python3

#  Copyright 2022 Google LLC.
#
#  This software is provided as is, without warranty or representation for
#  any use or purpose. Your use of it is subject to your agreement with Google.
#
# This is not an official Google product.


import configargparse
import logging
import sys
import json
import time
from pprint import pformat
import xlsxwriter

from lib.api import BASE_API_URL, make_request
from lib.searchstax import get_auth_token,  solr_account_usage, solr_deployments
from lib.util import print_err, _DEBUG

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

p = configargparse.ArgParser()
p.add('--account-name', help='Searchstax account name', env_var='ACCOUNT_NAME')
p.add('--solr-username', help='Searchstax account login email address', env_var='SOLR_USERNAME')
p.add('--solr-password', help='Searchstax account password', env_var='SOLR_PASSWORD')
p.add('--year', help='YEAR in digital', env_var='YEAR')
p.add('--month', help='MONTH in digital', env_var="MONTH")

options = p.parse_args()

account_name   = options.account_name
username       = options.solr_username
password       = options.solr_password
year           = options.year
month          = options.month

account_api_url = F"{BASE_API_URL}/account/{account_name}"

if __name__ == '__main__':
    # Declare dict to store solr uid and deployment name
    uid_deploymentname = {}

    # Declare array to store "deploymentName", "startDate", "endDate", "SKU", "usage"
    solr_usage = []

    # Initialize excel workbook
    workbook_name = F"solr_usage_{year}_{month}.xlsx"
    wb = xlsxwriter.Workbook(workbook_name)
    # Add a bold format to use to highlight cells.
    bold = wb.add_format({'bold': 1})

    worksheet = wb.add_worksheet()
    worksheet.write('A1', 'deploymentName', bold)
    worksheet.write('B1', 'startDate', bold)
    worksheet.write('C1', 'endDate', bold)
    worksheet.write('D1', 'SKU', bold)
    worksheet.write('E1', 'usage', bold)

    # Retrieve token
    auth_headers = get_auth_token(username, password)

    # List of deployments in searchstax account
    deployments= solr_deployments(account_api_url, auth_headers)

    # List all usages in searchstax account
    usages  = solr_account_usage(account_api_url, auth_headers, year, month)

    # Render dictionary to map uid to deployment name
    for deployment in deployments['results']:
        uid_deploymentname[deployment['uid']] = deployment['name']

    if _DEBUG == 8:
        logging.debug(pformat(uid_deploymentname))

    # Render set of solr deployname with its startDate, endDate, SKU and usage
    for usage in usages:
        try:
            solr_usage.append([uid_deploymentname[usage['objectID']], usage['startDate'], usage['endDate'], usage['SKU'], usage['usage']])
        except:
            solr_usage.append([usage['objectID'], usage['startDate'], usage['endDate'], usage['SKU'], usage['usage']])

    if _DEBUG == 8:
        logging.debug(pformat(solr_usage))
    
    row = 1
    col = 0

    for deploymentname, startdate, enddate, sku, usage in solr_usage:
        worksheet.write(row, col, deploymentname)
        worksheet.write(row, col+1, startdate)
        worksheet.write(row, col+2, enddate)
        worksheet.write(row, col+3, sku)
        worksheet.write(row, col+4, usage)

        row += 1
        col = 0

    wb.close()