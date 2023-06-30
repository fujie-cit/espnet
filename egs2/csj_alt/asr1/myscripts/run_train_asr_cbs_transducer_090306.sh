#!/usr/bin/env bash
# Set bash to 'debug' mode, it will exit on :
# -e 'error', -u 'undefined variable', -o ... 'error in pipeline', -x 'print commands',
set -e
set -u
set -o pipefail

train_set=train_nodup
valid_set=train_dev
test_sets="eval1 eval2 eval3"

asr_config=myconf/train_asr_cbs_transducer_090306.yaml
inference_config=myconf/decode_cbs_transdcuer.yaml
asr_tag=train_asr_cbs_transducer_090306

lm_config=conf/train_lm.yaml
# use_lm=true
# use_wordlm=false

# speed perturbation related
# (train_set will be "${train_set}_sp" if speed_perturb_factors is specified)
# speed_perturb_factors="0.9 1.0 1.1"

./asr.sh                                               \
    --ngpu 2                                           \
    --use_streaming true                               \
    --lang jp                                          \
    --feats_type raw                                   \
    --token_type word                                  \
    --asr_config "${asr_config}"                       \
    --asr_tag "${asr_tag}"                             \
    --inference_config "${inference_config}"           \
    --train_set "${train_set}"                         \
    --valid_set "${valid_set}"                         \
    --test_sets "${test_sets}"                         \
    --lm_train_text "data/${train_set}/text" "$@"

#    --lm_config "${lm_config}"                         \
#    --audio_format wav                                 \
#    --use_lm ${use_lm}                                 \
#    --use_word_lm ${use_wordlm}                        \
#    --speed_perturb_factors "${speed_perturb_factors}" \
#    --asr_speech_fold_length 512 \
#    --asr_text_fold_length 150 \
#    --lm_fold_length 150 \
