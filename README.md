twiki-to-mediawiki-xml
======================

This is a new attempt to convert a TWiki to a MediaWiki. This tool parses the
TWiki data files and produces a MediaWiki XML dump. This import method is
different from past open solutions, but it is the most native way to get data
into MediaWiki, and it supports importing all possible features (like
revisions).

This tool runs on Python 3.8+.

A lot of the TWiki parsing logic is reworked from [Ryan Castillo's
Twiki-to-Mediawiki](https://github.com/rmcastil/Twiki-to-Mediawiki)
(written in Perl).

## Planning

A current (possible) plan for this tool is to develop several sub-tools:

- **TWiki medtadata parser:** Given a TWiki data web directory, convert the data
  as-is to easily-machine-readable JSON (including revisions)
- **TWiki to Wikitext convertor:** Convert the contents of pages from TWiki format
  to Wikitext format
- **TWiki to Wikitext conventions convertor:** Take a parsed TWiki metadata data
  and convert in-place to MediaWiki conventions (like WikiWords to
  Capital_Snake_Case).
- **TWiki JSON to MediaWiki XML**: Given converted JSON files, transform them
  into a [MediaWiki XML dump](https://www.mediawiki.org/wiki/Manual:Importing_XML_dumps).

## Features

### Current

- None!

### Planned

- Convert all formatting ([Wikitext](https://www.mediawiki.org/wiki/Wikitext))
- Revisions
- Preserve all timestamps
- Convert [signatures](https://www.mediawiki.org/wiki/Help:Signatures)
- Convert WikiWords to link
- Convert WikiWords to [MediaWiki convention (underscores)](https://en.wikipedia.org/wiki/Wikipedia:Naming_conventions_(technical_restrictions))
- Attachments/Files
- File metadata
- File revisions
- Move user pages to MediaWiki `User:` given a list of user pages
- Rename user pages to target MediaWiki username given a mapping
- Convert parents pages to [Subpages](https://www.mediawiki.org/wiki/Help:Subpages)

### Possible but Unlikely
- Support multiple TWiki webs
- Unit testing

## Development

Install Python 3.8 or later and [PIP](https://pypi.org/project/pip/). Clone
the repo and change to it. It is recommended to use a venv (if you know how).
Then:

```bash
pip install -e .
```

The `twiki-to-mediawiki-xml` command should now be available.

## License

Copyright (C) 2022-present  AB Tech, Carnegie Mellon University

Copyright (C) 2022          Perry Naseck (git@perrynaseck.com)

Copyright (C) 2011-2016     Ryan Castillo (some parts of files)

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
