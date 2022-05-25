#!/usr/bin/env python3
"""
twiki_to_mediawiki_xml.py: Convert a TWiki to MediaWiki XML.

Created by Perry Naseck on 2022-05-23.
This file is part of the https://github.com/ABTech/twiki-to-mediawiki-xml

Copyright (C) 2022-present  AB Tech, Carnegie Mellon University
Copyright (C) 2022          Perry Naseck (git@perrynaseck.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import sys
import traceback
from json import dumps
from logging import getLogger
from os.path import normpath

from twiki_to_mediawiki_xml.twiki_parser import TWikiParser

logger = getLogger(__name__)

LICENSE_NOTICE = """twiki-to-mediawiki-xml Copyright (C) 2022-present  AB Tech
This program comes with ABSOLUTELY NO WARRANTY; for details see LICENSE and
README.md. This is free software, and you are welcome to redistribute it
under certain conditions; for details see LICENSE and README.md.

"""


def main() -> int:
    """Convert a TWiki to MediaWiki XML."""
    parser = argparse.ArgumentParser(
        description='Convert a TWiki to MediaWiki XML.',
        epilog=LICENSE_NOTICE)
    parser.add_argument('command',  type=str,
                        choices=['twiki_parser'],
                        help='Which tool to run')
    parser.add_argument('in_path',  type=str,
                        help='Input path')
    parser.add_argument('out_path',  type=str,
                        help='Output path')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Don\'t output the result, just run')
    args = parser.parse_args()

    norm_in_path = normpath(args.in_path)
    norm_out_path = normpath(args.out_path)

    out = ""
    try:
        if args.command == 'twiki_parser':
            parser = TWikiParser(norm_in_path, norm_out_path)
            out = parser.run()
        if not args.quiet:
            print(dumps(out))

    except Exception as error:  # pylint: disable=broad-except
        logger.error('%s\n\n%s', repr(error), traceback.format_exc())
        return 1

    return 0


if __name__ == "__main__":
    RES = main()
    sys.exit(RES)
