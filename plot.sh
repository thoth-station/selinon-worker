#!/usr/bin/bash

set -ex

selinon-cli -vvv plot --nodes-definition demo_worker/config/nodes.yaml --flow-definitions demo_worker/config/flows --output-dir fig/ --format png

