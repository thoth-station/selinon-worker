#!/usr/bin/bash

set -ex

pipenv run selinon-cli -vvv plot --nodes-definition thoth/worker/config/nodes.yaml --flow-definitions thoth/worker/config/flows --output-dir fig/ --format png

