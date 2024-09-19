#!/bin/bash

BUILD_VERSION=GRCh$1
VCF_DIR=./data/input_vcfs/$BUILD_VERSION
INPUT_FILENAME=$2
INPUT_FILE=$VCF_DIR/$INPUT_FILENAME
SED_SCRIPT="/$3/d"
OUTPUT_FILE=$VCF_DIR/${INPUT_FILENAME/.vcf.gz/_2.vcf.gz}

zcat $INPUT_FILE | sed $SED_SCRIPT | bgzip > $OUTPUT_FILE