#!/usr/bin/env python3
# thoth-worker
# Copyright(C) 2018, 2019, 2020 Fridolin Pokorny
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

"""Selinon worker for Thoth to perform data aggregation and analysis for high volume data (parallel processing)."""

__name__ = "thoth.worker"
__version__ = "0.0.2"
__author__ = "Fridolin Pokorny"

from thoth.common import init_logging

from .utils import get_config_files
from .utils import init


# Init logging so we get errors reported.
init_logging()
