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
from selinon import DataStorage


class ProjectInfoStore(DataStorage):
    """Store information about the given Python project."""

    def __init__(self, bucket: str, prefix: str, aws_access_key_id: str, aws_secret_access_key: str, s3_endpoint: str):
        self.ceph = None
        self.bucket = bucket
        self.prefix = prefix
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.s3_endpoint = s3_endpoint

    def connect(self):
        self.ceph = CephStore(
            prefix=self.prefix.format(**os.environ),
            bucket=self.bucket.format(**os.environ),
            secret_key=self.aws_secret_access_key.format(**os.environ),
            key_id=self.aws_access_key_id.format(**os.environ),
            host=self.s3_endpoint.format(**os.environ)
        )
        self.ceph.connect()

    def is_connected(self):
        return self.ceph is not None

    def disconnect(self):
        self.ceph = None

    @staticmethod
    def get_result_document_id(flow_name: str, task_name: str, node_args):
        return os.path.join(flow_name, task_name[:-len("Task")], node_args["package_name"])

    def retrieve(self, flow_name: str, task_name: str, task_id: str) -> dict:
        raise NotImplementedError

    def store(self, node_args: dict, flow_name: str, task_name: str, task_id: str, result: str) -> str:
        document_id = self.get_result_document_id(flow_name, task_name, node_args)
        return self.ceph.store_document(result, document_id)
