#!/bin/env python

from iterfzf import iterfzf
from tabulate import tabulate
from argparse import ArgumentParser
import sys, json, gzip, requests, subprocess

def _menu(menu, subs_list):
    # TODO: Raise an exception in the try block. So the caller can deal with
    # it as needed.
    # TODO: print error log instead of stdout print
    if menu:
        subs_str = '\n'.join(subs_list)
        try:
            choice = subprocess.run(menu.split(), input=subs_str, text=True,
                                check=True, capture_output=True).stdout
        except subprocess.CalledProcessError as err:
            print("Error: ", err)
            print("Exiting.")
            sys.exit(3)
    else:
        choice = iterfzf(subs_list)

    return choice

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

    keys = ['MovieName', 'SubFileName', 'SubDownloadLink', 'Score']
    subs = [{key: sub[key] for key in keys} for sub in data]

    return subs

def _get_cli_args():
    parser = ArgumentParser()

    # The main argument
    parser.add_argument('moviename')

    # The optional, but essental, 'options'
    parser.add_argument('-m', '--menu', action='store',
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
    # Parse cli arguments
    args = _get_cli_args()

    # Get subtitles from the REST apis
    subs_dict_list = get_subs(args.moviename)
    subs_dict_enum = enumerate(subs_dict_list)

    # Format the dictionary items to be readable
    _filter = lambda i, sub: [i, sub['MovieName'], sub['SubFileName'], sub['Score']]
    subs_list = ['{:<3} | {:10.10} | {:<50.50} | {:<3.2}'
                 .format(*_filter(idx, sub)) for idx, sub in subs_dict_enum]

    # Run the menu and let user choose
    choice = _menu(args.menu, subs_list)
    idx = int(choice.split(' | ')[0])

    # Download the subtitle which is probaby gzipped
    url = subs_dict_list[idx]['SubDownloadLink']
    print(idx, url)
    r = requests.get(url)

    if r.status_code == 200:
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


