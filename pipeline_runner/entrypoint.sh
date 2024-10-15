#!/usr/bin/env bash

# https://github.com/broadinstitute/seqr/blob/d80d7f4140b94b7a5b0417bc0b13a8602fb7f061/deploy/docker/pipeline-runner/Dockerfile#L98
# install VEP v104; replaces VEP v99 installed in the Docker image
cd /ensembl-vep-release-104
perl INSTALL.pl -a ap -n -l -g all
ln -sf /ensembl-vep-release-104/vep /vep

# Update Google Cloud components
gcloud components update --version=447.0.0 -q

set -x

# sleep to keep container running and available for kicking off pipelines
sleep 1000000000000
