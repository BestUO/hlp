import re
import tensorflow as tf
from utils import get_config, get_word_index
import tensorflow as tf


#此方法依据文本是中文文本还是英文文本，若为英文文本是按字符切分还是按单词切分
def preprocess_sentence(str, mode):
    if mode == "cn":
        return preprocess_sentence_ch(str)
    elif mode == "en_word":
        return preprocess_sentence_en_word(str)
    else:
        return preprocess_sentence_en_char(str)

#基于数据文本规则的行获取
def text_row_process(str, row_style):
    if row_style == 1:
        #当前数据文本的每行为'index string\n'
        return str.strip().split(" ",1)[1].lower()
    elif row_style == 2:
        #当前数据文本的每行为'index\tstring\n'
        return str.strip().split("\t",1)[1].lower()
    else:
        #文本每行"string\n"
        return str.strip().lower()

# 非初次训练时，基于word_index和处理好的文本list得到数字list
def get_text_int_sequences(process_text_list, word_index):
    text_int_sequences = []
    for process_text in process_text_list:
        text_int_sequences.append(text_to_int_sequence(process_text, word_index))
    return text_int_sequences

# process_text转token序列
def text_to_int_sequence(process_text, word_index):
    int_sequence = []
    for c in process_text.split(" "):
        int_sequence.append(int(word_index[c]))
    return int_sequence

# 基于某种mode(en_word,en_char,cn等)来处理原始的文本语料
def get_process_text_list(text_list, mode):
    process_text_list = []
    for text in text_list:
        process_text_list.append(preprocess_sentence(text, mode))
    return process_text_list

# 初次训练时基于处理好的文本数据来获取文本数字list，并返回tokenizer对象以进行word_index和index_word的保存
def tokenize(texts):
    tokenizer = tf.keras.preprocessing.text.Tokenizer(filters='')  # 无过滤字符
    tokenizer.fit_on_texts(texts)
    text_int_sequences = tokenizer.texts_to_sequences(texts)  # 文本数字序列
    return text_int_sequences, tokenizer

# 读取文本文件，并基于某种row_style来处理原始语料
def get_text_list(text_path, row_style):
    text_list = []
    with open(text_path, "r") as f:
        sentence_list = f.readlines()
    for sentence in sentence_list:
        text_list.append(text_row_process(sentence, row_style))
    return text_list

# 基于原始text和其label_length的整形数字list来补齐label_tensor
def get_text_label(text_int_sequences, max_label_length):
    label_tensor_numpy = tf.keras.preprocessing.sequence.pad_sequences(
        text_int_sequences,
        maxlen=max_label_length,
        padding='post'
        )
    label_tensor = tf.convert_to_tensor(label_tensor_numpy)
    return label_tensor

# 获取最长的label_length
def get_max_label_length(text_int_sequences):
    max_label_length = 0
    for seq in text_int_sequences:
        max_label_length = max(max_label_length, len(seq))
    return max_label_length

# 对英文句子：小写化，切分句子，添加开始和结束标记，按单词切分
def preprocess_sentence_en_word(s):
    s = s.lower().strip()
    # 在单词与跟在其后的标点符号之间插入一个空格
    # 例如： "he is a boy." => "he is a boy ."
    # 参考：https://stackoverflow.com/questions/3645931/python-padding-punctuation-with-white-spaces-keeping-punctuation
    s = re.sub(r"([?.!,])", r" \1 ", s)  # 切分断句的标点符号
    s = re.sub(r'[" "]+', " ", s)  # 合并多个空格

    # 除了 (a-z, A-Z, ".", "?", "!", ",")，将所有字符替换为空格
    s = re.sub(r"[^a-zA-Z?.!,]+", " ", s)
    s = s.strip()
    """
    # 给句子加上开始和结束标记
    # 以便模型知道何时开始和结束预测
    s = '<start> ' + s + ' <end>'
    """
    return s

#对英文句子：小写化，切分句子，添加开始和结束标记，将空格转为<space>，按字符切分
def preprocess_sentence_en_char(s):
    s = s.lower().strip()

    result = ""
    for i in s:
        if i == " ":
            result += "<space> "
        else:
            result += i + " "
    """
    result = "<start> " + result.strip() + " <end>"
    """
    return result.strip()

# 对中文句子：按字切分句子，添加开始和结束标记
def preprocess_sentence_ch(s):
    s = s.lower().strip()

    s = [c for c in s]
    s = ' '.join(s)
    s = re.sub(r'[" "]+', " ", s)  # 合并多个空格

    s = s.strip()
    """
    # 给句子加上开始和结束标记
    # 以便模型知道何时开始和结束预测
    s = '<start> ' + s + ' <end>'
    """
    return s