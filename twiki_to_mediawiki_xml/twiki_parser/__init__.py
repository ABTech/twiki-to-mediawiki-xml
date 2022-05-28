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
from subprocess import check_output  # nosec B404
from typing import Sequence

from editrcs import ParseRcs

SKIP_REVISIONS_DEFAULT = ("SiteStatistics", "UserListHeader", "WebLeftBar",
                          "WebStatistics")
CO_PATH_DEFAULT = "/usr/bin/co"

logger = getLogger(__name__)


class TWikiParser():
    """Convert TWiki to JSON."""

    def __init__(self,
                 twiki_data_web_path: str,
                 out_path: str,
                 skip_revisions: Sequence[str] = SKIP_REVISIONS_DEFAULT,
                 co_path: str = CO_PATH_DEFAULT):
        """Initialize the TWiki convertor class."""
        self.twiki_data_web_path = twiki_data_web_path
        self.out_path = out_path
        self.skip_revisions = skip_revisions
        self.co_path = co_path

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
            "page_name": splitext(basename(twiki_txt_path))[0]
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

        # Process METAs
        page["meta_strs"] = self.find_twiki_meta_strs(page["twiki_txt"])
        page["metas"] = self.parse_twiki_meta_strs(page["meta_strs"])

        # Some checks for METAs
        self.check_metas(page["page_name"], page["metas"])

        if "twiki_v" in page and page["page_name"] in self.skip_revisions:
            logger.warning("Skipping revisions for %s", page["page_name"])
        elif "twiki_v" in page:
            page["revisions"] = self.parse_twiki_revisions(
                page["twiki_v"],
                page["twiki_v_path"],
                self.co_path)

            # Some checks for revisions
            self.check_revisions(page["page_name"], page["revisions"],
                                 page["twiki_txt"])

        return page

    @staticmethod
    def find_twiki_meta_strs(twiki_txt: dict):
        """Find TWiki META data on a page."""
        topic_metas_strs = {}
        topic_metas_strs_list = findall(r'^%META:(.*)\{(.*)\}%',
                                        twiki_txt, flags=MULTILINE)
        for meta_str_list in topic_metas_strs_list:
            topic_metas_strs[meta_str_list[0]] = (
                topic_metas_strs.get(meta_str_list[0], []) +
                [meta_str_list[1]]
            )
        return topic_metas_strs

    @staticmethod
    def parse_twiki_meta_strs(metas_strs: dict):
        """Parse TWiki META data from an object of strings."""
        metas = {}
        for meta_name, val in metas_strs.items():
            metas[meta_name] = TWikiParser.parse_twiki_meta_str(meta_name, val)
        return metas

    @staticmethod
    def parse_twiki_meta_str(meta: str, meta_strs: Sequence[str]):
        """Parse TWiki META data from string."""
        all_meta = []
        for meta_str in meta_strs:
            meta = TWikiParser.parse_twiki_object(meta_str)
            all_meta.append(meta)
        return all_meta

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

    @staticmethod
    def check_metas(page_name: str, metas: dict, rev: str = None):
        """Check parsed TWiki META data."""
        if "TOPICINFO" not in metas:
            logger.warning(
                'META TOPICINFO missing for %s rev %s', page_name, rev)
        elif len(metas["TOPICINFO"]) > 1:
            logger.warning(
                'Multiple META TOPICINFO for %s rev %s', page_name, rev)
        for meta, vals in metas.items():
            for val in vals:
                if len(val) == 0:
                    logger.warning('A META %s is empty for %s rev %s',
                                   meta, page_name, rev)

    @staticmethod
    def parse_twiki_revisions(
            twiki_v: str,
            twiki_v_path: str,
            co_path: str = CO_PATH_DEFAULT):
        """Parse TWiki revisions."""
        rcs = ParseRcs(twiki_v)
        deltas = []
        revisions = {
            "head": rcs.getHead(),
            "branch": rcs.getBranch(),
            "access": rcs.getAccess(),
            "symbols": rcs.getSymbols(),
            "locks": rcs.getLocks(),
            "comment": rcs.getComment(),
            "desc": rcs.getDesc(),
            "rcs_string": rcs.toString(),
            "deltas": [],
        }
        rcs.mapDeltas(deltas.append)
        for delta in deltas:
            revision = {
                "revision": delta.getRevision(),
                "commit_id": delta.getCommitId(),
                "date": delta.getDate(),
                "author": delta.getAuthor(),
                "state": delta.getState(),
                "branches": delta.getBranches(),
                "next": delta.getNext(),  # Previous for trunks
                "log": delta.getLog(),
                "delta_string": delta.deltaToString(),
                "delta_text_string": delta.deltaTextToString(),
            }
            revisions["deltas"].append(revision)
        # textFromDiff and textToDiff from editrcs error, so we use co
        for revision in revisions["deltas"]:
            rev, path = revision["revision"], twiki_v_path
            cmd = [co_path, "-q", f"-p{rev}", path]
            revision["text"] = check_output(cmd, text=True,  # nosec B603
                                            encoding="cp1252")
            revision["meta_strs"] = TWikiParser.find_twiki_meta_strs(
                revision["text"])
            revision["metas"] = TWikiParser.parse_twiki_meta_strs(
                revision["meta_strs"])
        return revisions

    @staticmethod
    def check_revisions(page_name: str, revisions: dict, twiki_txt: str):
        """Check parsed revision TWiki data."""
        # Check head is not on branch
        if revisions["branch"] is not None:
            logger.warning(
                'Revisions on branch for %s', page_name)

        # Some checks for revisions
        for i, revision in enumerate(revisions["deltas"]):
            # Check METAs
            TWikiParser.check_metas(page_name, revision["metas"],
                                    rev=revision["revision"])

            # Check latest revision matches txt
            if revisions["head"] == revision["revision"]:
                if twiki_txt != revision["text"]:
                    logger.warning(
                        'Head rev (%s) not equal to current data for %s',
                        revision["revision"], page_name)

            # Check for current branch
            if len(revision["branches"]) > 0:
                logger.warning(
                    'Revision %s has branches for %s',
                    revision["revision"],
                    page_name)

            # Check for duplicates
            for j, revision2 in enumerate(revisions["deltas"]):
                if (i != j and
                        revision["revision"] == revision2["revision"]):
                    logger.warning(
                        'Duplicate revision %s for %s',
                        revision["revision"],
                        page_name)
