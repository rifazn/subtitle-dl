#!/bin/env python

import sys
import json
import gzip
import requests
import subprocess
from string import Template
from tabulate import tabulate
from argparse import ArgumentParser

headers = {
        "User-Agent": "TemporaryUserAgent",
}

# TODO:
# * Implement the options: c, i, and m
# * Implement retries in case of failed downloads
# * Use OS agnostic TMP dir
# * -m and -j ARE NOT be mutually exclusive. But now I think they should be.

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
    parser.add_argument('-p', '--print-table',
            help='Prints the output formatted as a table.',
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

    # Optionally print the results in stdout
    if args.json:
        print(json.dumps(subs))

    elif args.print_table:
        print(tabulate(subs, headers=['Movie Name', 'Subtitle Name', 'URL', 'Rating']))

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

            # Write the gzip file
            gzipname = header['Content-Disposition'].split('filename=')[1].strip('"')
            with open('/tmp/' + gzipname, 'wb') as f:
                f.write(r.content)

            # Extract the gzip file and read the content
            with gzip.open(f.name, 'rb') as gzipfile:
                file_contents = gzipfile.read()

            # Write the content as regular subtitle file
            srt_name = gzipname[:-3]
            with open(srt_name, 'wb') as subfile:
                subfile.write(file_contents)

            print("done")
        else:
            print("Could not download resource. Status: ", r.status_code)

        print(choice.stdout)
        print(idx, subs[idx][-2])

