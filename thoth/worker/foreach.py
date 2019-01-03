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

"""Iterate over results of tasks to spawn tasks in parallel."""


import logging

_LOGGER = logging.getLogger(__name__)


def iter_sync_documents(storage_pool, node_args):
    """Iterate over documents to be synced."""
    try:
        return storage_pool.get("SyncListingTask")
    except Exception as exc:
        _LOGGER.exception(str(exc))
        return []


def iter_pypi_projects(storage_pool, node_args):
    """Iterate over PyPI projects as stated on PyPI simple API index."""
    try:
        return storage_pool.get("PyPIListingTask")
    except Exception as exc:
        _LOGGER.exception(str(exc))
        return []


def iter_pypi_projects_ceph(storage_pool, node_args):
    """Iterate over documents of project information as stored on Ceph."""
    try:
        storage = storage_pool.get_connected_storage("ProjectInfoStore")
        return [
            {"package_name": package_name}
            for package_name in storage.get_project_listing()
        ]
    except Exception as exc:
        _LOGGER.exception(str(exc))
        return []
