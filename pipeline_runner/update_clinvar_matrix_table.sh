#!/bin/bash

BUILD_VERSIONS=('37' '38')

for BUILD_VERSION in "${BUILD_VERSIONS[@]}"
do
  CLINVAR_HT=clinvar.GRCh${BUILD_VERSION}.ht
  rm -rf "/seqr-reference-data/GRCh${BUILD_VERSION}/${CLINVAR_HT}"
  mkdir -p "/seqr-reference-data/GRCh${BUILD_VERSION}/${CLINVAR_HT}"
  cd "/seqr-reference-data/GRCh${BUILD_VERSION}"
  gsutil -m rsync -r "gs://seqr-reference-data/GRCh${BUILD_VERSION}/clinvar/${CLINVAR_HT}" "./${CLINVAR_HT}"
done