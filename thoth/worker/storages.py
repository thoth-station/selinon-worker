import os

from thoth.storages.ceph import CephStore
from selinon import DataStorage


class ProjectInfoStore(DataStorage):

    def __init__(self, bucket: str, prefix: str, aws_access_key_id: str, aws_secret_access_key: str):
        self.ceph = None
        self.bucket = bucket
        self.prefix = prefix
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

    def connect(self):
        self.ceph = CephStore(
            prefix=self.prefix.format(**os.environ),
            bucket=self.bucket.format(**os.environ),
            secret_key=self.aws_secret_access_key.format(**os.environ),
            key_id=self.aws_access_key_id.format(**os.environ)
        )
        self.ceph.connect()

    def is_connected(self):
        return self.ceph is not None

    def disconnect(self):
        self.ceph = None

    def retrieve(self, flow_name: str, task_name: str, task_id: str) -> dict:
        return self.ceph.retrieve_document(str(task_id))

    def store(self, node_args: dict, flow_name: str, task_name: str, task_id: str, result: str) -> str:
        document_id = self.ceph.store_document(result, task_id)
        return document_id
