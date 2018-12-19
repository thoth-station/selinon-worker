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
    try:
        return storage_pool.get('SyncListingTask')
    except Exception as exc:
        _LOGGER.exception(str(exc))
        return []


def iter_pypi_projects(storage_pool, node_args):
    try:
        return storage_pool.get('PyPIListingTask')
    except Exception as exc:
        _LOGGER.exception(str(exc))
        return []
