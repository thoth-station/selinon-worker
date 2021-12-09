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
