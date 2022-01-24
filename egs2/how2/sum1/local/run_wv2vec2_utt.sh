#!/bin/bash

set -e
set -u
set -o pipefail

train_set="tr_2000h"
valid_set="cv05"
#test_sets="dev5_test held_out_test"
test_sets="dev5_test_vid"
asr_config=conf/asr_wav2vec_ft.yaml
inference_config=conf/decode.yaml


feats_type=raw
token_type=bpe
nlsyms=data/nlsyms
nbpe=1000
bpe_nlsyms="[hes]"
use_lm=false
mdur=20



./asr.sh \
    --lang en \
    --feats_type ${feats_type} \
    --token_type ${token_type} \
    --nbpe ${nbpe} \
    --nlsyms_txt ${nlsyms} \
    --bpe_nlsyms ${bpe_nlsyms} \
    --use_lm ${use_lm} \
    --asr_config "${asr_config}" \
    --inference_config "${inference_config}" \
    --train_set "${train_set}" \
    --valid_set "${valid_set}" \
    --test_sets "${test_sets}" \
    --max_wav_duration "$mdur" \
    --feats_normalize null \
    --bpe_train_text "data/${train_set}/text" "$@"
