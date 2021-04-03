#!/bin/env python

import requests
import json
from argparse import ArgumentParser
from tabulate import tabulate

parser = ArgumentParser()
parser.add_argument('moviename')
parser.add_argument('-j', '--json', help='Prints the output formatted as json',
                    action="store_true")
args = parser.parse_args()

headers = {
        "User-Agent": "TemporaryUserAgent",
}

response = requests.get(
    f'https://rest.opensubtitles.org/search/query-{args.moviename}',
    headers=headers)

if response.status_code != 200:
    print("Error in Request")
    sys.exit(2)

data = response.json()

dd = [[movie['MovieName'], movie['SubFileName'][:20],
       movie['SubDownloadLink'][:20],
       movie['Score']] for movie in data[:5]]
if args.json:
    print(json.dumps(dd))
else:
    print(tabulate(dd, headers=['Movie Name', 'Subtitle Name', 'URL', 'Rating']))
