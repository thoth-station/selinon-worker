#!/usr/bin/env python3
# thoth-worker
# Copyright(C) 2018 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Tasks related to PyPI."""

import logging
from urllib.parse import urlparse
from collections import OrderedDict

from selinon import SelinonTask
from selinon import StoragePool
from selinon import FatalTaskError

import requests
from thoth.python import Source

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


PYPI = Source(url="https://pypi.org/simple")


class PyPIListingTask(SelinonTask):
    """List available Python projects on PyPI."""

    def run(self, node_args):
        """"Get listing of available packages on PyPI."""
        return [{"package_name": package_name} for package_name in PYPI.get_packages()]


class ProjectInfoTask(SelinonTask):
    """Aggregate project information as provided by PyPI."""

    def run(self, node_args) -> dict:
        """Download the given JSON document for project as provided by PyPI."""
        assert "package_name" in node_args
        package_name = node_args["package_name"]

        # For now we retrieve description for the latest release.
        api_url = PYPI.get_api_url()
        response = requests.get(api_url + f"/{package_name}/json")
        response.raise_for_status()

        result = response.json()
        return result


class RetrieveProjectReadmeTask(SelinonTask):
    """Retrieve README file from GitHub/GitLab if available."""

    _GITHUB_README_PATH = (
        "https://raw.githubusercontent.com/{project}/{repo}/master/README{extension}"
    )

    # Based on https://github.com/github/markup#markups
    # Markup type to its possible extensions mapping, we use OrderedDict as we
    # check the most used types first
    README_TYPES = OrderedDict(
        (
            ("Markdown", ("md", "markdown", "mdown", "mkdn")),
            ("reStructuredText", ("rst",)),
            ("AsciiDoc", ("asciidoc", "adoc", "asc")),
            ("Textile", ("textile",)),
            ("RDoc", ("rdoc",)),
            ("Org", ("org",)),
            ("Creole", ("creole",)),
            ("MediaWiki", ("mediawiki", "wiki")),
            ("Pod", ("pod",)),
            ("Unknown", ("",)),
        )
    )

    def run(self, node_args) -> dict:
        """Retrieve README file from GitHub."""
        # TODO: add GitLab support.
        package_name = node_args["package_name"]
        project_info_store = StoragePool.get_connected_storage("ProjectInfoStore")

        home_page = (
            project_info_store.retrieve_project_info(package_name)
            .get("info", {})
            .get("home_page")
        )
        if not home_page:
            raise FatalTaskError(f"No home page found for project {package_name!r}")

        home_page = urlparse(home_page)
        if home_page.netloc != "github.com":
            raise FatalTaskError(
                f"No GitHub home page associated for project {package_name!r}"
            )

        path_parts = home_page.path.split("/")
        if len(path_parts) < 3:
            # 3 because of leading slash
            raise FatalTaskError(
                f"Unable to parse GitHub organization and repo for project {package_name!r}"
            )

        project, repo = path_parts[1], path_parts[2]
        for readme_type, extensions in self.README_TYPES.items():
            for extension in extensions:
                if extension:
                    extension = "." + extension
                url = self._GITHUB_README_PATH.format(
                    project=project, repo=repo, extension=extension
                )
                response = requests.get(url)
                if response.status_code != 200:
                    _LOGGER.debug(
                        'No README%s found for type "%s" at "%s"',
                        extension,
                        readme_type,
                        url,
                    )
                    continue

                _LOGGER.debug(
                    'README%s found for type "%s" at "%s"', extension, readme_type, url
                )
                return {
                    "type": readme_type,
                    "content": response.text,
                    "package_name": package_name,
                    "url": url,
                }
