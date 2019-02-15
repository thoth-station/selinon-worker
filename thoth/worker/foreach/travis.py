import logging

from selinon import StoragePool

_LOGGER = logging.getLogger(__name__)


def iter_travis_repos(storage_pool: StoragePool, node_args: dict) -> list:
    """Iterate over repos and extend node args with the repo name."""
    try:
        repos = storage_pool.get('TravisActiveRepos')

        new_node_args = []
        for repo in repos:
            new_node_args.append(dict(repo=repo, **node_args))

        return new_node_args
    except Exception as exc:
        _LOGGER.exception(str(exc))
        return []


def iter_travis_builds(storage_pool: StoragePool, node_args: dict) -> list:
    """Iterate over builds found and extend node args with the build information."""
    try:
        builds = storage_pool.get('TravisRepoBuilds')

        new_node_args = []
        for build in builds:
            new_node_args.append(dict(**build, **node_args))

        return new_node_args
    except Exception as exc:
        _LOGGER.exception(str(exc))
        return []


def iter_travis_builds_count(storage_pool: StoragePool, node_args: dict) -> list:
    """Iterate over build counts respecting offset so build id downloads can be done in parallel."""
    try:
        builds_count = storage_pool.get('TravisRepoBuildsCount')['count']

        new_node_args = []
        for offset in range(builds_count):
            new_node_args.append(dict(**node_args, offset=offset))

        return new_node_args
    except Exception as exc:
        _LOGGER.exception(str(exc))
        return []
