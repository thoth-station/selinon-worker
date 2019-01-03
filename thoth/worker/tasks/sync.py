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

"""Tasks related to syncing results to the graph database (experimental for benchmarks)."""

import logging

from selinon import SelinonTask

from thoth.storages.graph import GraphDatabase
from thoth.storages import SolverResultsStore
from thoth.storages import AnalysisResultsStore


_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class SyncListingTask(SelinonTask):
    """List available documents present on Ceph that should be synced into the graph database."""

    def run(self, node_args):
        result = []

        solver_store = SolverResultsStore()
        solver_store.connect()

        _LOGGER.info("Retrieving solver documents")
        for document_id in solver_store.get_document_listing():
            result.append({"document_id": document_id, "solver": True})

        analysis_store = AnalysisResultsStore()
        analysis_store.connect()

        _LOGGER.info("Retrieving analysis documents")
        for document_id in analysis_store.get_document_listing():
            result.append({"document_id": document_id, "solver": False})

        return result


class GraphSyncSolverTask(SelinonTask):
    """Sync solver document into graph."""

    def run(self, node_args):
        document_id = node_args["document_id"]

        graph = GraphDatabase()
        graph.connect()

        solver_store = SolverResultsStore()
        solver_store.connect()

        _LOGGER.info("Retrieving solver document with id %r", document_id)
        solver_document = solver_store.retrieve_document(document_id)

        _LOGGER.info("Syncing solver document with id %r", document_id)
        graph.sync_solver_result(solver_document)


class GraphSyncAnalysisTask(SelinonTask):
    """Sync analysis document into graph."""

    def run(self, node_args):
        document_id = node_args["document_id"]

        graph = GraphDatabase()
        graph.connect()

        analysis_store = AnalysisResultsStore()
        analysis_store.connect()

        _LOGGER.info("Retrieving analysis document with id %r", document_id)
        analysis_document = analysis_store.retrieve_document(document_id)

        _LOGGER.info("Syncing analysis document with id %r", document_id)
        graph.sync_analysis_result(analysis_document)
