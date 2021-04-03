# Subtitle-dl

A command line python app that downloads subtitle of any movie by consuming opensubtitles.org's API. This is part of a project being made for my university's "Software Engineering" course.

## Installation

1. Clone the repository.
2. Create a virtual environment and source it (`python -m venv venv && source venv/bin/activate`)
3. Install the dependencies (`pip install -r requirements`).

## Usage

`python srt-gt.py <Movie Name>`

### Options

```sh
$ python srt-gt.py -h
usage: srt-gt.py [-h] [-j] [-c] [-i] [-m MENU] moviename

positional arguments:
  moviename

optional arguments:
  -h, --help            show this help message and exit
  -j, --json            Prints the output formatted as json
  -c, --clipboard       Get the movie name from clipboard.
  -i                    Interactive mode. Classic prompt mode for selecting the subtitle
  -m MENU, --menu MENU  Use a menu program like dmenu, bemenu, etc.

```
