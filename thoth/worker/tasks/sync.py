import logging

from selinon import SelinonTask

from thoth.storages.graph import GraphDatabase
from thoth.storages import SolverResultsStore
from thoth.storages import AnalysisResultsStore


_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class SyncListingTask(SelinonTask):
    def run(self, node_args):
        result = []

        solver_store = SolverResultsStore()
        solver_store.connect()

        _LOGGER.info("Retrieving solver documents")
        for document_id in solver_store.get_document_listing():
            result.append({'document_id': document_id, 'solver': True})

        analysis_store = AnalysisResultsStore()
        analysis_store.connect()

        _LOGGER.info("Retrieving analysis documents")
        for document_id in analysis_store.get_document_listing():
            result.append({'document_id': document_id, 'solver': False})

        return result


class GraphSyncSolverTask(SelinonTask):
    def run(self, node_args):
        document_id = node_args['document_id']

        graph = GraphDatabase()
        graph.connect()

        solver_store = SolverResultsStore()
        solver_store.connect()

        _LOGGER.info("Retrieving solver document with id %r", document_id)
        solver_document = solver_store.retrieve_document(document_id)

        _LOGGER.info("Syncing solver document with id %r", document_id)
        graph.sync_solver_result(solver_document)



class GraphSyncAnalysisTask(SelinonTask):
    def run(self, node_args):
        document_id = node_args['document_id']

        graph = GraphDatabase()
        graph.connect()

        analysis_store = AnalysisResultsStore()
        analysis_store.connect()

        _LOGGER.info("Retrieving analysis document with id %r", document_id)
        analysis_document = analysis_store.retrieve_document(document_id)

        _LOGGER.info("Syncing analysis document with id %r", document_id)
        graph.sync_analysis_result(analysis_document)
