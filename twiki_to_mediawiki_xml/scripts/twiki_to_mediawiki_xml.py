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

# from twiki_to_mediawiki_xml import ?

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
    parser.add_argument('twiki_data_web_path',  type=str,
                        help='Path to TWiki data web folder')
    args = parser.parse_args()

    print(args.twiki_data_web_path)
    print("Nothing yet!")

    return 0


if __name__ == "__main__":
    RES = main()
    sys.exit(RES)
