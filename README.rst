thoth-worker
------------

A worker implementation for running workflows - used for data gathering for
project Thoth.

The worker implementation is an implementation of Selinon's worker - see `Selinon <https://github.com/selinon/selinon>`_ and `Selinon <https://selinon.readthedocs.io>`_ docs for more info.


Visualizing flows
=================

To visualize available flows, visually show which storage adapters are used for which flows as well as how tasks are grouped, you can issue the following command that places SVG images into ``fig/`` directory.
.. code-block::

  pipenv run selinon-cli -vvv plot --nodes-definition thoth/worker/config/nodes.yaml --flow-definitions thoth/worker/config/flows --output-dir fig

Running thoth-worker in the cluster
===================================

There is assigned a namespace to run thoth-worker and data aggregation part (ping someone from Thoth team on AICoE channel). The main interaction point is an `API service <https://github.com/thoth-station/selinon-api>`_.

Running thoth-worker locally
============================

All workflows are primarily designed to be run in the cluster, but Selinon offers a simple CLI interface to run flows locally.

Please configure AICoE gopass for passwords management (ping somebody on AICoE channel for more info), you can inject your passwords into your environment by running:

.. code-block:: console

  eval $(gopass show aicoe/thoth/ceph.sh)
  export THOTH_CEPH_BUCKET_PREFIX=data/thoth/$USER/

Please export ``THOTH_CEPH_BUCKET_PREFIX`` with your username as shown above so you do not clash with data used in the cluster - this way you will work with your own copy of data.

Before running flows, install all the requirements:

.. code-block:: console

  pipenv install

Now you are able to run Selinon flows, to run keywords gathering flow, issue the following command:

.. code-block:: console


  export PYTHONPATH=.
  pipenv run selinon-cli -vvv execute --nodes-definition thoth/worker/config/nodes.yaml --flow-definitions thoth/worker/config/flows --flow-name keywords


If you would like to run only some of the tasks in defined flows, feel free to use selective flow runs (see `docs <https://selinon.readthedocs.io/en/latest/selective.html>`_ for more info):

.. code-block:: console

  pipenv run selinon-cli -vvv execute --nodes-definition thoth/worker/config/nodes.yaml --flow-definitions thoth/worker/config/flows --flow-name keywords --selective-task-names StackOverflowKeywordsAggregationTask

To see all the available flows, reach out to ``flows`` section in the ``thoth/worker/config/nodes.yaml`` file. It has a descriptive information with listing of all the available flows and arguments that are requested (you can specify arguments for CLI run via ``--node-args``, do not forget to use ``-j`` for JSON arguments).

It can be also useful to set ``--sleep-time`` to 0 for selinon-cli, not to wait for scheduler to schedule flows in large flow runs.
