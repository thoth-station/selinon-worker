#!/usr/bin/bash

set -ex

selinon-cli -vvv plot --nodes-definition thoth_worker/config/nodes.yaml --flow-definitions thoth_worker/config/flows --output-dir fig/ --format png

