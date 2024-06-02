Fix Season Names README
=======================

Fix Season Names is just a small helper script to fix season names in a media
library after they've been broken with Jellyfin 10.9.x.

It runs throughs a whole library, looking for tvshow.nfo files to find TV shows,
then looks for season.nfo files in subfolders to find their seasons. The
information in those files are used to query The Movie Database via its API
to grab the names of each season, and then the season.nfo files are patched
to rename to the seasons accordingly.

An API key for The Movie Database is required to run this script.

Fix Season Names is released under the terms of the
[GNU Affero General Public License version 3](https://www.gnu.org/licenses/agpl.html)
(or later).
