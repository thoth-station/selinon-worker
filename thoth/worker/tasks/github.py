#!/usr/bin/env python3
# thoth-worker
# Copyright(C) 2018, 2019, 2020 Fridolin Pokorny
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

from collections import OrderedDict
import logging
import os
import requests
from selinon import SelinonTask
from thoth.python import Source
import yaml

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


PYPI = Source(url="https://pypi.org/simple")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
_PRESCRIPTIONS_BASE_URL = "https://raw.githubusercontent.com/thoth-station/prescriptions/master/prescriptions/"


class _GitHubTaskBase(SelinonTask):
    """A base class for GitHub related routines."""

    def get_project_repo_github(self, package_name: str):
        """Get project and repo for the given package based on aggregated package info from Thoth's Prescriptions."""
        package_prefix = package_name[:2] + "_"
        headers = {"Authorization": GITHUB_TOKEN}
        prescription_link = os.path.join(
            _PRESCRIPTIONS_BASE_URL, package_prefix, package_name, "gh_link.yaml"
        )

        gh_link_yaml = requests.get(prescription_link, headers=headers)

        if gh_link_yaml.status_code != 200:
            _LOGGER.debug(
                f"Request status code {gh_link_yaml.status_code}: Cannot access prescription YAML file at {prescription_link}"
            )
            package_prefix_alternatives = [
                package_name[:1] + "_",
                package_name[:3] + "_",
            ]
            valid_status_code = False

            for prefix in package_prefix_alternatives:
                prescription_link = os.path.join(
                    _PRESCRIPTIONS_BASE_URL, prefix, package_name, "gh_link.yaml"
                )
                gh_link_yaml = requests.get(
                    prescription_link,
                    headers=headers,
                )

                if gh_link_yaml.status_code != 200:
                    _LOGGER.debug(
                        f"Request status code {gh_link_yaml.status_code}: Cannot access prescription YAML file at {prescription_link}"
                    )
                else:
                    valid_status_code = True
                    break

        if not valid_status_code:
            raise Exception(
                "Cannot access prescription YAML file URL: invalid status code"
            )

        yaml_file = yaml.safe_load(gh_link_yaml.text)
        repo_link = yaml_file["units"]["wraps"][0]["run"]["justification"][0]["link"]

        return package_name, repo_link

    def run(self, node_args: dict) -> dict:
        raise NotImplementedError


class RetrieveProjectReadmeTask(_GitHubTaskBase):
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
        project, repo = self.get_project_repo_github(node_args["package_name"])

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
                    "package_name": node_args["package_name"],
                    "url": url,
                }


class RetrieveGitHubInfoTask(_GitHubTaskBase):
    """Aggregate GitHub information for a Python package."""

    _HEADERS = {
        "Accept": "application/vnd.github.mercy-preview+json, "  # for topics
        "application/vnd.github.v3+json"  # recommended by GitHub for License API
    }

    _GITHUB_TOPICS_URL = "https://api.github.com/repos/{project}/{repo}/topics"

    _GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

    def requests(self, url):
        """Perform request to GitHub API, adjust headers and token (if configured so)."""
        if self._GITHUB_TOKEN:
            headers = dict(**self._HEADERS, Authorization=f"token {self._GITHUB_TOKEN}")
        else:
            _LOGGER.warning(
                "No GitHub token configured, API requests will be throttled"
            )
            headers = self._HEADERS

        response = requests.get(url, headers=headers)
        return response

    def run(self, node_args: dict) -> dict:
        """Aggregate information for a Python package based on URL stated in the project info on PyPI."""
        project, repo = self.get_project_repo_github(node_args["package_name"])

        # Topics gathering.
        response = self.requests(
            self._GITHUB_TOPICS_URL.format(project=project, repo=repo)
        )
        response.raise_for_status()
        topics = response.json()["names"]

        return {"topics": topics}
