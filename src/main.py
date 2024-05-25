"""! Main entry point for Fix Season Names.
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
from typing import Any, Dict

from fix_season_names import FixSeasonNames
from util import Util


class Main:  # pylint: disable=too-few-public-methods
    """! Frame that runs the main application.
    """

    @staticmethod
    def _print_version() -> None:
        """! Print version information.
        """

        info: Dict[str, Any] = Util.get_project_info()

        # Print program version information
        print(f"{info['name']} {info['version']}")
        print()
        print(f"Copyright (c) {info['years']} {', '.join(info['authors'])}")
        print()
        print("This is free software; see the source for copying conditions.  There is NO")
        print("warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.")

    @staticmethod
    def _parse_args() -> argparse.Namespace:
        """! Parse command line arguments.

        @return An object containing the parsed command line arguments.
        """
        info: Dict[str, Any] = Util.get_project_info()
        nameversion: str = f"{info['name']} {info['version']}"
        description: str = f"{nameversion} -- {info['summary']}"

        parser: argparse.ArgumentParser = argparse.ArgumentParser(description=description, add_help=False)

        # Note: we're setting required to False even on required arguments and do the checks
        # ourselves below. We're doing that because we want more dynamic --version behaviour

        parser.add_argument('-h', '--help', action="help", help='Show this help message and exit')
        parser.add_argument("-v", "--version", required=False, action="store_true",
                            help="Print the version and exit")

        parser.add_argument('path', nargs='*', default=['.'], help="The path to operate on. "
                            "If none given, use the current directory")

        args_op = parser.add_argument_group("operational arguments")
        args_op.add_argument("-n", "--dry-run", required=False, action="store_true",
                             help="Go through all the motions but don't modify any files")

        args_tmdb = parser.add_argument_group("TMDB arguments (one of these is REQUIRED)")
        args_tmdb.add_argument("-b", "--bearer", required=False, type=str,
                               help="The bearer token for the TMDB API")
        args_tmdb.add_argument("-B", "--bearer-file", required=False, type=str,
                               help="Read the bearer token for the TMDB API from this file")

        args: argparse.Namespace = parser.parse_args()

        if args.version:
            Main._print_version()
            parser.exit()

        if args.bearer is None and args.bearer_file is None:
            parser.error("one of the following arguments is required: -b/--bearer, -f/--bearer-file")
        if args.bearer is not None and args.bearer_file is not None:
            parser.error("only one of the following arguments is supported at the same time: "
                         "-b/--bearer, -B/--bearer-file")

        if args.bearer_file is not None:
            try:
                with open(args.bearer_file, "r", encoding="utf-8") as bearer_file:
                    args.bearer = bearer_file.read().strip()
            except OSError as error:
                print(f"Failed to open bearer file '{args.bearer_file}': {error}")
                parser.exit(status=2)

        return args

    def run(self) -> None:
        """! Run the main Fix Season Names application.
        """
        args = Main._parse_args()

        fix_season_names: FixSeasonNames = FixSeasonNames(args)
        fix_season_names.run()


def main() -> None:
    """! Fix Season Names main function, running the main app.
    """
    main_app: Main = Main()
    main_app.run()


if __name__ == '__main__':
    main()
