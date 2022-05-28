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

from logging import getLogger

from lxml.etree import Element, QName, SubElement, tostring  # nosec B410

from twiki_to_mediawiki_xml import __version__

logger = getLogger(__name__)


class MediaWikiXMLExporter():
    """Convert TWiki to JSON."""

    def __init__(self,
                 twiki_json_path: str,
                 site_name: str,
                 db_name: str,
                 base_page_url: str):
        """Initialize the MediaWiki exporter class."""
        self.twiki_json_path = twiki_json_path
        self.site_name = site_name
        self.db_name = db_name
        self.base_page_url = base_page_url

        self.mediawiki_xml_root = None

    def run(self) -> None:
        """Run the conversion."""
        # Create XML root
        self.mediawiki_xml_root = self.generate_xml_root()

        # siteinfo section
        site_info = SubElement(self.mediawiki_xml_root, 'siteinfo')
        site_info_site_name = SubElement(site_info, 'sitename')
        site_info_site_name.text = self.site_name
        site_info_db_name = SubElement(site_info, 'dbname')
        site_info_db_name.text = self.db_name
        site_info_base = SubElement(site_info, 'base')
        site_info_base.text = self.base_page_url
        site_info_generator = SubElement(site_info, 'generator')
        site_info_generator.text = "twiki-to-mediawiki-xml"
        if __version__ is not None:
            site_info_generator.text += f" {__version__}"
        site_info_case = SubElement(site_info, 'case')
        site_info_case.text = "first-letter"

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
    def generate_default_namspaces_list(site_name: str) -> list[tuple]:
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
