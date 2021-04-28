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

    # The main argument
    parser.add_argument('moviename')

    # The optional but essential 'options'
    parser.add_argument('-j', '--json',
            help='Prints the output formatted as json',
                action="store_true")
    parser.add_argument('-c', '--clipboard',
            help='Get the movie name from clipboard.',
                action="store_true")
    parser.add_argument('-i', help='Interactive mode. Classic prompt mode for selecting the subtitle',
                action="store_true")
    parser.add_argument('-m', '--menu',
            help='Use a menu program like dmenu, bemenu, etc.')

    # Now parse the arguments passed on the command line
    args = parser.parse_args()

    subs = get(args.moviename)

    if args.menu:
        menu = args.menu
        menu_items = f'\n'.join([f'{sub[0]:>3} | {sub[2]:<80} | Rating {sub[-1]}' for sub in subs])

        # Let the user choose the sub through the given menu application
        choice = subprocess.run(menu.split(), input=menu_items, capture_output=True, text=True)
        idx = int(choice.stdout.split('|')[0]) - 1

        # Download the resource
        url = subs[idx][-2]
        r = requests.get(url)

        if r.status_code == 200: # Download successful
            header = r.headers
            fname = header['Content-Disposition'].split('filename=')[1].strip('"')
            with open('/tmp/' + fname, 'wb') as f:
                f.write(r.content)

        print(choice.stdout)
        print(idx, subs[idx][-2])

    elif args.json:
        print(json.dumps(subs))

    else:
        print(tabulate(subs, headers=['Movie Name', 'Subtitle Name', 'URL', 'Rating']))
