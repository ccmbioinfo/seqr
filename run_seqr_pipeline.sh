#!/bin/bash
#usage: ~/ccm_seqr/run_seqr_pipeline.sh <path_to_famID_txt> <path_to_vcf_folder> <sample_type> <genome_version>
#the VCF path would be the path after GRCh37/38 folder ex: Muise/C1012

input_vcf_fam_list=$1
vcf_folder=$2
sample_type=$3
genome_version=$4

while read -r fam
do
echo $fam
vcf=$(ls $fam*.vcf.gz)
index=$(echo $fam | tr '[:upper:]' '[:lower:]')
docker-compose exec pipeline-runner python3 -m seqr_loading SeqrMTToESTask --local-scheduler --reference-ht-path /seqr-reference-data/GRCh38/combined_reference_data_grch38.ht --clinvar-ht-path /seqr-reference-data/GRCh38/clinvar.GRCh38.ht --vep-config-json-path /vep_configs/vep-GRCh38-loftee.json --es-host elasticsearch --es-index-min-num-shards 1 --sample-type WES --es-index musie_japanese --genome-version 38 --source-paths /input_vcfs/GRCh38/Muise/japanese_cohort/musie_japanese.vcf.gz --dest-path /input_vcfs/GRCh38/Muise/japanese_cohort/musie_japanese.mt --dont-validate > pipeline-logs/err_file_musie_japanese-dontval.txt
tmux new-session -d -s $fam
tmux send-keys -t $fam ${tmux_commad} ENTER
echo 'moving to the next'
done < $input_vcf_fam_list
