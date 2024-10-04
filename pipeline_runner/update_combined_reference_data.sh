#!/bin/bash

BUILD_VERSIONS=('37' '38')

for BUILD_VERSION in "${BUILD_VERSIONS[@]}"
do
  REF_DATA_HT=combined_reference_data_grch${BUILD_VERSION}.ht
  rm -rf "/seqr-reference-data/GRCh${BUILD_VERSION}/${REF_DATA_HT}"
  mkdir -p "/seqr-reference-data/GRCh${BUILD_VERSION}/${REF_DATA_HT}"
  cd "/seqr-reference-data/GRCh${BUILD_VERSION}"
  gsutil -m rsync -r "gs://seqr-reference-data/GRCh${BUILD_VERSION}/all_reference_data/${REF_DATA_HT}" "./${REF_DATA_HT}"
done