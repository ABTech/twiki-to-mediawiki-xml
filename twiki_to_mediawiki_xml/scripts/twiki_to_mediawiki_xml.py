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
from shutil import which

from twiki_to_mediawiki_xml import __version__
from twiki_to_mediawiki_xml.mediawiki_xml_exporter import MediaWikiXMLExporter
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
                        choices=['twiki_parser', 'mediawiki_xml_exporter'],
                        help='Which tool to run')
    parser.add_argument('in_path',  type=str,
                        help='Input directory or file path')
    parser.add_argument('-b', '--base-page-url', action='store',
                        help='URL of MediaWiki base page.')
    parser.add_argument('-c', '--co-path', action='store',
                        help='Path to co binary')
    parser.add_argument('-d', '--db-name', action='store',
                        help='Name of MediaWiki database.')
    parser.add_argument('-o', '--out_path',  type=str,
                        help='Output to file (UTF-8) instead of stdout')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Don\'t output the result, just run')
    parser.add_argument('-s', '--site-name', action='store',
                        help='Name of MediaWiki site.')
    if __version__ is not None:
        parser.add_argument('--version', action='version',
                            version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    norm_in_path = normpath(args.in_path)

    out = ""
    try:
        if args.command == 'twiki_parser':
            co_path = which("cos")
            if co_path is None:
                raise Exception("Could not find co executable, please specify "
                                "--co-path!")
            cmd_args = [norm_in_path, co_path]
            cmd_kwargs = {}
            parser = TWikiParser(*cmd_args, **cmd_kwargs)
            parser.run()
            out = parser.get_pages()
            out_processed = dumps(out)
        elif args.command == 'mediawiki_xml_exporter':
            if (args.base_page_url is None or args.db_name is None or
                    args.site_name is None):
                parser.error("mediawiki_xml_exporter requires "
                             "--base-page-url, --db-name, and --site-name.")
            cmd_args = [
                norm_in_path,
                args.site_name,
                args.db_name,
                args.base_page_url
            ]
            cmd_kwargs = {}
            exporter = MediaWikiXMLExporter(*cmd_args, **cmd_kwargs)
            exporter.run()
            out_processed = exporter.get_xml_str()

        if args.out_path is not None:
            norm_out_path = normpath(args.out_path)
            with open(norm_out_path, "w",  encoding="utf-8") as out_file:
                out_file.write(out_processed)
        elif args.out_path is None and not args.quiet:
            print(out_processed)

    except Exception as error:  # pylint: disable=broad-except
        logger.error('%s\n\n%s', repr(error), traceback.format_exc())
        return 1

    return 0


if __name__ == "__main__":
    RES = main()
    sys.exit(RES)
