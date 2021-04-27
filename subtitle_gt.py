#!/bin/env python

import sys
import json
import requests
import subprocess
from string import Template
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

    subs = [[idx, movie['MovieName'], movie['SubFileName'], movie['SubDownloadLink'],
            movie['Score']] for idx, movie in enumerate(data, start=1)]

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
        menu_items = f'\n'.join([f'{sub[0]:>3} | {sub[2]:<80} | Rating {sub[-1]}' for sub in subs])
        choice = subprocess.run(menu.split(), input=menu_items, capture_output=True, text=True)
        print(choice.stdout)
        idx = choice.stdout.split('|')[0]
        print(idx, subs[int(idx)][-2])
    elif args.json:
        print(json.dumps(subs))
    else:
        print(tabulate(subs, headers=['Movie Name', 'Subtitle Name', 'URL', 'Rating']))
