# 事前学習モデルによる音声認識
from espnet2.bin.asr_inference import Speech2Text
import soundfile as sf

# sound_file = "./dump/raw/eval/data/format.1/A02F0038_0000588_0008428.flac"
# sound_file = "./dump/raw/org/train/data/format.1/A01F0001_0032592_0041435.flac"
# sound_file = "./dump/raw/eval/data/format.30/A02M0098_1339153_1343153.flac"
# sound_file = "./dump/raw/eval/data/format.30/A02M0098_1367472_1376604.flac"
# sound_file = "./dump/raw/eval/data/format.1/A02F0038_0042048_0048239.flac"
# sound_file = "./dump/raw/eval1/data/format.1/A01M0097_0226936_0236320.flac"

data = [
    ("./dump/raw/eval1/data/format.5/A01M0110_0385047_0394376.flac",
     "コ チ ラ ノ | ヨ ー イ ン ノ | ヒ ト ツ ト イ タ シ マ シ テ <sp> エ ー ゴ ダ ン セ ー ノ | ス ピ ー チ レ ー ト ガ <sp> タ ノ | オ ン セ ー ニ ク ラ ベ <sp> ヤ ヤ | ハ ヤ カ ッ タ | タ メ ト <sp> カ ン ガ エ テ オ リ マ ス"),
    ("./dump/raw/eval1/data/format.10/A03M0106_0703155_0712484.flac",
     "ア+F | ニュ ー | オ+D ー+D バ+D ー+D | ニュ ー | ワ ル | ア+F ー+F ノ+F | シュ+D <sp> オ ー ブ デ ス ネ <sp> デ | エ+F ー+F ト+F ー+F | ヤ ク ヨ ン ジュ ッ パ ー セ ン ト | ゲ ン ショ ー ト ユ ー | カ タ チ デ <sp> ア+F ノ+F | キ ホ ン テ キ ナ | エ+F ト+F | ホ ン ヤ ク セ ー ノ ー ガ | エ+F ー+F ト+F | ク+D ト+D ー+D タ+D")
]



# 音声認識器の作成
speech2text = Speech2Text(
    "./exp/asr_train_asr_conformer_raw_jp_word/config.yaml",
    "./exp/asr_train_asr_conformer_raw_jp_word/valid.acc.best.pth",
    # Decoding parameters are not included in the model file
    maxlenratio=0.0,
    minlenratio=0.0,
    beam_size=20,
    ctc_weight=0.3,
    lm_weight=0.5,
    penalty=0.0,
    nbest=10    
)

for sound_file, correct_text in data:
    # 音声ファイルの読み込み
    speech, rate = sf.read(sound_file)

    # 音声認識の実行
    nbests = speech2text(speech)

    # 認識結果の表示
    text, *_ = nbests[0]

    print(sound_file)
    print(f"[CORRECT] {correct_text}")
    print(f"[RECOG]   {text}")
