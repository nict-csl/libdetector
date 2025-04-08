import re
import os
from gensim.utils import simple_preprocess

#------------------------------------------
#テキストクリーニング
def clean_text(text):
    # 不要な文字や記号を削除
    result_text = text
    result_text = re.sub("\r?\n", ' ', result_text)
    result_text = re.sub("\t", '', result_text)
    result_text = re.sub('\s+', ' ', result_text)	#複数のスペースを一つに変換
    ##result_text = re.sub(r'[^\w\s]', '', result_text)
    return result_text

#------------------------------------------
def tokenize(data, min_word_len):
     # テキストを分かち書きして単語リストにします
    tokenized_text = simple_preprocess(data, min_len=int(min_word_len))  # 必要に応じてトークン化の条件を変更できます
    return tokenized_text

#------------------------------------------
def check_file_size(file_path):
    file_size = os.path.getsize(file_path)
    if file_size < 128:
        return False
    else:
        return True
      
