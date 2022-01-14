#!/bin/env python

from iterfzf import iterfzf
from tabulate import tabulate
from argparse import ArgumentParser, SUPPRESS
import os, re, sys, tempfile, json, gzip, requests, subprocess

def _menu(menu, subs_list):
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

def _save(fname, file_contents, outfilename=None):
    video_extensions = tuple(".mp4 .mkv .avi".split())
    if fname.endswith(video_extensions):
        fname = fname[:-3] + 'srt'
    elif not fname.endswith('.srt'):
        fname += fname + '.srt'

    # if outfilename is a directory
    if outfilename is not None:
        if outfilename.endswith(os.path.sep):
            if not os.path.isdir(outfilename):
                print("The directory does not exist. Please create it first.")
                sys.exit(4)
            fname = os.path.join(outfilename, fname)
        else:
            fname = outfilename[:]

    with open(fname, 'wb') as f:
        f.write(file_contents)
    print("File saved to", fname)

def get_subs(moviename):
    """Get a list of subtitles for 'moviename' where each sub is a dictionary.

    Keys in each dict item
    ----------------------
    'MovieName', 'SubFileName', 'SubDownloadLink', 'SubRating'

    Returns:
    list(dict)
    """
    headers = {
            "User-Agent": "TemporaryUserAgent",
    }

    english_only = 'sublanguageid-eng'

    response = requests.get(
        f'https://rest.opensubtitles.org/search/query-{moviename}/{english_only}',
        headers=headers)

    if response.status_code != 200:
        print("Error in Request")
        print(f'status: {response.status_code}',
              f'content: {response.content}', sep='\n')
        sys.exit(2)

    data = response.json()

    keys = ['MovieName', 'SubFileName', 'SubDownloadLink', 'SubRating']
    subs = [{key: sub[key] for key in keys} for sub in data]
    subs.sort(key=lambda sub: float(sub['SubRating']), reverse=True)

    return subs

def _get_cli_args():
    parser = ArgumentParser()

    # The main argument
    parser.add_argument('moviename')

    # The optional, but essental, 'options'
    parser.add_argument('-m', '--menu', action='store',
        help='Use a menu program like dmenu, bemenu, etc.')
    parser.add_argument('-R', '--best-rating', action='store_true',
        help='Download the best rated subtitle. Don\'t prompt user.')
    parser.add_argument('--feeling-lucky', action='store_true',
        help=SUPPRESS)

    # All the related to output
    out_group = parser.add_mutually_exclusive_group()
    out_group.add_argument('-j', '--json', action='store_true',
        help='Prints the output formatted as json.')
    out_group.add_argument('-p', '--print', action='store_true',
        help='Print subtitles formatted as a table. Do not parse this.')
    out_group.add_argument('-o', '--output', metavar='', dest='output',
        help='Output to <filename_or_dir>. For ex: /dir/fname.srt, or /dir/.')
    out_group.add_argument('-x', '--dont-rename', action='store_true',
        help='Download file with original name. Do not rename to <movie_name>.')

    return parser.parse_args()


if __name__ == "__main__":
    # Parse cli arguments
    args = _get_cli_args()

    # Get subtitles from the REST apis
    subs_dict_list = get_subs(args.moviename)
    subs_dict_enum = enumerate(subs_dict_list)

    # Format the dictionary items to be readable
    _fields = lambda sub: [sub['SubFileName'], sub['SubRating']]
    subs_list = ['{:<3} | {:<50.50} | {:<3.4}'
                 .format(idx, *_fields(sub)) for idx, sub in subs_dict_enum]

    if args.json:
        print(json.dumps(subs_dict_list))
        sys.exit(0)

    # Subtitle selection. Download best rated subtitle, or
    # Run the menu and let user choose
    if args.best_rating or args.feeling_lucky:
        idx = 0
    else:
        choice = _menu(args.menu, subs_list)
        try:
            idx = int(choice.split(' | ')[0])
        except (TypeError, AttributeError):
            print("No sub selected.", "Exiting.")
            sys.exit(1)
        except Exception as e:
            print(f"Exception: {e.__class__}")
            sys.exit(4)

    # Download the subtitle which is probaby gzipped
    url = subs_dict_list[idx]['SubDownloadLink']
    print(idx, url)
    r = requests.get(url)

    if r.status_code == 200:
        header = r.headers

        # Write the downloaded gzip file
        gzipname = header['Content-Disposition'].split('filename=')[1].strip('"')
        with open(os.path.join(tempfile.gettempdir(), gzipname), 'wb') as f:
            f.write(r.content)

        # Extract the gzip file and read the content
        with gzip.open(f.name, 'rb') as gzipfile:
            file_contents = gzipfile.read()

        # Write the content as regular subtitle file
        if not args.dont_rename:
            _save(args.moviename, file_contents, outfilename=args.output)
        else:
            srt_name = gzipname[:-3]
            with open(srt_name, 'wb') as subfile:
                subfile.write(file_contents)

        print("done")
    else:
        print("Could not download resource. Status: ", r.status_code)


