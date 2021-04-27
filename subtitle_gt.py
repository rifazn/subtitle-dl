#!/bin/env python

import sys
import json
import requests
import subprocess
from tabulate import tabulate
from argparse import ArgumentParser

headers = {
        "User-Agent": "TemporaryUserAgent",
}

# TODO: Implement the options: c, i, and m

def get(movie):
    response = requests.get(
        f'https://rest.opensubtitles.org/search/query-{movie}',
        headers=headers)

    if response.status_code != 200:
        print("Error in Request")
        sys.exit(2)

    data = response.json()

    subs = [[movie['MovieName'], movie['SubFileName'], movie['SubDownloadLink'],
            movie['Score']] for movie in data[:5]]

    return subs

if __name__ == "__main__":
    # CLI arguments parser
    parser = ArgumentParser()

    parser.add_argument('moviename')
    parser.add_argument('-j', '--json', help='Prints the output formatted as json',
                        action="store_true")
    parser.add_argument('-c', '--clipboard', help='Get the movie name from clipboard.',
                        action="store_true")
    parser.add_argument('-i', help='Interactive mode. Classic prompt mode for selecting the subtitle',
                        action="store_true")
    parser.add_argument('-m', '--menu', help='Use a menu program like dmenu, bemenu, etc.')
    args = parser.parse_args()

    subs = get(args.moviename)

    if args.menu:
        menu = args.menu
        menu_items = '\n'.join(map(lambda x: f'{x[1]} | Rating: {x[-1]}', subs))
        print(menu_items)
        choice = subprocess.run(menu.split(), input=menu_items, capture_output=True, text=True)
        print(f'User Choice: {choice.stdout}')
    elif args.json:
        print(json.dumps(subs))
    else:
        print(tabulate(subs, headers=['Movie Name', 'Subtitle Name', 'URL', 'Rating']))
