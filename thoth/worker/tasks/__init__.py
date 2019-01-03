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

"""Tasks available in Selinon worker for data aggregation and processing."""

import logging

# Turn off too verbose loggers.
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("libarchive").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

from .keywords import KeywordsAggregationTask
from .keywords import PyPIProjectKeywordsTask
from .keywords import StackOverflowKeywordsAggregationTask
from .project2vec import Project2VecCreationTask
from .project2vec import Project2VecTask
from .pypi import ProjectInfoTask
from .pypi import PyPIListingTask
from .pypi import RetrieveProjectReadmeTask
from .sync import GraphSyncAnalysisTask
from .sync import GraphSyncSolverTask
from .sync import SyncListingTask
