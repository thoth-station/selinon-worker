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
