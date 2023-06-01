#!/usr/bin/env bash

. ./path.sh
set -e # exit on error

#check existing directories
if [ $# != 1 ]; then
  echo "Usage: data_indiv.sh <CSJTOPDIR>"
  exit 1;
fi

CSJTOPDIR=$1
WAV_DIR="${CSJTOPDIR}/WAV"
TRN_DIR="${CSJTOPDIR}/TRN"
INDIV_DIR="data/indiv"

# WAV_DIR内の.wavファイルを再帰的に検索し、処理を行う
find "${WAV_DIR}" -type f -name "*[0-9].wav" | while IFS= read -r wav_file; do
    base_name=$(basename "${wav_file}")
    file_name="${base_name%.*}"
    extension="${base_name##*.}"

    trn_file=$(find "${TRN_DIR}" -type f -name "${file_name}.trn" | head -n 1)
    indiv_dir="${INDIV_DIR}/${file_name}"

    if [ ! -d "${indiv_dir}" ]; then
        mkdir -p "${indiv_dir}"
    fi

    echo python local/make_text_from_csj_trn.py "${trn_file}" "${indiv_dir}" tokenized_kana --wav_file_path "${wav_file}"
    python local/make_text_from_csj_trn.py \
          "${trn_file}" \
          "${indiv_dir}" \
          tokenized_kana \
          --wav_file_path "${wav_file}" \
          --para_info F,filler D,disfluency
    # utils/fix_data_dir.sh "${indiv_dir}"
done
