"""
__init__.py: TWiki to MediaWiki formatting root.

Created by Perry Naseck on 2022-05-29.
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

from json import load
from typing import List

from twiki_to_mediawiki_xml.twiki_to_mediawiki_format.page_names_replace import \
    TwikiToMediaWikiPageNamesReplace  # noqa: E501
from twiki_to_mediawiki_xml.twiki_to_mediawiki_format.subpages import \
    TwikiToMediaWikiSubpages


class TWikiToMediaWikiFormat():
    """Convert TWiki to MediaWiki formatting."""

    def __init__(self, twiki_json_path: str, page_names_csv_path: str):
        """Initialize converting TWiki to MediaWiki formatting."""
        self.twiki_json_path = twiki_json_path
        self.page_names_csv_path = page_names_csv_path

        self.twiki_json = None
        self.mediawiki_pages = None

    def run(self) -> None:
        """Run the conversion."""
        # Read JSON
        with open(self.twiki_json_path, "r", encoding="utf-8") as file_txt:
            self.twiki_json = load(file_txt)

        # replace page names (titles)
        page_names_replace = TwikiToMediaWikiPageNamesReplace(
            self.twiki_json,
            self.page_names_csv_path)
        page_names_replace.run()
        self.mediawiki_pages = page_names_replace.get_pages()

        # subpages
        subpages_conversion = TwikiToMediaWikiSubpages(self.mediawiki_pages)
        subpages_conversion.run()
        self.mediawiki_pages = subpages_conversion.get_pages()

    def get_mediawiki_pages(self) -> List[dict]:
        """Return the converted pages."""
        return self.mediawiki_pages
