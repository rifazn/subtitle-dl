#!/bin/env python

from string import Template
from tabulate import tabulate
from argparse import ArgumentParser
import sys, json, gzip, requests, subprocess

def fzf(input):
    print(input)

def print_json(subs):
    print(subs)

def save(rename=True):
    pass

def get_subs(moviename):
    """Get a list of subtitles for 'moviename' where each sub is a dictionary.

    Keys in each dict item
    ----------------------
    'MovieName', 'SubFileName', 'SubDownloadLink', 'Score'

    Returns:
    list(dict)
    """
    headers = {
            "User-Agent": "TemporaryUserAgent",
    }

    response = requests.get(
        f'https://rest.opensubtitles.org/search/query-{moviename}',
        headers=headers)

    if response.status_code != 200:
        print("Error in Request")
        print(f'status: {response.status_code}',
              f'content: {response.content}', sep='\n')
        sys.exit(2)

    data = response.json()

    subs = [
        [sub['MovieName'], sub['SubFileName'], sub['SubDownloadLink'],
         sub['Score']] for sub in data
    ]

    return subs

def _get_cli_args():
    parser = ArgumentParser()

    # The main argument
    parser.add_argument('moviename')

    # The optional, but essental, 'options'
    parser.add_argument('-m', '--menu', default=fzf,
        help='Use a menu program like dmenu, bemenu, etc.')

    # All the related to output
    out_group = parser.add_mutually_exclusive_group()
    out_group.add_argument('-j', '--json', action='store_true',
        help='Prints the output formatted as json.')
    out_group.add_argument('-p', '--print', action='store_true',
        help='Print subtitles formatted as a table. Do not parse this.')
    out_group.add_argument('-o', '--output', metavar='', dest='output',
        help='Output to <filename_or_dir>. For ex: /dir/fname.srt, or /dir/')

    return parser.parse_args()


if __name__ == "__main__":
    args = _get_cli_args()
    args.menu(args.moviename)

