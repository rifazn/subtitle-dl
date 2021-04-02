#!/bin/env python

import requests
from tabulate import tabulate
import sys

headers = {
        "User-Agent": "TemporaryUserAgent",
}

if len(sys.argv) != 2:
    print("Usage ./subpyner.py \"movie name\"")
    sys.exit(1)

print(sys.argv[1])
response = requests.get(f'https://rest.opensubtitles.org/search/query-{sys.argv[1]}', headers=headers)

if response.status_code != 200:
    print("Error in Request")
    sys.exit(2)

data = response.json()

dd = [[movie['MovieName'], movie['SubFileName'][:20],
       movie['SubDownloadLink'][:20],
       movie['Score']] for movie in data[:5]]
print(tabulate(dd, headers=['Movie Name', 'Subtitle Name', 'URL', 'Rating']))
