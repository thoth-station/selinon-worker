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

"""Gathering keywords and tags for project2vec."""

import logging
import re
import itertools

import xmltodict
import requests
from selinon import SelinonTask
from selinon import StoragePool
from selinon.errors import NoParentNodeError

_LOGGER = logging.getLogger(__name__)


class StackOverflowKeywordsAggregationTask(SelinonTask):
    """Aggregate keywords from StackOverflow."""

    _STACKOVERFLOW_URL = (
        "https://archive.org/download/stackexchange/stackoverflow.com-Tags.7z"
    )

    def run(self, node_args: dict) -> dict:
        """Aggregate StackOverflow keywords."""
        # Move import here as we run this task locally, there are issues with libarchive.so in Python's s2i.
        import libarchive.public

        response = requests.get(self._STACKOVERFLOW_URL)
        if not response.ok:
            raise RuntimeError(
                "Failed to fetch stack overflow tags, request ended with status code %s: %s",
                response.status_code,
                response.text,
            )

        tags = None
        with libarchive.public.memory_reader(response.content) as archive:
            for entry in archive:
                tags = xmltodict.parse(b"".join(entry.get_blocks()))
                break

        result = {}
        for tag in tags["tags"]["row"]:
            try:
                result[tag["@TagName"]] = int(tag["@Count"])
            except ValueError:
                _LOGGER.warning(
                    "Failed to parse number of occurrences for tag %s", tag["@TagName"]
                )
                continue
            except KeyError:
                _LOGGER.exception("Missing tagname or tag count")
                continue

        return result


class KeywordsAggregationTask(SelinonTask):
    """Combine keywords from multiple sources and aggregate it into a single dict used in model creation."""

    def run(self, node_args: dict) -> dict:
        """Combine keywords from multiple sources."""
        result = {}
        for i in itertools.count():
            try:
                keywords = self.parent_flow_result(
                    "_pypi_keywords_flow", "PyPIProjectKeywordsTask", i
                )
            except NoParentNodeError:
                # This exception is raised if there are no more parent tasks.
                break

            for keyword, count in keywords.items():
                if keyword not in result:
                    result[keyword] = 0

                result[keyword] += count

        return result


class PyPIProjectKeywordsTask(SelinonTask):
    """Get keywords for a single project."""

    def run(self, node_args: dict) -> dict:
        package_name = node_args["package_name"]
        project_info_store = StoragePool.get_connected_storage("ProjectInfoStore")
        document = project_info_store.retrieve_project_info(package_name)

        keywords = document.get("info", {}).get("keywords") or ""
        keywords = re.split(r"[\s+,;]", keywords)

        keywords_dict = {}
        for keyword in keywords:
            if not keyword:
                continue

            keyword = keyword.lower()
            keywords_dict[keyword] = keywords_dict.get(keyword, 0) + 1

        return keywords_dict
