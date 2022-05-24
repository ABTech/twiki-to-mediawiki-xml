"""
replace_rules.py: In-place text replacement from TWiki to MediaWiki Formats.

Created by Perry Naseck on 2022-05-22.
This file is part of the https://github.com/ABTech/twiki-to-mediawiki-xml

Copyright (C) 2022-present  AB Tech, Carnegie Mellon University
Copyright (C) 2022          Perry Naseck (git@perrynaseck.com)
Copyright (C) 2011-2016     Ryan Castillo

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

# Many of the regex rules in this file come from Ryan Castillo's Perl
# script:
# https://github.com/rmcastil/Twiki-to-Mediawiki/blob/f236827dd1795ee400186a19a4f11a248a949874/twiki2mediawiki.pl

# This is just a start... this file should probably get split into a whole
# bunch of functions/class methods that handle in-place substitutions only
# and the metadata and loading/saving should be somewhere else. -pnaseck

# A bunch of these regex from the original Perl code had flags that weren't
# obvious how they translate to Python (I don't know PCRE). These should be
# tested. -pnaseck

from re import sub


def text_formatting(to_convert: str):
    """Convert TWiki page content to Wikitext."""
    # pylint: disable=line-too-long

    out = to_convert

    # LatexModePlugin -> Extension:Math
    out = sub(r'%\$(.*?)\$%', r"<math>$1<\/math>", out)

    # DirectedGraphPlugin -> Extension:GraphViz
    out = sub(r'<(\/?)dot>', r"<$1graphviz>", out)

    # <verbatim>
    out = sub(r'<(\/?)verbatim>', r"<$1pre>", out)

    # Anchors
    out = sub(r'^\s*#(\S+)\s*$', r'<div id="<nop>$1"><\/div>', out)  # replace anchors with empty div's  # noqa: E501

    # Interwikis
    # q#s/\[\[$iwSitePattern:$iwPagePattern\]\]/makeLink("$1:$2")/ge#,
    # q#s/\[\[$iwSitePattern:$iwPagePattern\]\[([^\]]+)\]\]/makeLink("$1:$2",$3)/ge#,  # noqa: E501
    # q#s/(?:^|(?<=[\s\-\*\(]))$iwSitePattern:$iwPagePattern(?=[\s\.\,\;\:\!\?\)\|]*(?:\s|$))/makeInterwikiLink($1,$2)/ge#,  # noqa: E501

    # Links
    # out = sub(r'\[\[(https?\:.*?)\]\[(.*?)\]\]', r"makeLink($1,$2)", out)  # [[http(s):...][label]]  # noqa: E501
    # out = sub(r'\[\[(ftp\:.*?)\]\[(.*?)\]\]', r"makeLink($1,$2)", out)  # [[ftp:...][label]]  # noqa: E501
    # out = sub(r'\[\[([^\]<>]*)\]\]', r"makeLink(makeWikiWord($1),$1)", out)  # [[link]]  # noqa: E501
    # out = sub(r'\[\[([^\]<>]*)\]\[(.*?)\]\]', r"makeLink(makeWikiWord($1),$2)", out)  # [[link][text]]  # noqa: E501
    # out = sub(r'<a.*?href="(.*?)".*?>\s*(.*?)\s*<\/a>', r"makeLink($1,$2)", out)  # <a href="...">...</a>  # noqa: E501

    # WikiWords
    # out = sub(r'$web\.([A-Z][${man}]*)', r"makeLink($1)", out)  # $web.WikiWord -> link  # noqa: E501
    # out = sub(r'([A-Z][${man}]*)\.($wwPattern)', r"<nop>$1.<nop>$2", out)  # OtherWebName.WikiWord -> <nop>OtherWebName.<nop>WikiWord  # noqa: E501
    out = sub(r'<nop>([A-Z]{1}\w+?[A-Z]{1})', r"!$1", out)  # change <nop> to ! in front of Twiki words.  # noqa: E501
    # out = sub(r'(?:^|(?<=[\s\(]))($wwPattern)', r"makeLink($1,spaceWikiWord($1))", out)  # WikiWord -> link  # noqa: E501
    out = sub(r'!([A-Z]{1}\w+?[A-Z]{1})', r"$1", out)  # remove ! in front of Twiki words.  # noqa: E501
    out = sub(r'<nop>', r"", out)  # remove <nop>

    # Images (attachments only) and links wrapped around images
    out = sub(r'<img .*?src="Media:(.+?)".*?\/>', r"[[File:$1]]", out)  # inline images  # noqa: E501
    out = sub(r'\[\[\s*(.+?)\s*\|\s*\[\[File:(.*?)\]\]\s*\]\]', r"[[File:$2|link=$1]]", out)  # external links around images  # noqa: E501
    out = sub(r'\[\s*(.+?)\s+\[\[File:(.*?)\]\]\s*\]', r"[[File:$2|link=$1]]", out)  # internal links around images  # noqa: E501

    # Formatting
    out = sub(r'(^|[\s\(])\*(\S+?|\S[^\n]*?\S)\*($|(?=[\s\)\.\,\:\;\!\?]))', r"\1'''\2'''", out)  # bold  # noqa: E501
    out = sub(r'(^|[\s\(])\_\_(\S+?|\S[^\n]*?\S)\_\_($|(?=[\s\)\.\,\:\;\!\?]))', r"\1'''''\2'''''", out)  # italic bold  # noqa: E501
    out = sub(r'(^|[\s\(])\_(\S+?|\S[^\n]*?\S)\_($|(?=[\s\)\.\,\:\;\!\?]))', r"\1''\2''", out)  # italic  # noqa: E501
    out = sub(r'/(^|[\s\(])==(\S+?|\S[^\n]*?\S)==($|(?=[\s\)\.\,\:\;\!\?]))', r"1'''<tt>\2<\/tt>'''", out)  # monospaced bold  # noqa: E501
    out = sub(r'/(^|[\s\(])=(\S+?|\S[^\n]*?\S)=($|(?=[\s\)\.\,\:\;\!\?]))', r"\1<tt>\2<\/tt>", out)  # monospaced  # noqa: E501
    out = sub(r'/(^|[\n\r])---\+\+\+\+\+\+([^\n\r]*)', r"\1======\2 ======", out)  # H6  # noqa: E501
    out = sub(r'/(^|[\n\r])---\+\+\+\+\+([^\n\r]*)', r"\1=====\2 =====", out)  # H5  # noqa: E501
    out = sub(r'/(^|[\n\r])---\+\+\+\+([^\n\r]*)', r"\1====\2 ====", out)  # H4
    out = sub(r'/(^|[\n\r])---\+\+\+([^\n\r]*)', r"\1===\2 ===", out)  # H3
    out = sub(r'/(^|[\n\r])---\+\+([^\n\r]*)', r"\1==\2 ==", out)  # H2
    out = sub(r'/(^|[\n\r])---\+([^\n\r]*)', r"\1=\2 =", out)  # H1

    # Bullets
    out = sub(r'(^|[\n\r])[ ]{3}\* ', r"$1\* ", out)  # level 1 bullet
    out = sub(r'(^|[\n\r])[\t]{1}\* ', r"$1\* ", out)  # level 1 bullet: Handle single tabs (from twiki .txt files)  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{6}\* ', r"$1\*\* ", out)  # level 2 bullet
    out = sub(r'(^|[\n\r])[\t]{2}\* ', r"$1\*\* ", out)  # level 1 bullet: Handle double tabs  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{9}\* ', r"$1\*\*\* ", out)  # level 3 bullet
    out = sub(r'(^|[\n\r])[\t]{3}\* ', r"$1\*\*\* ", out)  # level 3 bullet: Handle tabbed version  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{12}\* ', r"$1\*\*\*\* ", out)  # level 4 bullet
    out = sub(r'(^|[\n\r])[ ]{15}\* ', r"$1\*\*\*\*\* ", out)  # level 5 bullet
    out = sub(r'(^|[\n\r])[ ]{18}\* ', r"$1\*\*\*\*\*\* ", out)  # level 6 bullet  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{21}\* ', r"$1\*\*\*\*\*\*\* ", out)  # level 7 bullet  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{24}\* ', r"$1\*\*\*\*\*\*\*\* ", out)  # level 8 bullet  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{27}\* ', r"$1\*\*\*\*\*\*\*\*\* ", out)  # level 9 bullet  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{30}\* ', r"$1\*\*\*\*\*\*\*\*\*\* ", out)  # level 10 bullet  # noqa: E501

    # Numbering
    out = sub(r'(^|[\n\r])[ ]{3}[0-9]\.? ', r"$1\# ", out)  # level 1 bullet
    out = sub(r'(^|[\n\r])[\t]{1}[0-9]\.? ', r"$1\# ", out)  # level 1 bullet: handle 1 tab  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{6}[0-9]\.? ', r"$1\#\# ", out)  # level 2 bullet
    out = sub(r'(^|[\n\r])[\t]{2}[0-9]\.? ', r"$1\#\# ", out)  # level 2 bullet: handle 2 tabs  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{9}[0-9]\.? ', r"$1\#\#\# ", out)  # level 3 bullet  # noqa: E501
    out = sub(r'(^|[\n\r])[\t]{3}[0-9]\.? ', r"$1\#\#\# ", out)  # level 3 bullet: handle 3 tabs  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{12}[0-9]\.? ', r"$1\#\#\#\# ", out)  # level 4 bullet  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{15}[0-9]\.? ', r"$1\#\#\#\#\# ", out)  # level 5 bullet  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{18}[0-9]\.? ', r"$1\#\#\#\#\#\# ", out)  # level 6 bullet  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{21}[0-9]\.? ', r"$1\#\#\#\#\#\#\# ", out)  # level 7 bullet  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{24}[0-9]\.? ', r"$1\#\#\#\#\#\#\#\# ", out)  # level 8 bullet  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{27}[0-9]\.? ', r"$1\#\#\#\#\#\#\#\#\# ", out)  # level 9 bullet  # noqa: E501
    out = sub(r'(^|[\n\r])[ ]{30}[0-9]\.? ', r"$1\#\#\#\#\#\#\#\#\#\# ", out)  # level 10 bullet  # noqa: E501

    # Definitions
    # There must be a better MW convention
    out = sub(r'(^|[\n\r])[ ]{3}\$ ([^\:]*)', r"$1\; $2 ", out)  # $ definition: term  # noqa: E501

    # Lookup variable
    # q#s/%$varPattern%/getTwikiVar($1,'')/ge#,
    # q#s/%$varPattern(\{.*?\})%/getTwikiVar($1,$2)/ge#

    return out


# pylint: disable=line-too-long
TEST = "This is normal.<br /><br />This is a new paragraph.<br /><br />This text is normal. *This text is bolded.* _This text is italicized. *This text is both.* *This text is also both.**_ <u>This text is underlined. *This text is bold & underlined. <i>This text is ital and underlined. <b>This is all three!</b></i></u><br /><br /><br /><b>This is bold</b><br /><br /><b>This is still bold.</b><br /><br /><br />OK"  # noqa: E501
print(text_formatting(TEST))
