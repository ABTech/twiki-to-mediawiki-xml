"""
__init__.py: Convert TWiki JSON to MediaWiki XML.

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
from typing import List

from lxml.etree import Element, QName, SubElement, tostring  # nosec B410
from pkg_resources import parse_version

from twiki_to_mediawiki_xml import __version__

logger = getLogger(__name__)


class MediaWikiXMLExporter():
    """Convert TWiki to JSON."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 mediawiki_json_path: str,
                 site_name: str,
                 db_name: str,
                 base_page_url: str,
                 namespace: int = 0):
        """Initialize the MediaWiki exporter class."""
        self.mediawiki_json_path = mediawiki_json_path
        self.site_name = site_name
        self.db_name = db_name
        self.base_page_url = base_page_url
        self.namespace = namespace

        self.mediawiki_json = None
        self.mediawiki_xml_root = None

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
        for page_i, page_in in enumerate(self.mediawiki_json):
            page = SubElement(self.mediawiki_xml_root, 'page')
            SubElement(page, 'title').text = page_in["page_name"]
            SubElement(page, 'ns').text = str(self.namespace)
            SubElement(page, 'id').text = str(page_i + 1)

            # Assume latest revision matches text, so use latest revision data
            # instead of latest txt or TOPICINFO
            if "revisions" in page_in:
                new_revs = self.convert_twiki_deltas_to_mediawiki_revs(
                    page_in["revisions"]["deltas"], rev_counter)
                for rev in new_revs:
                    page.append(rev)
                rev_counter += len(new_revs)
            else:
                if ("TOPICINFO" not in page_in["metas"] or
                        len(page_in["metas"]["TOPICINFO"]) < 1):
                    logger.warning('Cannot convert %s without either '
                                   'revisions or TOPICINFO.',
                                   page_in["page_name"])
                    continue
                if len(page_in["metas"]["TOPICINFO"]) > 1:
                    logger.warning('Page %s has multiple TOPICINFO, using '
                                   'first one.', page_in["page_name"])
                revision = self.convert_twiki_page_to_mediawiki_rev(
                    page_in, rev_counter, None)
                rev_counter += 1
                page.append(revision)

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
    def generate_mediawiki_contributor(username: str = None,
                                       user_id: int = None,
                                       user_ip: str = None) -> Element:
        """Generate a MediaWiki contributor."""
        contributor = Element('contributor')
        if username is not None:
            SubElement(contributor, 'username').text = username
        if user_id is not None:
            SubElement(contributor, 'id').text = user_id
        if user_ip is not None:
            SubElement(contributor, 'ip').text = user_ip
        return contributor

    @staticmethod
    def generate_mediawiki_rev(  # pylint: disable=too-many-arguments
            rev_id: int,
            timestamp: datetime,
            contributor: dict,
            text: str,
            parent_id: int = None,
            origin_id: int = None,
            ) -> Element:
        """Generate a MediaWiki revision."""
        revision = Element('revision')
        SubElement(revision, 'id').text = str(rev_id)
        if parent_id is not None:
            SubElement(revision, 'parentid').text = str(parent_id)
        timestamp_xml = f"{timestamp.isoformat()}Z"
        SubElement(revision, 'timestamp').text = timestamp_xml
        revision.append(
            MediaWikiXMLExporter.generate_mediawiki_contributor(**contributor))
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
        return revision

    @staticmethod
    def convert_twiki_rev_to_mediawiki_rev(twiki_revision: dict, rev_id: int,
                                           parent_id: int = None) -> Element:
        """Convert a TWiki revision to a MediaWiki revision."""
        timestamp = None
        if int(twiki_revision["date"].split(".")[0]) < 101:
            timestamp = datetime.strptime(twiki_revision["date"],
                                          "%y.%m.%d.%H.%M.%S")
        else:
            timestamp = datetime.strptime(twiki_revision["date"],
                                          "%Y.%m.%d.%H.%M.%S")
        return MediaWikiXMLExporter.generate_mediawiki_rev(
            rev_id,
            # datetime.utcfromtimestamp(int(twiki_revision["date"])),
            timestamp,
            {"username": twiki_revision["author"]},
            twiki_revision["text"],
            parent_id
        )

    @staticmethod
    def convert_twiki_page_to_mediawiki_rev(twiki_page: dict, rev_id: int,
                                            parent_id: int = None) -> Element:
        """Convert a TWiki page to a MediaWiki revision."""
        twiki_date = twiki_page["metas"]["TOPICINFO"][0]["date"]
        twiki_author = twiki_page["metas"]["TOPICINFO"][0]["author"]
        return MediaWikiXMLExporter.generate_mediawiki_rev(
            rev_id,
            datetime.utcfromtimestamp(int(twiki_date)),
            {"username": twiki_author},
            twiki_page["twiki_txt"],
            parent_id
        )

    @staticmethod
    def convert_twiki_deltas_to_mediawiki_revs(
            deltas: List[dict],
            rev_counter: int) -> List[Element]:
        """Convert TWiki deltas to MediaWiki revisions."""
        out = []
        deltas_sorted = sorted(
            deltas,
            key=lambda rev: parse_version(rev['revision']))
        revision_mapping = {}
        for delta in deltas_sorted:
            parent_id = None
            if delta["next"] != "":
                parent_id = revision_mapping[delta["next"]]
            revision = MediaWikiXMLExporter.convert_twiki_rev_to_mediawiki_rev(
                delta, rev_counter, parent_id)
            revision_mapping[delta["revision"]] = rev_counter
            rev_counter += 1
            out.append(revision)
        return out
