"""! The actual Fix Season Names logic.
"""

# Fix Season Names - Fix TV season names in Jellyfin
#
# Fix Season Names is the legal property of its developers, whose names
# can be found in the AUTHORS file distributed with this source
# distribution.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Union

from tmdb import TMDB


class FixSeasonNames:  # pylint: disable=too-few-public-methods
    """! Fix Season Names logic.
    """

    def __init__(self, args: argparse.Namespace) -> None:
        self._bearer: str = args.bearer
        self._dry_run: bool = args.dry_run
        self._paths: List[str] = args.path

        self._tmdb: Optional[TMDB] = None

    @staticmethod
    def _find_tv_shows(paths: Union[List[Path], List[str]]) -> List[Path]:
        shows = []

        for path in paths:
            if not Path(path).is_dir():
                raise IOError(f"\"{path}\" does not exist or is not a directory")

            new_shows = list(Path(path).rglob('tvshow.nfo'))
            shows.extend(sorted(new_shows))

        return shows

    @staticmethod
    def _find_seasons(paths: Union[List[Path], List[str]]) -> List[Path]:
        seasons = []

        for path in paths:
            if not Path(path).is_dir():
                raise IOError(f"\"{path}\" does not exist or is not a directory")

            new_seasons = list(Path(path).rglob('season.nfo'))
            seasons.extend(sorted(new_seasons))

        return seasons

    @staticmethod
    def _get_xml_element_text(node, path: str) -> Optional[str]:
        element = node.find(path)
        if element is None:
            return None

        return None if element.text == "" else element.text

    @staticmethod
    def _set_xml_element_text(node, path: str, text: str) -> None:
        element = node.find(path)
        if element is None:
            raise KeyError(f"No such tag {path}")

        element.text = text

    def _fix_season(self, show_id: int, language: str, season: Path) -> None:
        season_tree = ET.parse(season)
        season_root = season_tree.getroot()

        if season_root.tag != "season":
            raise AttributeError("The file doesn't describe a season")

        old_title = self._get_xml_element_text(season_root, "./title")
        season_number = self._get_xml_element_text(season_root, "./seasonnumber")

        if old_title is None or season_number is None:
            raise KeyError("Season has no title or season number")

        assert self._tmdb is not None
        season_details = self._tmdb.get_tv_series_season(show_id, int(season_number), language=language)

        new_title = season_details["name"]

        if old_title == new_title:
            print(f"Season {season_number} already has the correct title '{new_title}'")
            return

        print(f"Fixing season {season_number} from '{old_title}' to '{new_title}' "
              f"{'' if not self._dry_run else '(DRY RUN)'}")

        if self._dry_run:
            return

        self._set_xml_element_text(season_root, "./title", new_title)

        with open(season, "w", encoding="utf-8") as outfile:
            outfile.write('\ufeff<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n')
            season_tree.write(outfile, encoding="unicode", xml_declaration=False)

    def _fix_show(self, show: Path) -> None:
        show_tree = ET.parse(show)
        show_root = show_tree.getroot()

        if show_root.tag != "tvshow":
            raise AttributeError("This file doesn't describe a TV show")

        title = self._get_xml_element_text(show_root, "./title")
        year = self._get_xml_element_text(show_root, "./year")
        tmdbid = self._get_xml_element_text(show_root, "./tmdbid")

        language = self._get_xml_element_text(show_root, "./language")
        if language is None:
            language = "en"

        if title is None or year is None or tmdbid is None:
            raise KeyError("TV Show has no title, year or TMDB ID")

        print(f"{title} ({year}) [{tmdbid}] {{{language}}}")

        seasons = self._find_seasons([show.parent])
        if not seasons:
            raise AttributeError("This show doesn't have any seasons")

        for season in seasons:
            try:
                self._fix_season(int(tmdbid), language, season)
            except (OSError, AttributeError, KeyError, ValueError, RuntimeError) as error:
                print(f"Skipping {season.parent.name}: {error}")

    def run(self) -> None:
        """! Run the main logic.
        """

        try:
            shows = self._find_tv_shows(self._paths)
        except IOError as error:
            print(f"Error: {error}")
            return

        if not shows:
            print("No TV shows found!")
            return

        print(f"Found {len(shows)} TV show(s)")

        self._tmdb = TMDB(self._bearer)

        for show_index, show in enumerate(shows, start=1):
            print("")
            print("---")
            print(f"{show_index}/{len(shows)}: {show}:")

            try:
                self._fix_show(show)
            except (OSError, AttributeError, KeyError) as error:
                print(f"Skipping: {error}")
