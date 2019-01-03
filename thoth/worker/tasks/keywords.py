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

import libarchive.public
import xmltodict
import requests
from selinon import SelinonTask
from selinon import StoragePool

_LOGGER = logging.getLogger(__name__)


class PyPIKeywordsAggregationTask(SelinonTask):
    """Extract keywords from project information that was previously aggregated."""

    def run(self, node_args: dict) -> dict:
        """Extract and aggregate keywords from project description as provided by PyPI."""
        project_info_store = StoragePool.get_connected_storage("ProjectInfoStore")

        keywords_dict = {}
        # TODO: if the keywords extraction takes too much time we can encounter task timeouts, we can rewrite this into map-reduce fashion
        for document in project_info_store.iter_project_info_documents():
            keywords = document.get("info", {}).get('keywords') or ''
            keywords = re.split(r"[\s+,;]", keywords)
            for keyword in keywords:
                if not keyword:
                    continue

                keyword = keyword.lower()
                keywords_dict[keyword] = keywords_dict.get(keyword, 0) + 1

        return keywords_dict


class StackOverflowKeywordsAggregationTask(SelinonTask):
    """Aggregate keywords from StackOverflow."""

    _STACKOVERFLOW_URL = 'https://archive.org/download/stackexchange/stackoverflow.com-Tags.7z'

    def run(self, node_args: dict) -> dict:
        """Aggregate StackOverflow keywords."""
        response = requests.get(self._STACKOVERFLOW_URL)
        if not response.ok:
            raise RuntimeError("Failed to fetch stack overflow tags, request ended with status code %s: %s", response.status_code, response.text)

        tags = None
        with libarchive.public.memory_reader(response.content) as archive:
            for entry in archive:
                tags = xmltodict.parse(b"".join(entry.get_blocks()))
                break

        result = {}
        for tag in tags['tags']['row']:
            try:
                result[tag['@TagName']] = int(tag['@Count'])
            except ValueError:
                _LOGGER.warning("Failed to parse number of occurrences for tag %s", tag['@TagName'])
                continue
            except KeyError:
                _LOGGER.exception("Missing tagname or tag count")
                continue

        return result


class KeywordsAggregationTask(SelinonTask):
    """Combine keywords from multiple sources and aggregate it into a single dict used in model creation."""

    def run(self, node_args: dict) -> dict:
        """Combine keywords from multiple sources."""
        pypi_keywords = self.parent_task_result('PyPIKeywordsAggregationTask')
        stackoverflow_keywords = self.parent_task_result('StackOverflowKeywordsAggregationTask')
        # TODO: aggregate them
