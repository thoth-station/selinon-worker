import logging

from selinon import SelinonTask

import requests
from thoth.python import Source

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


PYPI = Source(url="https://pypi.org/simple")


class PyPIListingTask(SelinonTask):
    def run(self, node_args):
        return [{"package_name": package_name} for package_name in PYPI.get_packages()][:2]


class DownloadProjectInfoTask(SelinonTask):
    def run(self, node_args):
        assert "package_name" in node_args
        package_name = node_args["package_name"]

        # For now we retrieve description for the latest release.
        api_url = PYPI.get_api_url()
        response = requests.get(api_url + f"/{package_name}/json")
        response.raise_for_status()

        return response.json()
