"""
__init__.py: Convert TWiki to JSON.

Created by Perry Naseck on 2022-05-24.
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

from glob import glob
from logging import getLogger
from os.path import basename, exists, splitext

logger = getLogger(__name__)


class TWikiParser():
    """Convert TWiki to JSON."""

    def __init__(self, twiki_data_web_path: str, out_path: str):
        """Initialize the TWiki convertor class."""
        self.twiki_data_web_path = twiki_data_web_path
        self.out_path = out_path

        self.twiki_pages = []

    def run(self):
        """Run the conversion."""
        # Find all of the page files
        self.twiki_pages = self.find_data_files()

        return self.twiki_pages

    def find_data_files(self):
        """Find TWiki data files in input folder."""
        twiki_txt_files = glob(f'./{self.twiki_data_web_path}/*.txt')
        twiki_pages = []

        for twiki_txt_file in twiki_txt_files:
            page = {
                "twiki_txt_path": twiki_txt_file,
                "twiki_page_name": splitext(basename(twiki_txt_file))[0]
            }

            revision_path = f'{twiki_txt_file},v'
            if exists(revision_path):
                page["twiki_v_path"] = revision_path
            else:
                logger.warning('No revision file for %s', twiki_txt_file)

            twiki_pages.append(page)
        return twiki_pages

    def parse_metadata(self):
        """Parse TWiki data file metadata."""

    def parse_contents(self):
        """Parse TWiki data file contents."""

    def parse_revisions(self):
        """Parse TWiki data revisions."""
