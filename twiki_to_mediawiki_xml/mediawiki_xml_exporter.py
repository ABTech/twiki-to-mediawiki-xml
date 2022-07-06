"""
mediawiki_xml_exporter.py: Convert TWiki JSON to MediaWiki XML.

Created by Perry Naseck on 2022-05-28.
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

from datetime import datetime
# from hashlib import sha1
from json import load
from logging import getLogger
from re import sub
from typing import List, Tuple

from lxml.etree import Element, QName, SubElement, tostring  # nosec B410
from pkg_resources import parse_version

from twiki_to_mediawiki_xml import __version__

logger = getLogger(__name__)


# pylint: disable=too-many-instance-attributes
class MediaWikiXMLExporter():
    """Convert TWiki to JSON."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 mediawiki_json_path: str,
                 site_name: str,
                 db_name: str,
                 base_page_url: str,
                 namespace: int = 0,
                 migration_username: str = "TWiki_Migration",
                 migration_timestamp: datetime = None):
        """Initialize the MediaWiki exporter class."""
        self.mediawiki_json_path = mediawiki_json_path
        self.site_name = site_name
        self.db_name = db_name
        self.base_page_url = base_page_url
        self.namespace = namespace
        self.migration_username = migration_username
        if migration_timestamp is None:
            self.migration_timestamp = datetime.now()
        else:
            self.migration_timestamp = migration_timestamp

        self.mediawiki_json = None
        self.mediawiki_xml_root = None

    # pylint: disable=too-many-locals
    def run(self) -> None:
        """Run the conversion."""
        # Read JSON
        with open(self.mediawiki_json_path, "r", encoding="utf-8") as file_txt:
            self.mediawiki_json = load(file_txt)

        # Create XML root
        self.mediawiki_xml_root = self.generate_xml_root()

        # siteinfo section
        site_info = SubElement(self.mediawiki_xml_root, 'siteinfo')
        SubElement(site_info, 'sitename').text = self.site_name
        SubElement(site_info, 'dbname').text = self.db_name
        SubElement(site_info, 'base').text = self.base_page_url
        site_info_generator = SubElement(site_info, 'generator')
        site_info_generator.text = "twiki-to-mediawiki-xml"
        if __version__ is not None:
            site_info_generator.text += f" {__version__}"
        SubElement(site_info, 'case').text = "first-letter"

        # siteinfo namespaces section
        site_info_namespaces = SubElement(site_info, 'namspaces')
        namespaces_list = self.generate_default_namspaces_list(self.site_name)
        for namespace_item in namespaces_list:
            namespace = SubElement(
                site_info_namespaces,
                'namespace',
                attrib=namespace_item[0])
            if namespace_item[1] is not None:
                namespace.text = namespace_item[1]

        # pages
        rev_counter = 1
        page_counter = 1
        for page_in in self.mediawiki_json:
            page = self.generate_xml_page_header(
                self.mediawiki_xml_root,
                page_in["page_name"],
                self.namespace,
                page_counter
            )
            page_counter += 1

            # Assume latest revision matches text, so use latest revision data
            # instead of latest txt or TOPICINFO
            last_rev = None
            if "revisions" in page_in:
                new_revs, rev_counter, page_counter = (
                    self.convert_twiki_deltas_to_mw_revs(
                        page_in["revisions"]["deltas"],
                        self.mediawiki_xml_root, self.namespace,
                        page_in["page_name"],
                        self.mediawiki_json,
                        rev_counter,
                        page_counter))
                for rev in new_revs:
                    page.append(rev[0])
                last_rev = new_revs[-1][1]
            else:
                if ("TOPICINFO" not in page_in["metas"] or
                        len(page_in["metas"]["TOPICINFO"]) < 1):
                    logger.warning('Cannot convert %s without either '
                                   'revisions or TOPICINFO.',
                                   page_in["page_name"])
                    continue
                logger.warning('Using TOPICINFO for %s since no revisions.',
                               page_in["page_name"])
                if len(page_in["metas"]["TOPICINFO"]) > 1:
                    logger.warning('Page %s has multiple TOPICINFO, using '
                                   'first one.', page_in["page_name"])
                revision = self.convert_twiki_page_to_mw_rev(
                    page_in, rev_counter, None)
                rev_counter += 1
                last_rev = revision[1]
                page.append(revision[0])

            if "old_page_name" in page_in and last_rev is not None:
                old_name = page_in["old_page_name"]
                new_name = page_in["page_name"]
                rev_name, rev_counter, page_counter = (
                    self.convert_twiki_deltas_to_mw_move(
                        last_rev, old_name, new_name, self.mediawiki_xml_root,
                        self.namespace, self.migration_username,
                        self.migration_timestamp, rev_counter, page_counter))
                page.append(rev_name[0])

    def get_xml_str(self) -> str:
        """Get converted XML as string."""
        return tostring(
            self.mediawiki_xml_root,
            pretty_print=True,
            xml_declaration=False,
            encoding="utf-8"
        ).decode("utf-8")

    @staticmethod
    def generate_xml_root() -> Element:
        """Generate the MediaWiki XML root."""
        attr_qname_schema_location = QName(
            "http://www.w3.org/2001/XMLSchema-instance",
            "schemaLocation")
        attr_qname_lang = QName("http://www.w3.org/XML/1998/namespace", "lang")
        return Element(
            'mediawiki',
            nsmap={
                None: "http://www.mediawiki.org/xml/export-0.11/",
                "xsi": "http://www.w3.org/2001/XMLSchema-instance"
            },
            attrib={
                attr_qname_schema_location:
                    "http://www.mediawiki.org/xml/export-0.11/ "
                    "http://www.mediawiki.org/xml/export-0.11.xsd",
                "version": "0.11",
                attr_qname_lang: "en"
            }
        )

    @staticmethod
    def generate_xml_page_header(
            xml_root: Element,
            title: str,
            namespace: int,
            page_id: int) -> Element:
        """Generate the minimum elements for a page."""
        page = SubElement(xml_root, 'page')
        SubElement(page, 'title').text = title
        SubElement(page, 'ns').text = str(namespace)
        SubElement(page, 'id').text = str(page_id)
        return page

    @staticmethod
    def generate_default_namspaces_list(site_name: str) -> List[tuple]:
        """Generate list of default MediaWiki namespaces."""
        return [
            ({"key": "-2", "case": "first-letter"}, "Media"),
            ({"key": "-1", "case": "first-letter"}, "Special"),
            ({"key": "0", "case": "first-letter"}, None),
            ({"key": "1", "case": "first-letter"}, "Talk"),
            ({"key": "2", "case": "first-letter"}, "User"),
            ({"key": "3", "case": "first-letter"}, "User talk"),
            ({"key": "4", "case": "first-letter"}, site_name),
            ({"key": "5", "case": "first-letter"}, f"{site_name} talk"),
            ({"key": "6", "case": "first-letter"}, "File"),
            ({"key": "7", "case": "first-letter"}, "File talk"),
            ({"key": "8", "case": "first-letter"}, "MediaWiki"),
            ({"key": "9", "case": "first-letter"}, "MediaWiki talk"),
            ({"key": "10", "case": "first-letter"}, "Template"),
            ({"key": "11", "case": "first-letter"}, "Template talk"),
            ({"key": "12", "case": "first-letter"}, "Help"),
            ({"key": "13", "case": "first-letter"}, "Help talk"),
            ({"key": "14", "case": "first-letter"}, "Category"),
            ({"key": "15", "case": "first-letter"}, "Category talk"),
        ]

    @staticmethod
    def generate_mw_contributor(username: str = None,
                                user_id: int = None,
                                user_ip: str = None) -> Element:
        """Generate a MediaWiki contributor."""
        contributor = Element('contributor')
        if username is not None:
            SubElement(contributor, 'username').text = username.capitalize()
        if user_id is not None:
            SubElement(contributor, 'id').text = user_id
        if user_ip is not None:
            SubElement(contributor, 'ip').text = user_ip
        return contributor

    @staticmethod
    def generate_mw_rev(  # pylint: disable=too-many-arguments
            rev_id: int,
            timestamp: datetime,
            contributor: dict,
            text: str,
            parent_id: int = None,
            origin_id: int = None,
            minor: bool = False,
            comment: str = None) -> Tuple[Element, dict]:
        """Generate a MediaWiki revision."""
        revision = Element('revision')
        SubElement(revision, 'id').text = str(rev_id)
        if parent_id is not None:
            SubElement(revision, 'parentid').text = str(parent_id)
        timestamp_xml = f"{timestamp.isoformat()}Z"
        SubElement(revision, 'timestamp').text = timestamp_xml
        revision.append(
            MediaWikiXMLExporter.generate_mw_contributor(**contributor))
        if minor:
            SubElement(revision, 'minor')
        if comment is not None:
            SubElement(revision, 'comment').text = comment
        if origin_id is None:
            origin_id = rev_id
        SubElement(revision, 'origin').text = str(origin_id)
        SubElement(revision, 'model').text = "wikitext"
        SubElement(revision, 'format').text = "text/x-wiki"

        # text
        attr_qname_space = QName("http://www.w3.org/XML/1998/namespace",
                                 "space")
        text_filtered = sub('.\b', '', text)
        text_filtered = sub('\b+', '', text_filtered)
        text_encoded = text_filtered.encode('utf-8')
        # sha1_hash = sha1(text_encoded).hexdigest()
        SubElement(revision, 'text', attrib={
            "bytes": str(len(text_encoded)),
            # "sha1": sha1_hash,
            attr_qname_space: "preserve"
        }).text = text_filtered
        # SubElement(revision, 'sha1').text = sha1_hash
        return (revision, {
            "rev_id": rev_id,
            "timestamp": timestamp,
            "contributor": contributor,
            "text": text,
            "parent_id": parent_id,
            "origin_id": origin_id
        })

    @staticmethod
    def convert_twiki_rev_to_mw_rev(twiki_revision: dict, rev_id: int,
                                    parent_id: int = None
                                    ) -> Tuple[Element, dict]:
        """Convert a TWiki revision to a MediaWiki revision."""
        timestamp = (
            MediaWikiXMLExporter.parse_twiki_delta_date(twiki_revision["date"])
        )
        return MediaWikiXMLExporter.generate_mw_rev(
            rev_id,
            # datetime.utcfromtimestamp(int(twiki_revision["date"])),
            timestamp,
            {"username": twiki_revision["author"]},
            twiki_revision["text"],
            parent_id
        )

    @staticmethod
    def convert_twiki_page_to_mw_rev(twiki_page: dict, rev_id: int,
                                     parent_id: int = None
                                     ) -> Tuple[Element, dict]:
        """Convert a TWiki page to a MediaWiki revision."""
        twiki_date = twiki_page["metas"]["TOPICINFO"][0]["date"]
        twiki_author = twiki_page["metas"]["TOPICINFO"][0]["author"]
        return MediaWikiXMLExporter.generate_mw_rev(
            rev_id,
            datetime.utcfromtimestamp(int(twiki_date)),
            {"username": twiki_author},
            twiki_page["twiki_txt"],
            parent_id
        )

    @staticmethod
    # pylint: disable=too-many-arguments
    def convert_twiki_deltas_to_mw_revs(
            deltas: List[dict],
            mediawiki_xml_root: dict,
            namespace: int,
            new_page_name: str,
            all_pages: list,
            rev_counter: int,
            page_counter: int
    ) -> Tuple[List[Tuple[Element, dict]], int, int]:
        """Convert TWiki deltas to MediaWiki revisions."""
        out = []
        deltas_sorted = sorted(
            deltas,
            key=lambda rev: parse_version(rev['revision']))
        revision_mapping = {}
        moves_handled = []
        last_rev = None
        for delta in deltas_sorted:
            parent_id = None
            if delta["next"] != "":
                parent_id = revision_mapping[delta["next"]]

            revision = MediaWikiXMLExporter.convert_twiki_rev_to_mw_rev(
                delta, rev_counter, parent_id)
            last_rev = revision[1]
            revision_mapping[delta["revision"]] = rev_counter
            rev_counter += 1
            out.append(revision)

            if "TOPICMOVED" in delta["metas"]:
                for meta_moved in delta["metas"]["TOPICMOVED"]:
                    move_date_int = int(meta_moved["date"])
                    if move_date_int not in moves_handled:
                        move_timestamp = (
                            datetime.utcfromtimestamp(move_date_int))
                        old_name = meta_moved["from"].split(".")[1]
                        new_name = meta_moved["to"].split(".")[1]
                        username = meta_moved["by"]
                        moves_handled.append(move_date_int)
                        if old_name == new_name:
                            logger.warning("Ignoring move between wikis, %s "
                                           "(%s)", new_name, new_page_name)
                            continue
                        if any(page['page_name'] == old_name for page in
                               all_pages):
                            logger.warning("Ignoring move from %s to %s "
                                           "because old name exists as page "
                                           "(%s)",
                                           old_name, new_name, new_page_name)
                            continue
                        rev_name, rev_counter, page_counter = (
                            MediaWikiXMLExporter.convert_twiki_deltas_to_mw_move(  # noqa: E501
                                last_rev, old_name, new_page_name,
                                mediawiki_xml_root, namespace, username,
                                move_timestamp, rev_counter, page_counter))
                        out.append(rev_name)
                        revision_mapping[delta["revision"]] = (
                            rev_name[1]["rev_id"])
        return (out, rev_counter, page_counter)

    @staticmethod
    # pylint: disable=too-many-arguments
    def convert_mw_rev_to_mw_rev_renamed(
            last_rev: Element,
            old_name: str,
            new_name: str,
            rev_counter: int,
            username: str,
            timestamp: datetime
    ) -> Tuple[Tuple[Element, dict], Tuple[Element, dict]]:
        """Convert MediaWiki rev to MediaWiki renamed revision."""
        contributor = {"username": username}
        text = last_rev["text"]
        parent_id = last_rev["rev_id"]
        origin_id = last_rev["rev_id"]
        redirect_text = f"#REDIRECT [[{new_name}]]"
        comment = (
            f"{username} moved page [[{old_name}]] to [[{new_name}]]"
        )
        return (MediaWikiXMLExporter.generate_mw_rev(
            rev_counter,
            timestamp,
            contributor,
            text,
            parent_id=parent_id,
            origin_id=origin_id,
            minor=True,
            comment=comment
        ), MediaWikiXMLExporter.generate_mw_rev(
            rev_counter + 1,
            timestamp,
            contributor,
            redirect_text,
            minor=True,
            comment=comment
        ))

    @staticmethod
    # pylint: disable=too-many-arguments
    def convert_twiki_deltas_to_mw_move(
            last_rev: dict,
            old_name: str,
            new_name: str,
            mediawiki_xml_root: Element,
            namespace: int,
            username: str,
            timestamp: datetime,
            rev_counter: int,
            page_counter: int) -> Tuple[Tuple[Element, dict], int, int]:
        """Convert a delta to a move revision and redirect page."""
        rev_name = MediaWikiXMLExporter.convert_mw_rev_to_mw_rev_renamed(
            last_rev, old_name, new_name, rev_counter,
            username, timestamp
        )
        rev_counter += 2
        redir_page = MediaWikiXMLExporter.generate_xml_page_header(
            mediawiki_xml_root,
            old_name,
            namespace,
            page_counter
        )
        page_counter += 1
        SubElement(redir_page, 'redirect', attrib={
            "title": new_name
        })
        redir_page.append(rev_name[1][0])
        return (rev_name[0], rev_counter, page_counter)

    @staticmethod
    def parse_twiki_delta_date(date: str) -> datetime:
        """Parse a TWiki delta date.

        Takes dates in the form YYYY.MM.DD.HH.MM.SS or YY.MM.DD.HH.MM.SS.
        """
        timestamp = None
        if int(date.split(".")[0]) < 101:
            timestamp = datetime.strptime(date, "%y.%m.%d.%H.%M.%S")
        else:
            timestamp = datetime.strptime(date, "%Y.%m.%d.%H.%M.%S")
        return timestamp
