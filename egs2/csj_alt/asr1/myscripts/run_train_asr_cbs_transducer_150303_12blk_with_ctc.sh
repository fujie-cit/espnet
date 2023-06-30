#!/usr/bin/env bash
# Set bash to 'debug' mode, it will exit on :
# -e 'error', -u 'undefined variable', -o ... 'error in pipeline', -x 'print commands',
set -e
set -u
set -o pipefail

train_set=train_nodup
valid_set=train_dev
test_sets="eval1 eval2 eval3"

asr_config=myconf/train_asr_cbs_transducer_150303_12blk_with_ctc.yaml
inference_config=myconf/decode_cbs_transducer.yaml
asr_tag=train_asr_cbs_transducer_150303_12blk_with_ctc
inference_asr_model=valid.cer_transducer.ave.pth

pretrained_model=exp/asr_train_asr_cbs_transducer_120306_12blk_with_ctc/valid.cer_transducer.ave_10best.pth

lm_config=conf/train_lm.yaml
use_lm=false
use_wordlm=false

# speed perturbation related
# (train_set will be "${train_set}_sp" if speed_perturb_factors is specified)
# speed_perturb_factors="0.9 1.0 1.1"

./asr.sh                                               \
    --ngpu 2                                           \
    --use_streaming false                              \
    --lang jp                                          \
    --feats_type raw                                   \
    --token_type word                                  \
    --lm_config "${lm_config}"                         \
    --use_lm ${use_lm}                                 \
    --use_word_lm ${use_wordlm}                        \
    --asr_config "${asr_config}"                       \
    --asr_tag "${asr_tag}"                             \
    --inference_config "${inference_config}"           \
    --inference_asr_model "${inference_asr_model}"     \
    --train_set "${train_set}"                         \
    --valid_set "${valid_set}"                         \
    --test_sets "${test_sets}"                         \
    --pretrained_model "${pretrained_model}"           \
    "$@"
