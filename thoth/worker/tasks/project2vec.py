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

"""Implementation of project2vec vector space creation using Map-Reduce."""

import typing
import itertools
import logging

from nltk import word_tokenize
from selinon import SelinonTask
from selinon import StoragePool
from selinon.errors import NoParentNodeError

from thoth.worker.exceptions import NotFoundException

_LOGGER = logging.getLogger(__name__)


class Project2VecTask(SelinonTask):
    """Implementation of project2vec for a single project (one vector in the resulting project2vec vector space)."""

    _KEYWORD_OCCURRENCE_THRESHOLD = 0

    @staticmethod
    def get_documents(package_name: str):
        """Retrieve documents that should be used for keywords extraction."""
        project_info_store = StoragePool.get_connected_storage("ProjectInfoStore")
        readme_store = StoragePool.get_connected_storage("ReadmeStore")

        # TODO: try to perform cleaning for README files - we could use content type, the same applies for description
        try:
            yield project_info_store.retrieve_project_info(package_name).get(
                "info", {}
            ).get("description", "")
        except NotFoundException:
            _LOGGER.info("No project info found found for project %r", package_name)
            pass

        try:
            yield readme_store.retrieve_project_readme(package_name)["result"][
                "content"
            ]
        except NotFoundException:
            _LOGGER.info("No README file found for project %r", package_name)
            pass

    @classmethod
    def get_keywords(cls) -> typing.List[str]:
        """Retrieve keywords vector aggregated before."""
        aggregated_keywords_store = StoragePool.get_connected_storage(
            "AggregatedKeywordsStore"
        )
        keywords = aggregated_keywords_store.retrieve_keywords()
        return sorted(
            keyword
            for keyword, occurrence in keywords["result"].items()
            if occurrence > cls._KEYWORD_OCCURRENCE_THRESHOLD
        )

    def run(self, node_args: dict) -> dict:
        """Compute a single vector for project2vec for the given project."""
        package_name = node_args["package_name"]

        keywords = self.get_keywords()
        vector = [0] * len(keywords)

        for document in self.get_documents(package_name):
            if not document:
                continue

            document = word_tokenize(document)
            for idx, keyword in enumerate(keywords):
                if keyword in document:
                    vector[idx] = 1

        return {"project": package_name, "vector": vector}


class Project2VecCreationTask(SelinonTask):
    """Implementation of project2vec - creation of project2vec vector space (reduce part)."""

    def run(
        self, node_args: dict
    ) -> typing.Tuple[typing.List[str], typing.List[typing.List[int]]]:
        """Aggregate project2vec results into a single vector space."""
        projects = []
        for i in itertools.count():
            try:
                result = self.parent_flow_result("_project2vec", "Project2VecTask", i)
            except NoParentNodeError:
                # This exception is raised if there are no more parent tasks.
                _LOGGER.exception("Foo")
                break

            projects.append((result["project"], result["vector"]))

        # Sort by project names
        project_names = []
        vector_space = []
        for project in sorted(projects):
            project_names.append(project[0])
            vector_space.append(project[1])

        return project_names, vector_space
