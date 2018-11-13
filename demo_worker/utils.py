#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ######################################################################
# Copyright (C) 2016-2018  Fridolin Pokorny, fridolin.pokorny@gmail.com
# This file is part of Selinon project.
# ######################################################################
"""Library utilities for Selinon demo app."""

import os

from selinon import Config

_BASE_NAME = os.path.join(os.path.dirname(os.path.relpath(__file__)), 'config')


def get_config_files():
    """Retrieve configuration files used in application."""
    flow_definition_files = []
    for conf_file in os.listdir(os.path.join(_BASE_NAME, 'flows')):
        if conf_file.endswith(('.yaml', '.yml')) and not conf_file.startswith('.'):
            flow_definition_files.append(os.path.join(_BASE_NAME, 'flows', conf_file))

    # We expect nodes.yaml to be present explicitly.
    return os.path.join(_BASE_NAME, 'nodes.yaml'), flow_definition_files


def init(with_result_backend=False):
    """Init Celery and Selinon.

    :param with_result_backend: true if the application should connect to the result backend
    :return: Celery application instance
    """
    # Avoid exception on CLI run.
    from celery import Celery

    conf = {
        'broker_url': os.environ['BROKER_URL']
    }

    if with_result_backend:
        conf['result_backend'] = os.environ['RESULT_BACKEND_URL']

    app = Celery('app')
    app.config_from_object(conf)

    # Set Selinon configuration.
    Config.set_config_yaml(*get_config_files())
    # Prepare Celery
    Config.set_celery_app(app)

    return app
