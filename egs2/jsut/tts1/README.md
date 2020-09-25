# JSUT RECIPE

This is the recipe of Japanese single female speaker TTS model with [JSUT](https://sites.google.com/site/shinnosuketakamichi/publication/jsut) corpus.

See the following pages for the usage:
- [How to run the recipe](../../TEMPLATE/tts1/README.md#how-to-run)
- [How to train FastSpeech](../../TEMPLATE/tts1/README.md#fastspeech-training)
- [How to train FastSpeech2](../../TEMPLATE/tts1/README.md#fastspeech-training2)

See the following pages before asking the question:
- [ESPnet2 Tutorial](https://espnet.github.io/espnet/espnet2_tutorial.html)
- [ESPnet2 TTS FAQ](../../TEMPLATE/tts1/README.md#faq)

# INITIAL RESULTS

## Environments

- date: `Sun Sep 20 19:04:37 JST 2020`
- python version: `3.7.3 (default, Mar 27 2019, 22:11:17)  [GCC 7.3.0]`
- espnet version: `espnet 0.9.3`
- pytorch version: `pytorch 1.6.0`
- Git hash: `08b981aa61e6d4fc951af851f0fa4ebb14f00d4c`
  - Commit date: `Sun Sep 20 02:21:47 2020 +0000`

## Pretrained Models

### jsut_tts_train_tacotron2_raw_phn_jaconv_pyopenjtalk_train.loss.best
- https://zenodo.org/record/3963886

### jsut_tts_train_fastspeech_raw_phn_jaconv_pyopenjtalk_train.loss.best
- https://zenodo.org/record/3986225

### jsut_tts_train_fastspeech2_raw_phn_jaconv_pyopenjtalk_train.loss.ave
- https://zenodo.org/record/4032224

### jsut_tts_train_conformer_fastspeech2_raw_phn_jaconv_pyopenjtalk_train.loss.ave
- https://zenodo.org/record/4032246

### jsut_tts_train_transformer_raw_phn_jaconv_pyopenjtalk_train.loss.ave
- https://zenodo.org/record/4034121