"""
__init__.py: TWiki to MediaWiki subpages conversion.

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
from logging import getLogger
from typing import List

logger = getLogger(__name__)


class TwikiToMediaWikiSubpages():
    """Convert TWiki parents to MediaWiki subpages."""

    def __init__(self, twiki_pages: List[dict]):
        """Initialize conversion to MediaWiki subpages."""
        self.mediawiki_pages = deepcopy(twiki_pages)

    def run(self) -> None:
        """Run the subpage conversion."""
        children = {}
        children_by_index = {}
        for page_i, page in enumerate(self.mediawiki_pages):
            if ("TOPICPARENT" in page["metas"] and
                    len(page["metas"]["TOPICPARENT"]) > 0):
                if len(page["metas"]["TOPICPARENT"]) > 1:
                    logger.warning('Page %s has multiple TOPICPARENT, using '
                                   'first one.', page["page_name"])
                parent_name = page["metas"]["TOPICPARENT"][0]["name"]
                if "." in parent_name:
                    parent_name = parent_name.split(".")[1]
                page_name = page["page_name"]
                if page_name == parent_name:
                    logger.warning("Ignoring parent topic of same name for %s",
                                   parent_name)
                elif page_name.startswith("User:"):
                    logger.warning("Ignoring parent topic of %s for %s since "
                                   "it is a user page",
                                   parent_name, page_name)
                elif parent_name != 'WebHome':
                    children[page_name] = parent_name
                    children_by_index[page_name] = page_i
        for child_name, parent_name in children.items():
            reverse_path = [child_name, parent_name]
            next_parent = parent_name
            while next_parent in children:
                next_parent = children[next_parent]
                reverse_path.append(next_parent)
            names_path = reverse_path[::-1]
            new_page_name = self.page_to_subpage(names_path)
            page = self.mediawiki_pages[children_by_index[child_name]]
            if "old_page_name" not in page:
                # If page was not already renamed, this is now a rename
                page["old_page_name"] = page["page_name"]
            page["page_name"] = new_page_name

    def get_pages(self) -> List[dict]:
        """Return the converted pages."""
        return self.mediawiki_pages

    @staticmethod
    def page_to_subpage(names_path):
        """Return a new subpage name."""
        out = str(names_path[0])
        for name in names_path[1:]:
            out += f"/{name}"
        return out
