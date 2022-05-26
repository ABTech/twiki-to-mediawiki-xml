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
from re import MULTILINE, findall, sub
from shlex import split

logger = getLogger(__name__)


class TWikiParser():
    """Convert TWiki to JSON."""

    def __init__(self, twiki_data_web_path: str, out_path: str):
        """Initialize the TWiki convertor class."""
        self.twiki_data_web_path = twiki_data_web_path
        self.out_path = out_path

        self.twiki_txt_paths = []
        self.twiki_pages = []

    def run(self):
        """Run the conversion."""
        # Find all of the page files
        self.twiki_txt_paths = self.find_data_paths()

        # Convert metadata
        self.twiki_pages = []
        for twiki_txt_path in self.twiki_txt_paths:
            page_metadata = self.parse_metadata(twiki_txt_path)
            self.twiki_pages.append(page_metadata)

        return self.twiki_pages

    def find_data_paths(self):
        """Find TWiki data paths in input folder."""
        return glob(f'./{self.twiki_data_web_path}/*.txt')

    def parse_metadata(self, twiki_txt_path: str):
        """Parse TWiki data file metadata."""
        # Filename and topic name
        page = {
            "twiki_txt_path": twiki_txt_path,
            "twiki_page_name": splitext(basename(twiki_txt_path))[0]
        }

        # Check for revision file
        revision_path = f'{page["twiki_txt_path"]},v'
        if exists(revision_path):
            page["twiki_v_path"] = revision_path
        else:
            logger.warning('No revision file for %s', page["twiki_txt_path"])

        # Read page
        with open(page["twiki_txt_path"], "r", encoding="cp1252") as file_txt:
            page["twiki_txt"] = file_txt.read()

        # Read revision page
        if "twiki_v_path" in page:
            with open(page["twiki_v_path"], "r", encoding="cp1252") as file_v:
                page["twiki_v"] = file_v.read()

        # META vars
        topic_all_metas = {}
        topic_all_metas_strs = findall(r'^%META:(.*)\{(.*)\}%',
                                       page["twiki_txt"], flags=MULTILINE)
        for meta in topic_all_metas_strs:
            topic_all_metas[meta[0]] = (
                (topic_all_metas.get(meta[0], [])) + [meta[1]]
            )
        for meta, val in topic_all_metas.items():
            if meta == "TOPICINFO":
                page.update(self.parse_twiki_page_info(page, val))
            elif meta == "TOPICPARENT":
                page.update(self.parse_twiki_page_parent(page, val))
            elif meta == "FILEATTACHMENT":
                page.update(self.parse_twiki_page_attachments(page, val))
            elif meta == "TOPICMOVED":
                page.update(self.parse_twiki_page_moved(page, val))
            else:
                logger.warning(
                    'Unknown META %s found for %s', meta,
                    page["twiki_txt_path"])

        return page

    @staticmethod
    def parse_twiki_page_info(page: dict, topic_info_strs: str):
        """Parse TWiki TOPICINFO data."""
        out = {}
        topic_info = {}
        if len(topic_info_strs) > 1:
            logger.warning(
                'Multiple TOPICINFO found for %s, using first one',
                page["twiki_txt_path"])
        if len(topic_info_strs) == 0:
            logger.warning(
                'No TOPICINFO found for %s', page["twiki_txt_path"])
        else:
            out["twiki_topic_info_str"] = topic_info_strs[0]
            topic_info = TWikiParser.parse_twiki_object(
                out["twiki_topic_info_str"])
            if len(topic_info) > 0:
                out["twiki_topic_info"] = topic_info
            else:
                logger.warning(
                    'TOPICINFO empty for %s', page["twiki_txt_path"])
        return out

    @staticmethod
    def parse_twiki_page_parent(page: dict, topic_parent_strs: str):
        """Parse TWiki TOPICPARENT data."""
        out = {}
        topic_parent = {}
        if len(topic_parent_strs) > 1:
            logger.warning(
                'Multiple TOPICPARENT found for %s, using first one',
                page["twiki_txt_path"])
        if len(topic_parent_strs) > 0:
            out["twiki_topic_parent_str"] = topic_parent_strs[0]
            topic_parent = TWikiParser.parse_twiki_object(
                out["twiki_topic_parent_str"])
            if len(topic_parent) > 0:
                out["twiki_topic_parent"] = topic_parent
            else:
                logger.warning(
                    'TOPICPARENT present but empty for %s',
                    page["twiki_txt_path"])
        return out

    @staticmethod
    def parse_twiki_page_attachments(page: dict,
                                     topic_file_attachments_strs: str):
        """Parse TWiki FILEATTACHMENT data."""
        out = {}
        topic_file_attachments = []
        for file_attachment_str in topic_file_attachments_strs:
            file_attachment = TWikiParser.parse_twiki_object(
                file_attachment_str)
            if len(file_attachment) > 0:
                topic_file_attachments.append(file_attachment)
            else:
                logger.warning(
                    'A FILEATTACHMENT was empty for %s',
                    page["twiki_txt_path"])
        out["topic_file_attachments_strs"] = topic_file_attachments_strs
        out["topic_file_attachments"] = topic_file_attachments
        return out

    @staticmethod
    def parse_twiki_page_moved(page: dict,
                               topic_moved_strs: str):
        """Parse TWiki TOPICMOVED data."""
        out = {}
        topic_moved = []
        for moved_str in topic_moved_strs:
            moved = TWikiParser.parse_twiki_object(moved_str)
            if len(moved) > 0:
                topic_moved.append(moved)
            else:
                logger.warning(
                    'A TOPICMOVED was empty for %s',
                    page["twiki_txt_path"])
        out["topic_moved_strs"] = topic_moved_strs
        out["topic_moved"] = topic_moved
        return out

    @staticmethod
    def parse_twiki_object(twiki_object_str: str):
        """Parse a TWiki object string.

        In the form of: 'attr1="val1" attr2="val2" attr3="val3"'
        """
        twiki_object = {}
        # Split preserving spaces in quoted strings (note: \ will become \\)
        twiki_object_attr_strs = split(twiki_object_str, posix=True)
        for twiki_object_attr_str in twiki_object_attr_strs:
            # Split only first '=' to ensure no split in value string
            twiki_object_attr = twiki_object_attr_str.split('=', 1)
            twiki_object_attr_name = twiki_object_attr[0]
            # Strip only outer '""
            twiki_object_attr_val = sub(r'^\"(.*)\"$', r'\1',
                                        twiki_object_attr[1])
            twiki_object[twiki_object_attr_name] = twiki_object_attr_val
        return twiki_object
