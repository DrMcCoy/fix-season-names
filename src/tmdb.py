"""! Interacting with The Movie Database (TMDB).
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

from typing import Any, Dict, List, Optional

import requests


class TMDB:  # pylint: disable=too-few-public-methods
    """! Interacting with The Movie Database (TMDB).
    """

    def __init__(self, bearer: str) -> None:
        self._bearer: str = bearer
        self._try_auth()

    def _query(self, endpoint: str, path_params: Optional[List[str]] = None,
               query_params: Optional[Dict[Any, Any]] = None) -> Dict[Any, Any]:

        path_params_str = ""
        if path_params:
            path_params_str = "/" + "/".join(path_params)

        query_params_str = ""
        if query_params:
            query_params_str = "?" + "&".join([f"{key}={value}" for key, value in query_params.items()])

        url = f"https://api.themoviedb.org/3/{endpoint}{path_params_str}{query_params_str}"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self._bearer}"
        }

        response = requests.get(url, timeout=5, headers=headers)
        response.raise_for_status()

        return response.json()

    def _try_auth(self) -> None:
        print("Trying to authenticate with TMDB...")

        try:
            response = self._query("authentication")
            if "success" not in response:
                raise RuntimeError("Response has no success value")
            if not response["success"]:
                raise RuntimeError("Response yielded no success")
        except (requests.exceptions.HTTPError, RuntimeError) as error:
            raise RuntimeError(f"Failed to authenticate with TMDB: {error}") from error

    def get_tv_series_season(self, series_id: int, season_number: int,
                             language: Optional[str] = None) -> Dict[Any, Any]:
        """! Query TMDB for details about a season of a TV series.

        @param series_id      ID of the TV series on TMDB.
        @param season_number  Index of the season to query.
        @param language       For which language to query.

        @return A dict with details about the season.
        """

        try:
            query_params = None
            if language is not None:
                query_params = {"language": language}

            response = self._query("tv", path_params=[str(series_id), "season", str(season_number)],
                                   query_params=query_params)
            return response

        except requests.exceptions.HTTPError as error:
            raise RuntimeError(f"Failed to get season: {error}") from error
