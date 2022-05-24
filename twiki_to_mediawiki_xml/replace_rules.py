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

"""
Many of the regex rules in this file come from Ryan Castillo's Perl
script:
https://github.com/rmcastil/Twiki-to-Mediawiki/blob/f236827dd1795ee400186a19a4f11a248a949874/twiki2mediawiki.pl
"""

# This is just a start... this file should probably get split into a whole
# bunch of functions/class methods that handle in-place substitutions only
# and the metadata and loading/saving should be somewhere else. -pnaseck

# A bunch of these regex from the original Perl code had flags that weren't
# obvious how they translate to Python (I don't know PCRE). These should be
# tested. -pnaseck

from re import sub

def text_formatting(to_convert: str):
    out = to_convert

    # LatexModePlugin -> Extension:Math
    to_convert = sub(r'%\$(.*?)\$%', r"<math>$1<\/math>", to_convert)

    # DirectedGraphPlugin -> Extension:GraphViz
    to_convert = sub(r'<(\/?)dot>', r"<$1graphviz>", to_convert)

    # <verbatim>
    to_convert = sub(r'<(\/?)verbatim>', r"<$1pre>", to_convert)

    # Anchors
    to_convert = sub(r'^\s*#(\S+)\s*$', r'<div id="<nop>$1"><\/div>', to_convert)  # replace anchors with empty div's

    # Interwikis
    # q#s/\[\[$iwSitePattern:$iwPagePattern\]\]/makeLink("$1:$2")/ge#,
    # q#s/\[\[$iwSitePattern:$iwPagePattern\]\[([^\]]+)\]\]/makeLink("$1:$2",$3)/ge#,
    # q#s/(?:^|(?<=[\s\-\*\(]))$iwSitePattern:$iwPagePattern(?=[\s\.\,\;\:\!\?\)\|]*(?:\s|$))/makeInterwikiLink($1,$2)/ge#,

    # Links
    # to_convert = sub(r'\[\[(https?\:.*?)\]\[(.*?)\]\]', r"makeLink($1,$2)", to_convert)  # [[http(s):...][label]]
    # to_convert = sub(r'\[\[(ftp\:.*?)\]\[(.*?)\]\]', r"makeLink($1,$2)", to_convert)  # [[ftp:...][label]]
    # to_convert = sub(r'\[\[([^\]<>]*)\]\]', r"makeLink(makeWikiWord($1),$1)", to_convert)  # [[link]]
    # to_convert = sub(r'\[\[([^\]<>]*)\]\[(.*?)\]\]', r"makeLink(makeWikiWord($1),$2)", to_convert)  # [[link][text]]
    # to_convert = sub(r'<a.*?href="(.*?)".*?>\s*(.*?)\s*<\/a>', r"makeLink($1,$2)", to_convert)  # <a href="...">...</a>

    # WikiWords
    # to_convert = sub(r'$web\.([A-Z][${man}]*)', r"makeLink($1)", to_convert)  # $web.WikiWord -> link
    # to_convert = sub(r'([A-Z][${man}]*)\.($wwPattern)', r"<nop>$1.<nop>$2", to_convert)  # OtherWebName.WikiWord -> <nop>OtherWebName.<nop>WikiWord
    to_convert = sub(r'<nop>([A-Z]{1}\w+?[A-Z]{1})', r"!$1", to_convert)  # change <nop> to ! in front of Twiki words.
    # to_convert = sub(r'(?:^|(?<=[\s\(]))($wwPattern)', r"makeLink($1,spaceWikiWord($1))", to_convert)  # WikiWord -> link
    to_convert = sub(r'!([A-Z]{1}\w+?[A-Z]{1})', r"$1", to_convert)  # remove ! in front of Twiki words.
    to_convert = sub(r'<nop>', r"", to_convert)  # remove <nop>

    # Images (attachments only) and links wrapped around images
    to_convert = sub(r'<img .*?src="Media:(.+?)".*?\/>', r"[[File:$1]]", to_convert)  # inline images
    to_convert = sub(r'\[\[\s*(.+?)\s*\|\s*\[\[File:(.*?)\]\]\s*\]\]', r"[[File:$2|link=$1]]", to_convert)  # external links around images
    to_convert = sub(r'\[\s*(.+?)\s+\[\[File:(.*?)\]\]\s*\]', r"[[File:$2|link=$1]]", to_convert)  # internal links around images

    # Formatting
    to_convert = sub(r'(^|[\s\(])\*(\S+?|\S[^\n]*?\S)\*($|(?=[\s\)\.\,\:\;\!\?]))', r"\1'''\2'''", to_convert)  # bold
    to_convert = sub(r'(^|[\s\(])\_\_(\S+?|\S[^\n]*?\S)\_\_($|(?=[\s\)\.\,\:\;\!\?]))', r"\1'''''\2'''''", to_convert)  # italic bold
    to_convert = sub(r'(^|[\s\(])\_(\S+?|\S[^\n]*?\S)\_($|(?=[\s\)\.\,\:\;\!\?]))', r"\1''\2''", to_convert)  # italic
    to_convert = sub(r'/(^|[\s\(])==(\S+?|\S[^\n]*?\S)==($|(?=[\s\)\.\,\:\;\!\?]))', r"1'''<tt>\2<\/tt>'''", to_convert)  # monospaced bold
    to_convert = sub(r'/(^|[\s\(])=(\S+?|\S[^\n]*?\S)=($|(?=[\s\)\.\,\:\;\!\?]))', r"\1<tt>\2<\/tt>", to_convert)  # monospaced
    to_convert = sub(r'/(^|[\n\r])---\+\+\+\+\+\+([^\n\r]*)', r"\1======\2 ======", to_convert)  # H6
    to_convert = sub(r'/(^|[\n\r])---\+\+\+\+\+([^\n\r]*)', r"\1=====\2 =====", to_convert)  # H5
    to_convert = sub(r'/(^|[\n\r])---\+\+\+\+([^\n\r]*)', r"\1====\2 ====", to_convert)  # H4
    to_convert = sub(r'/(^|[\n\r])---\+\+\+([^\n\r]*)', r"\1===\2 ===", to_convert)  # H3
    to_convert = sub(r'/(^|[\n\r])---\+\+([^\n\r]*)', r"\1==\2 ==", to_convert)  # H2
    to_convert = sub(r'/(^|[\n\r])---\+([^\n\r]*)', r"\1=\2 =", to_convert)  # H1

    # Bullets
    to_convert = sub(r'(^|[\n\r])[ ]{3}\* ', r"$1\* ", to_convert)  # level 1 bullet
    to_convert = sub(r'(^|[\n\r])[\t]{1}\* ', r"$1\* ", to_convert)  # level 1 bullet: Handle single tabs (from twiki .txt files)
    to_convert = sub(r'(^|[\n\r])[ ]{6}\* ', r"$1\*\* ", to_convert)  # level 2 bullet
    to_convert = sub(r'(^|[\n\r])[\t]{2}\* ', r"$1\*\* ", to_convert)  # level 1 bullet: Handle double tabs
    to_convert = sub(r'(^|[\n\r])[ ]{9}\* ', r"$1\*\*\* ", to_convert)  # level 3 bullet
    to_convert = sub(r'(^|[\n\r])[\t]{3}\* ', r"$1\*\*\* ", to_convert)  # level 3 bullet: Handle tabbed version
    to_convert = sub(r'(^|[\n\r])[ ]{12}\* ', r"$1\*\*\*\* ", to_convert)  # level 4 bullet
    to_convert = sub(r'(^|[\n\r])[ ]{15}\* ', r"$1\*\*\*\*\* ", to_convert)  # level 5 bullet
    to_convert = sub(r'(^|[\n\r])[ ]{18}\* ', r"$1\*\*\*\*\*\* ", to_convert)  # level 6 bullet
    to_convert = sub(r'(^|[\n\r])[ ]{21}\* ', r"$1\*\*\*\*\*\*\* ", to_convert)  # level 7 bullet
    to_convert = sub(r'(^|[\n\r])[ ]{24}\* ', r"$1\*\*\*\*\*\*\*\* ", to_convert)  # level 8 bullet
    to_convert = sub(r'(^|[\n\r])[ ]{27}\* ', r"$1\*\*\*\*\*\*\*\*\* ", to_convert)  # level 9 bullet
    to_convert = sub(r'(^|[\n\r])[ ]{30}\* ', r"$1\*\*\*\*\*\*\*\*\*\* ", to_convert)  # level 10 bullet

    # Numbering
    to_convert = sub(r'(^|[\n\r])[ ]{3}[0-9]\.? ', r"$1\# ", to_convert)  # level 1 bullet
    to_convert = sub(r'(^|[\n\r])[\t]{1}[0-9]\.? ', r"$1\# ", to_convert)  # level 1 bullet: handle 1 tab
    to_convert = sub(r'(^|[\n\r])[ ]{6}[0-9]\.? ', r"$1\#\# ", to_convert)  # level 2 bullet
    to_convert = sub(r'(^|[\n\r])[\t]{2}[0-9]\.? ', r"$1\#\# ", to_convert)  # level 2 bullet: handle 2 tabs
    to_convert = sub(r'(^|[\n\r])[ ]{9}[0-9]\.? ', r"$1\#\#\# ", to_convert)  # level 3 bullet
    to_convert = sub(r'(^|[\n\r])[\t]{3}[0-9]\.? ', r"$1\#\#\# ", to_convert)  # level 3 bullet: handle 3 tabs
    to_convert = sub(r'(^|[\n\r])[ ]{12}[0-9]\.? ', r"$1\#\#\#\# ", to_convert)  # level 4 bullet
    to_convert = sub(r'(^|[\n\r])[ ]{15}[0-9]\.? ', r"$1\#\#\#\#\# ", to_convert)  # level 5 bullet
    to_convert = sub(r'(^|[\n\r])[ ]{18}[0-9]\.? ', r"$1\#\#\#\#\#\# ", to_convert)  # level 6 bullet
    to_convert = sub(r'(^|[\n\r])[ ]{21}[0-9]\.? ', r"$1\#\#\#\#\#\#\# ", to_convert)  # level 7 bullet
    to_convert = sub(r'(^|[\n\r])[ ]{24}[0-9]\.? ', r"$1\#\#\#\#\#\#\#\# ", to_convert)  # level 8 bullet
    to_convert = sub(r'(^|[\n\r])[ ]{27}[0-9]\.? ', r"$1\#\#\#\#\#\#\#\#\# ", to_convert)  # level 9 bullet
    to_convert = sub(r'(^|[\n\r])[ ]{30}[0-9]\.? ', r"$1\#\#\#\#\#\#\#\#\#\# ", to_convert)  # level 10 bullet

    # Definitions
    # There must be a better MW convention
    to_convert = sub(r'(^|[\n\r])[ ]{3}\$ ([^\:]*)', r"$1\; $2 ", to_convert)  # $ definition: term

    # Lookup variable
    # q#s/%$varPattern%/getTwikiVar($1,'')/ge#,
    # q#s/%$varPattern(\{.*?\})%/getTwikiVar($1,$2)/ge#

    return to_convert


test = """
This is normal.<br /><br />This is a new paragraph.<br /><br />This text is normal. *This text is bolded.* _This text is italicized. *This text is both.* *This text is also both.**_ <u>This text is underlined. *This text is bold & underlined. <i>This text is ital and underlined. <b>This is all three!</b></i></u><br /><br /><br /><b>This is bold</b><br /><br /><b>This is still bold.</b><br /><br /><br />OK
"""
print(text_formatting(test))
