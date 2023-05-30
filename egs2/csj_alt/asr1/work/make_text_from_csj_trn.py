import os
import re


# カナ表記('|'区切り)の文字列を，スペース区切りのカナの列にする        
_kanas = """ア イ ウ エ オ カ キ ク ケ コ ガ ギ グ ゲ ゴ サ シ ス セ ソ
ザ ジ ズ ゼ ゾ タ チ ツ テ ト ダ デ ド ナ ニ ヌ ネ ノ ハ ヒ フ ヘ ホ
バ ビ ブ ベ ボ パ ピ プ ペ ポ マ ミ ム メ モ ラ リ ル レ ロ ヤ ユ ヨ
ワ ヲ ン ウィ ウェ ウォ キャ キュ キョ ギャ ギュ ギョ シャ シュ ショ
ジャ ジュ ジョ チャ チュ チョ ディ ドゥ デュ ニャ ニュ ニョ ヒャ ヒュ ヒョ
ビャ ビュ ビョ ピャ ピュ ピョ ミャ ミュ ミョ リャ リュ リョ イェ クヮ
グヮ シェ ジェ ティ トゥ チェ ツァ ツィ ツェ ツォ ヒェ ファ フィ フェ フォ フュ
テュ ブィ ニェ ミェ スィ ズィ ヴァ ヴィ ヴ ヴェ ヴォ ー ッ | <sp>"""
_kana_list = [x.replace(' ', '') for x in _kanas.replace('\n', ' ').split(' ')]
# 長さの降順にソート
_kana_list = sorted(_kana_list, key=len, reverse=True)

# カナ表記の文字列を，カナのリストにする
def kana_string_to_list(string):
    """カナ表記の文字列を，カナのリストにする

    Args:
        string (str): カナ表記の文字列

    Returns:
        list: カナのリスト
    """
    result = []
    while len(string) > 0:
        for kana in _kana_list:
            if string.startswith(kana):
                result.append(kana)
                string = string[len(kana):]
                break
        else:
            raise Exception(f'Invalid kana string: {string}')
    return result

def convert_tagged_kana_string_to_kana_list_and_paralinguistic_info(string):
    def extract_tag_string(s):
        if len(s) == 0:
            return '', ''
        if s[0] != '(':
            raise ValueError('タグの始まりではありません')
        stack = []
        for i, c in enumerate(s):
            if c == '(':
                stack.append(i)
            elif c == ')':
                stack.pop()
                if len(stack) == 0:
                    return s[:i+1], s[i+1:]
        raise ValueError('タグの終わりが見つかりません')
    
    def split_content_with_semicolon_or_comma(content):
        result = []
        prev = 0
        open_parenthesis_count = 0
        for i, c in enumerate(content):
            if c in (';', ','):
                if open_parenthesis_count == 0:
                    result.append(content[prev:i])
                    prev = i + 1
            elif c == '(':
                open_parenthesis_count += 1
            elif c == ')':
                open_parenthesis_count -= 1
        result.append(content[prev:])
        return result

    tag2label_tag = {'D2': 'D'}
    def extract_text_from_tagged_string(s):
        # 空文字列の場合は～文字列を返す
        if len(s) == 0:
            return ''

        result = []
        result_tag = []

        while len(s) > 0:
            # タグが始まる前の部分を取り出す
            match = re.match(r'^([^(]+)(.*)$', s)
            if match:
                kana_list = kana_string_to_list(match.group(1))
                result.extend(kana_list)
                result_tag.extend(['N'] * len(kana_list))

                s = match.group(2)
            else:
                # 最長一致でタグの部分を取り出す
                tagged_string, s = extract_tag_string(s)
                match_ = re.match(r'^\(([^ ]+) (.+)\)$', tagged_string)
                if not match_:
                    if tagged_string == '(?)':
                        continue
                    elif tagged_string == '(L )':
                        # 1例 (L <FV>) というものがあることを確認
                        continue
                    else:
                        raise Exception('Invalid tagged string: {}'.format(tagged_string))
                tag = match_.group(1)
                content = match_.group(2)
                # タグごとにコンテンツの絞り込みをする
                if tag in ('F', 'D', 'D2', 'M', 'O', 'X', '笑', '泣', '咳', 'L'):
                    # これらのタグの場合はそのまま
                    pass
                else:
                    # とりあえずセミコロンとカンマで分割
                    contents = split_content_with_semicolon_or_comma(content)
                    if tag == '?':
                        # ? の場合は最初の要素だけ
                        content = contents[0]
                    elif tag in ('W', 'B'):
                        # W, B の場合は最初の要素だけ
                        content = contents[0]
                    else:
                        raise Exception('Unknown tag: {}'.format(tag))

                if tag in tag2label_tag:
                    label_tag = tag2label_tag[tag]
                else:
                    label_tag = tag
                # content がタグを含む場合は再帰処理をする
                if '(' in content:
                    kana_list, tag_list = extract_text_from_tagged_string(content)
                    tag_list = [t + label_tag for t in tag_list]
                else:
                    kana_list = kana_string_to_list(content)
                    tag_list = ['N'+label_tag] * len(kana_list)
                result.extend(kana_list)
                result_tag.extend(tag_list)
                
        return result, result_tag

    return extract_text_from_tagged_string(string)

def make_text_separated_kana(flattened_trn,
                             remove_word_sep=False, remove_sp=False,
                             remove_privacy_utt=True,
                             remove_extra_content=True):
    """カナ文のスペース区切りのリスト，およびパラ言語情報のスペース区切りリストを作成する
    """
    texts = []
    tags = []
    segments = []

    lecture_id = flattened_trn['lecture_id']
    for utterance in flattened_trn['flattened_utterances']:
        start = utterance['start']
        end = utterance['end']
        if lecture_id[0] == 'D':
            lecture_id_with_ch = lecture_id + utterance['channel']
        else:
            lecture_id_with_ch = lecture_id
        utt_id = f"{lecture_id_with_ch}_" + \
                 f"{int(start):04d}{int(start*1000)%1000:03d}_" + \
                 f"{int(end):04d}{int(end*1000)%1000:03d}"

        text = utterance['kana_text']

        # ボーカルフライ
        text = text.replace('<FV>', '')
        # うん/うーん/ふーん の音が特定困難な場合
        # 本来は基本形の文字列をカタカナ化したものを持ってきたい．
        text = text.replace('<VN>', 'ウン')        
        # 非語彙的な母音の引き延ばし
        text = text.replace('<H>', 'ー')
        # 非語彙的な子音の引き延ばし
        text = text.replace('<Q>', '')
        # 笑，咳，息
        text = text.replace('<笑>', '')
        text = text.replace('<咳>', '')
        text = text.replace('<息>', '')

        if remove_privacy_utt:
            if 'R' in text:
                continue
        if remove_extra_content:
            # '<' '>' で囲まれた文字列を削除
            text = re.sub(r'(?<!<sp>)<[^>]+>', '', text)
        if remove_word_sep:
            text = text.replace('|', '')
        if remove_sp:
            text = text.replace('<sp>', '')
        if len(text) == 0:
            continue

        kana_list, tag_list = convert_tagged_kana_string_to_kana_list_and_paralinguistic_info(text)

        texts.append(f"{utt_id} {' '.join(kana_list)}")
        tags.append(f"{utt_id} {' '.join(tag_list)}")
        segments.append(f"{utt_id} {start:.3f} {end:.3f}")

    return texts, tags, segments

def remove_tags_kana(string):
    """カナ文字列からタグを除去する.

    Args:
        string (str): 平文の文字列

    Returns:
        str: タグを除去した文字列
    """
    def extract_tag_string(s):
        if len(s) == 0:
            return '', ''
        if s[0] != '(':
            raise ValueError('タグの始まりではありません')
        stack = []
        for i, c in enumerate(s):
            if c == '(':
                stack.append(i)
            elif c == ')':
                stack.pop()
                if len(stack) == 0:
                    return s[:i+1], s[i+1:]
        raise ValueError('タグの終わりが見つかりません')

    def extract_text_from_tagged_string(s):
        # 空文字列の場合は～文字列を返す
        if len(s) == 0:
            return ''

        result = ''

        while len(s) > 0:
            # タグが始まる前の部分を取り出す
            match = re.match(r'^([^(]+)(.*)$', s)
            if match:
                result += match.group(1)
                s = match.group(2)
            else:
                # 最長一致でタグの部分を取り出す
                tagged_string, s = extract_tag_string(s)
                match_ = re.match(r'^\(([^ ]+) (.+)\)$', tagged_string)
                if not match_:
                    if tagged_string == '(?)':
                        continue
                    elif tagged_string == '(L )':
                        # 1例 (L <FV>) というものがあることを確認
                        continue
                    else:
                        raise Exception('Invalid tagged string: {}'.format(tagged_string))
                tag = match_.group(1)
                content = match_.group(2)
                # print(tag, content)
                # content がタグを含む場合は再帰処理をする
                if '(' in content:
                    content = extract_text_from_tagged_string(content)
                # タグごとの処理
                if tag in ('F', 'D', 'D2', 'M', 'O', 'X', '笑', '泣', '咳', 'L'):
                    pass
                elif tag == '?':
                    content = content.split(',')[0]
                elif tag in ('W', 'B'):
                    content = content.split(';')[0]
                else:
                    raise Exception(f'Unknown tag: {tag}')
                result += content
                
        return result

    return extract_text_from_tagged_string(string)


def make_text_kana(flattened_trn,
                   remove_word_sep=False, remove_sp=True,
                   remove_privacy_utt=True,
                   remove_extra_content=True,
                   remove_tags=True):
    """カナ文の標準テキストを作成する
    """
    texts = []
    segments = []

    lecture_id = flattened_trn['lecture_id']
    for utterance in flattened_trn['flattened_utterances']:
        start = utterance['start']
        end = utterance['end']
        if lecture_id[0] == 'D':
            lecture_id_with_ch = lecture_id + utterance['channel']
        else:
            lecture_id_with_ch = lecture_id
        utt_id = f"{lecture_id_with_ch}_" + \
                 f"{int(start):04d}{int(start*1000)%1000:03d}_" + \
                 f"{int(end):04d}{int(end*1000)%1000:03d}"

        text = utterance['kana_text']

        # ボーカルフライ
        text = text.replace('<FV>', '')
        # うん/うーん/ふーん の音が特定困難な場合
        # 本来は基本形の文字列をカタカナ化したものを持ってきたい．
        text = text.replace('<VN>', 'ウン')        
        # 非語彙的な母音の引き延ばし
        text = text.replace('<H>', 'ー')
        # 非語彙的な子音の引き延ばし
        text = text.replace('<Q>', '')
        # 笑，咳，息
        text = text.replace('<笑>', '')
        text = text.replace('<咳>', '')
        text = text.replace('<息>', '')

        if remove_privacy_utt:
            if 'R' in text:
                continue
        if remove_extra_content:
            # '<' '>' で囲まれた文字列を削除
            text = re.sub(r'(?<!<sp>)<[^>]+>', '', text)
        if remove_word_sep:
            text = text.replace('|', '')
        if remove_sp:
            text = text.replace('<sp>', '')
        if remove_tags:
            text = remove_tags_kana(text)
        if len(text) == 0:
            continue

        texts.append(f"{utt_id} {text}")
        segments.append(f"{utt_id} {start:.3f} {end:.3f}")

    return texts, segments


def remove_tags_plain(string):
    """平文の文字列からタグを除去する.

    Args:
        string (str): 平文の文字列

    Returns:
        str: タグを除去した文字列
    """
    def extract_tag_string(s):
        if len(s) == 0:
            return '', ''
        if s[0] != '(':
            raise ValueError('タグの始まりではありません')
        stack = []
        for i, c in enumerate(s):
            if c == '(':
                stack.append(i)
            elif c == ')':
                stack.pop()
                if len(stack) == 0:
                    return s[:i+1], s[i+1:]
        raise ValueError('タグの終わりが見つかりません')

    def extract_text_from_tagged_string(s):
        # 空文字列の場合は～文字列を返す
        if len(s) == 0:
            return ''

        result = ''

        while len(s) > 0:
            # タグが始まる前の部分を取り出す
            match = re.match(r'^([^(]+)(.*)$', s)
            if match:
                result += match.group(1)
                s = match.group(2)
            else:
                # 最長一致でタグの部分を取り出す
                tagged_string, s = extract_tag_string(s)
                match_ = re.match(r'^\(([^ ]+) (.+)\)$', tagged_string)
                if not match_:
                    if tagged_string == '(?)':
                        continue
                    else:
                        raise Exception('Invalid tagged string: {}'.format(tagged_string))
                tag = match_.group(1)
                content = match_.group(2)
                # print(tag, content)
                # content がタグを含む場合は再帰処理をする
                if '(' in content:
                    content = extract_text_from_tagged_string(content)
                # タグごとの処理
                if tag in ('F', 'D', 'D2', 'M', 'O', 'X'):
                    pass
                elif tag == '?':
                    content = content.split(',')[0]
                elif tag == 'A':
                    contents = content.split(';')
                    c0 = contents[0]
                    c1 = contents[1]
                    if re.match(r'^[０-９．]+$', c1):
                        content = c0
                    else:
                        content = c1
                elif tag == 'K':
                    content = content.split(';')[0]
                else:
                    raise Exception(f'Unknown tag: {tag}')
                result += content
                
        return result

    return extract_text_from_tagged_string(string)


def make_text_plain(flattened_trn,
                    remove_word_sep=True, remove_sp=True,
                    remove_privacy_utt=True,
                    remove_extra_content=True,
                    remove_tags=True):
    texts = []
    segments = []

    lecture_id = flattened_trn['lecture_id']
    for utterance in flattened_trn['flattened_utterances']:
        start = utterance['start']
        end = utterance['end']
        if lecture_id[0] == 'D':
            lecture_id_with_ch = lecture_id + utterance['channel']
        else:
            lecture_id_with_ch = lecture_id
        utt_id = f"{lecture_id_with_ch}_" + \
                 f"{int(start):04d}{int(start*1000)%1000:03d}_" + \
                 f"{int(end):04d}{int(end*1000)%1000:03d}"

        text = utterance['plain_text']

        if remove_privacy_utt:
            if 'R' in text:
                continue
        if remove_extra_content:
            # '<' '>' で囲まれた文字列を削除
            text = re.sub(r'<[^>]*>', '', text)
        if remove_word_sep:
            text = text.replace('|', '')
        if remove_sp:
            text = text.replace('<sp>', '')
        if remove_tags:
            text = remove_tags_plain(text)
        if len(text) == 0:
            continue

        texts.append(f"{utt_id} {text}")
        segments.append(f"{utt_id} {start:.3f} {end:.3f}")

    return texts, segments

def flat_utterances(parsed_or_connected_trn, 
                    word_sep='|', remove_extra_content=False, 
                    utt_sep='<sp>', ):
    """TRNファイルの解析結果の中の発話（utterance）を, 平坦化した文字列に変換する.

    Args:
        parsed_or_connected_trn (dict): parse_trn_file() または connect_utterances() の出力
        word_sep (str, optional): 単語間の区切り文字. Defaults to '|'.
        remove_extra_content (bool, optional): Trueの場合, extra_contentを除去する. Defaults to False.
        utt_sep (str, optional): 発話間の区切り文字. Defaults to '<sp>'.

    Returns:
        dict: 平坦化された発話を含む辞書型のデータ            
    """
    output = {
        'lecture_id': parsed_or_connected_trn['lecture_id'],
    }
    is_connected = 'connected_utterances' in parsed_or_connected_trn
    if is_connected:
        utterances = parsed_or_connected_trn['connected_utterances']
    else:
        utterances = parsed_or_connected_trn['utterances']
    
    flattened_utterances = []
    for utterance in utterances:
        if not is_connected:
            utterance = [utterance]
        
        if remove_extra_content:
            utterance = [u for u in utterance if 'extra_content' not in u]
        if len(utterance) == 0:
            continue

        flattend_utterance = {
            'id': utterance[0]['id'],
            'start': utterance[0]['start'],
            'end': utterance[-1]['end'],
            'channel': utterance[0]['channel'],
        }

        plain_text = ''
        kana_text = ''
        for u in utterance:
            if 'extra_content' in u:
                plain_text += u['extra_content']
                kana_text += u['extra_content']
            else:
                plain_text += word_sep.join([word[0] for word in u['words']])
                kana_text += word_sep.join([word[1] for word in u['words']])
            plain_text += utt_sep
            kana_text += utt_sep
        plain_text = plain_text[:-len(utt_sep)]
        kana_text = kana_text[:-len(utt_sep)]
        
        flattend_utterance['plain_text'] = plain_text
        flattend_utterance['kana_text'] = kana_text
        flattened_utterances.append(flattend_utterance)

    output['flattened_utterances'] = flattened_utterances

    return output


def connect_utterances(parsed_trn, 
                       gap: float=0.5, max: float=10.0,
                       isolate_extra_content: bool=True):
    """TRNファイルの解析結果の中の発話（utterance）を, 
    発話間のポーズや発話の長さに基づいて接続する.

    Args:
        parsed_trn (dict): parse_trn_file() の出力
        gap (float, optional): 発話間のポーズの最大長さ. この長さを超えるポーズでは発話を分割する.
                                Defaults to 0.5.
        max (float, optional): 発話の最大長さ. 接続後の発話長がこの長さを超えないようにする. Defaults to 10.0.
        isolate_extra_content (bool, optional): Trueの場合, extra_contentは単独発話として扱う. Defaults to True.
    
    Returns:
        dict: 接続された発話を含む辞書型のデータ
    """
    output = {
        'lecture_id': parsed_trn['lecture_id'],
    }

    # utterance のリストのリスト
    connected_utterances = []
    # utterance のリスト（接続された発話のリスト）
    connected_utterance = []
    # 接続された発話の中に含まれる開いた括弧の数
    num_open_parentheses = 0
    for utterance in parsed_trn['utterances']:
        local_num_open_parentheses = sum([w[0].count('(') - w[0].count(')') for w in utterance['words']])
        # print(num_open_parentheses, local_num_open_parentheses, ''.join([w[0] for w in utterance['words']]), utterance.get('extra_content', ''))
        if len(connected_utterance) == 0:
            connected_utterance.append(utterance)
            num_open_parentheses = local_num_open_parentheses
            continue
        prev_utterance = connected_utterance[-1]
        if num_open_parentheses > 0:
            if 'extra_content' not in utterance:
                connected_utterance.append(utterance)
                num_open_parentheses += local_num_open_parentheses
            else:
                # タグ内の単独の<雑音>などは接続しない
                pass
        elif isolate_extra_content and 'extra_content' in prev_utterance:
            connected_utterances.append(connected_utterance)
            connected_utterance = [utterance]
            num_open_parentheses = local_num_open_parentheses
        elif utterance['start'] - prev_utterance['end'] < gap and \
              utterance['end'] - connected_utterance[0]['start'] < max and \
              utterance['channel'] == prev_utterance['channel'] and \
              (not isolate_extra_content or 'extra_content' not in utterance):
            connected_utterance.append(utterance)
            num_open_parentheses += local_num_open_parentheses
        else:
            connected_utterances.append(connected_utterance)
            connected_utterance = [utterance]
            num_open_parentheses = local_num_open_parentheses
    if len(connected_utterance) > 0:
        connected_utterances.append(connected_utterance)
    
    output['connected_utterances'] = connected_utterances

    return output


def parse_trn_file(filename, encoding='shift_jis'):
    """TRNファイルを解析して辞書型のデータに変換する
    
    Args:
        filename (str): TRNファイルのパス
        encoding (str, optional): TRNファイルのエンコーディング. Defaults to 'shift_jis'.

    Returns:
        dict: TRNファイルの内容を辞書型に変換したもの
    """
    with open(filename, 'r', encoding=encoding) as file:
        lines = file.readlines()

    lecture_id = None
    utterances = []
    current_utterance = None

    for line in lines:
        line = line.strip()

        if line.startswith('%講演ID:'):
            lecture_id = line.split(':')[1]
        elif len(line) > 0 and line[0].isdigit():
            if current_utterance:
                utterances.append(current_utterance)
            utterance_id, time_range, channel = line.split(' ')
            channel, extra_content = channel.split(':')
            start_time, end_time = map(float, time_range.split('-'))
            current_utterance = {
                'id': int(utterance_id),
                'start': start_time,
                'end': end_time,
                'channel': channel,
                'words': []
            }
            if extra_content != '':
                current_utterance['extra_content'] = extra_content
        elif line.startswith('%'):
            continue
        else:
            words = line.split('&')
            assert len(words) == 2
            words = tuple([word.strip() for word in words])
            current_utterance['words'].append(words)

    if current_utterance:
        utterances.append(current_utterance)

    output = {
        'lecture_id': lecture_id,
        'utterances': utterances
    }

    return output


__check_list = [
    "_",
    "(M (O _))",
    "(M (F _)_)",
    "(M (F _))",
    "(? _,_)",
    "(X (D _))",
    "(X _)",
    "(M (? _))",
    "(X (F _))",
    "(M (A _;_))",
    "(X (D (? _)))",
    "(O (? _))",
    "(M (D _))",
    "(M (O (? _)))",
    "(X (D2 _))",
    "(K _;_)",
    "(M (A _;_;_))",
    "(? (A _;_))",
    "(? (F _))",
    "(M _;_)",
    "(M (M _))",
    "(X (F (? _)))",
    "(F (? _,_))",
    "(? (F _,_))",
    "(M _;_;_)",
    "(? _,_;_)",
    "(? _,_,_)",
    "(? (D _))"
]

def remove_plain_tags(string):

    def extract_tag_string(s):
        if len(s) == 0:
            return '', ''
        if s[0] != '(':
            raise ValueError('タグの始まりではありません')
        stack = []
        for i, c in enumerate(s):
            if c == '(':
                stack.append(i)
            elif c == ')':
                stack.pop()
                if len(stack) == 0:
                    return s[:i+1], s[i+1:]
        raise ValueError('タグの終わりが見つかりません')

    def extract_text_from_tagged_string(s):
        # 空文字列の場合は～文字列を返す
        if len(s) == 0:
            return ''

        result = ''

        while len(s) > 0:
            # タグが始まる前の部分を取り出す
            match = re.match(r'^([^(]+)(.*)$', s)
            if match:
                result += match.group(1)
                s = match.group(2)
            else:
                # 最長一致でタグの部分を取り出す
                tagged_string, s = extract_tag_string(s)
                match_ = re.match(r'^\(([^ ]+) (.+)\)$', tagged_string)
                if not match_:
                    if tagged_string == '(?)':
                        continue
                    else:
                        raise Exception('Invalid tagged string: {}'.format(tagged_string))
                tag = match_.group(1)
                content = match_.group(2)
                # print(tag, content)
                # content がタグを含む場合は再帰処理をする
                if '(' in content:
                    content = extract_text_from_tagged_string(content)
                # タグごとの処理
                if tag in ('F', 'D', 'D2', 'M', 'O', 'X'):
                    pass
                elif tag == '?':
                    content = content.split(',')[0]
                elif tag == 'A':
                    contents = content.split(';')
                    c0 = contents[0]
                    c1 = contents[1]
                    if re.match(r'^[０-９．]+$', c1):
                        content = c0
                    else:
                        content = c1
                elif tag == 'K':
                    content = content.split(';')[0]
                else:
                    raise Exception(f'Unknown tag: {tag}')
                result += content
                
        return result

    return extract_text_from_tagged_string(string)


def __extract_tagged_strings(string):
    def convert_tag_string_without_content(s):
        match = re.match(r'^\([^ )]+\)$', s)
        if match:
            # print(s)
            return s
        match = re.match(r'^([^()]*)\(([^ ]+) (.+)\)([^())]*)$', s)
        if match:
            part1 = match.group(1)
            part2 = match.group(2)
            part3 = match.group(3)
            part4 = match.group(4)
            
            # if '(' not in part3 and ')' not in part3:
            #     if part2 not in ('F', 'D', 'D2', 'M', 'A', 'O', '?') or (part2 == '?' and ',' in part3):
            #         print(f"({part2} {part3})")
            
            converted_part1 = convert_tag_string_without_content(part1) if len(part1) > 0 else ''
            converted_part3 = convert_tag_string_without_content(part3) if len(part3) > 0 else ''
            converted_part4 = convert_tag_string_without_content(part4) if len(part4) > 0 else ''
            return f'{converted_part1}({part2} {converted_part3}){converted_part4}'
        
        result = ''
        for sc in s.split(';'):
            for cm in sc.split(','):
                result += '_,'
            result = result[:-1] + ';'
        return result[:-1]

    result = []
    stack = []
    start_index = 0

    for i, char in enumerate(string):
        if char == '(':
            stack.append(i)
        elif char == ')':
            if stack:
                start_index = stack.pop()
                if len(stack) > 0:
                    continue
                tagged_string = string[start_index:i+1]
                print(tagged_string)
                converted_tagged_string =convert_tag_string_without_content(tagged_string)
                # if converted_tagged_string in __check_list:
                #     print(f"{tagged_string} -> {converted_tagged_string}")
                result.append(converted_tagged_string)
            else:
                raise ValueError("Unbalanced parentheses")

    if stack:
        raise ValueError("Unbalanced parentheses")

    return result

if __name__ == "__main__":
    CSJ_PATH = "/autofs/diamond/share/corpus/CSJ"
    TRN_PATH = os.path.join(CSJ_PATH, "TRN/Form1")
    TRN_FILE = os.path.join(TRN_PATH, "core", "A01F0055.trn")
    # TRN_FILE = os.path.join(TRN_PATH, "noncore", "A01F0019.trn")
    # TRN_FILE = os.path.join(TRN_PATH, "core", "D01F0002.trn")
    OUT_FILE = os.path.basename(TRN_FILE).replace(".trn", ".txt")

    import glob
    from tqdm import tqdm

    tagged_token_count = {}
    tag_count = {}

    generator = tqdm(sorted(glob.glob(os.path.join(TRN_PATH, "**", "*.trn"), recursive=True)))
    # generator = sorted(glob.glob(os.path.join(TRN_PATH, "**", "*.trn"), recursive=True))
    for trn_file in generator:
        parsed = parse_trn_file(trn_file)
        connected = connect_utterances(parsed)
        flattened = flat_utterances(connected)
        texts, tags, segments = make_text_separated_kana(flattened)
        # for text, tag in zip(texts, tags):
        #     for te, ta in zip(text.split(' '), tag.split(' ')):
        #         ta = ta.replace('N', '')
        #         if len(ta) == 0:
        #             print(f"[{te}] ", end='')
        #         else:
        #             print(f"[{te}+{ta}] ", end='')
        #     print("")
        # import ipdb; ipdb.set_trace()
        for line in tags:
            _, tt = line.split(' ', 1)
            for t in tt.split(' '):
                for ta in t:
                    tag_count[ta] = tag_count.get(ta, 0) + 1
        print(tag_count)

    # for text in texts:
    #     _, t = text.split(' ', 1)
    #     for tagged_string in __extract_tagged_strings(t):
    #         # print(tagged_string)
    #         tagged_token_count[tagged_string] = tagged_token_count.get(tagged_string, 0) + 1
    # # generator.set_postfix(tagged_string_count=len(tagged_token_count))

    # keys = sorted(tagged_token_count, key=tagged_token_count.get, reverse=True)
    # for k in keys:
    #     print(k, tagged_token_count[k])

