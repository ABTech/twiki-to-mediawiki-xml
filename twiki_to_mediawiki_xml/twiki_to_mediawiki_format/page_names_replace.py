"""
page_names_format.py: TWiki to MediaWiki page name replacement.

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

from copy import deepcopy
from csv import reader
from logging import getLogger
from typing import List

logger = getLogger(__name__)


class TwikiToMediaWikiPageNamesReplace():
    """Replace TWiki style page names with MediaWiki style page names."""

    def __init__(self, twiki_pages: List[dict], names_path: dict):
        """Initialize conversion to MediaWiki page names."""
        self.names_path = names_path
        self.mediawiki_pages = deepcopy(twiki_pages)

        self.names = {}

    def run(self) -> None:
        """Run the page name replacement."""
        with open(self.names_path, "r", encoding="utf-8") as file_names:
            key_values = list(reader(file_names))
            for key_value in key_values:
                key, value = key_value[0], key_value[1]
                self.names[key] = value

        for page in self.mediawiki_pages:
            page_name = page["page_name"]
            if page_name not in self.names:
                logger.warning(
                    'Missing page name replacement for %s', page_name)
            else:
                new_page_name = self.names[page_name]
                if new_page_name != page_name:
                    page["old_page_name"] = page_name
                    page["page_name"] = new_page_name

            # And topic parent
            if "TOPICPARENT" in page["metas"]:
                for parent in page["metas"]["TOPICPARENT"]:
                    old_parent_name = parent["name"]
                    if old_parent_name not in self.names:
                        logger.warning(
                            'Missing parent page name replacement %s',
                            old_parent_name)
                    else:
                        new_parent_name = self.names[old_parent_name]
                        if new_parent_name != old_parent_name:
                            parent["old_name"] = old_parent_name
                            parent["name"] = new_parent_name

    def get_pages(self) -> List[dict]:
        """Return the converted pages."""
        return self.mediawiki_pages
