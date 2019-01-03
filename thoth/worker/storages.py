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

"""Storage adapters for Thoth worker."""

import os

from thoth.storages.ceph import CephStore
from thoth.common import datetime2datetime_str as datetime_str
from selinon import DataStorage


class CephWorkerStorageBase(DataStorage):
    """A base class for implementing Ceph based adapters in Thoth's worker."""

    def __init__(self, bucket: str, prefix: str, aws_access_key_id: str, aws_secret_access_key: str, s3_endpoint: str):
        """Initialize storing of project information."""
        self.ceph = None
        self.bucket = bucket
        self.prefix = prefix
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.s3_endpoint = s3_endpoint

    def connect(self):
        """Connect to the remote Ceph."""
        self.ceph = CephStore(
            prefix=self.prefix.format(**os.environ),
            bucket=self.bucket.format(**os.environ),
            secret_key=self.aws_secret_access_key.format(**os.environ),
            key_id=self.aws_access_key_id.format(**os.environ),
            host=self.s3_endpoint.format(**os.environ)
        )
        self.ceph.connect()

    def is_connected(self):
        """Check if we are connected to a Ceph."""
        return self.ceph is not None

    def disconnect(self):
        """Disconnect from remote Ceph."""
        self.ceph = None


class ProjectInfoStore(CephWorkerStorageBase):
    """Store information about the given Python project."""

    def retrieve(self, flow_name: str, task_name: str, task_id: str) -> dict:
        # We do not provide implementation of this method as we store project information based on project name.
        raise NotImplementedError

    def retrieve_project_info(self, package_name: str):
        """Retrieve project information as stored on Ceph."""
        return self.ceph.retrieve_document(package_name)

    def store(self, node_args: dict, flow_name: str, task_name: str, task_id: str, result: str) -> str:
        """Store package information."""
        return self.ceph.store_document(result, node_args["package_name"])

    def iter_project_info_documents(self) -> dict:
        """Iterate over documents stored on Ceph."""
        yield from (document for _, document in self.ceph.iterate_results())

    def get_project_listing(self):
        """Get listing of projects for which there is stored project info."""
        return [document_id.split('/')[-1] for document_id in self.ceph.get_document_listing()]


class ReadmeStore(CephWorkerStorageBase):
    """Store project README files onto Ceph."""

    def retrieve(self, flow_name, task_name, task_id):
        # We use project name for naming files so this method cannot be used, but is required by Selinon.
        raise NotImplementedError

    @staticmethod
    def _get_object_key(project_name: str) -> str:
        """Get object key under"""
        return os.path.join('readme', project_name)

    def retrieve_project_readme(self, project_name: str) -> dict:
        """Retrieve a project readme file."""
        return self.ceph.retrieve_document(self._get_object_key(project_name))

    def store(self, node_args: dict, flow_name: str, task_name: str, task_id: str, result: dict) -> dict:
        """Store the given readme file for the given project."""
        project_name = node_args['project_name']
        document = {
            'result': result,
            '@meta': {
                'datetime': datetime_str()
            }
        }
        return self.ceph.store_document(document, self._get_object_key(project_name))


class KeywordsStoreBase(CephWorkerStorageBase):
    """Storing JSON documents with aggregated keywords."""

    _DOCUMENT_ID = None

    def retrieve(self, flow_name: str, task_name: str, task_id: str) -> dict:
        """Retrieve keywords stored on Ceph."""
        return self.ceph.retrieve_document(self._DOCUMENT_ID)

    def store(self, node_args: dict, flow_name: str, task_name: str, task_id: str, result: dict) -> dict:
        """Store keywords stored on Ceph."""
        document = {
            'result': result,
            '@meta': {
                'datetime': datetime_str()
            }
        }
        return self.ceph.store_document(document, self._DOCUMENT_ID)


class PyPIKeywordsStore(KeywordsStoreBase):
    """Storing keywords of keywords as found on PyPI."""

    _DOCUMENT_ID = 'keywords_pypi.json'


class StackOverflowKeywordsStore(KeywordsStoreBase):
    """Store keywords as found on StackOverflow."""

    _DOCUMENT_ID = 'keywords_stackoverflow.json'


class AggregatedKeywordsStore(KeywordsStoreBase):
    """Store keywords that are aggregated from different keywords sources."""

    _DOCUMENT_ID = 'keywords_aggregated.json'

