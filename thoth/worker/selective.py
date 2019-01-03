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

"""Implementation of selective run functions used in selective flow runs."""


def no_run_generic(flow_name, node_name, node_args, task_names, storage_pool):
    """Do not run task on selective flow runs.

    This is useful in scenario where we do not not use task_id when storing results of tasks.
    """
    return "@id"
