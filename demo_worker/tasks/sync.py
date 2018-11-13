from selinon import SelinonTask


class GraphSyncTask(SelinonTask):
    def run(self, node_args):
        document_id = node_args['document_id']
        print("Document id is %r", document_id)
