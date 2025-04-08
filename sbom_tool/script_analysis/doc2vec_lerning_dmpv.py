from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import strip_tags, strip_numeric
import random
import re
import sys
import subprocess
import doc2vec_common
import platform
import os
import csv

MODEL_LIST_CSV = "../script_parse/file_info_model.csv"

tagged_data = []

# テキストファイルからデータを読み込む関数
def read_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.readlines()
    return data

def read_and_tokenize_data(file_path, label, label2, label3, min_word_len):
    with open(file_path, 'r', encoding='utf-8') as f:
        # ファイル全体を読み込む
        input_data = f.read()

        clean_data = doc2vec_common.clean_text(input_data)

        # テキストを分かち書きして単語リストにします
        tokenized_text = doc2vec_common.tokenize(clean_data, min_word_len)  # 必要に応じてトークン化の条件を変更できます
       
        ##print(tokenized_text)
        
        # TaggedDocumentオブジェクトを作成してリストに追加します
        tagged_data.append(TaggedDocument(words=tokenized_text, tags=[label, label2, label3]))
    
    return tagged_data

#--------------------------
# label作成
#--------------------------
def make_label(label_key):
    index_correction = 1
    label_1 = 0
    label_2 = 0
    label_3 = 0

    with open(MODEL_LIST_CSV, 'r') as file:
        csv_reader = csv.reader(file)
        
        # CSVファイルの各行を処理
        for row in csv_reader:
            # 行から4番目の要素（0から数えて3番目の要素）を取得
            key = row[4+index_correction]
            
            # 検索キーと一致するかチェック
            if key == label_key:
                # 一致した行を表示
                #print(row)
                label_1 = row[0+index_correction]                
                label_2 = row[0+index_correction] + " + " + row[1+index_correction]               
                label_3 = row[0+index_correction] + " + " + row[1+index_correction] + " + " + row[2+index_correction]               
                break

    return label_1, label_2, label_3

###########################
# MAIN
###########################
# システムの種類を取得
system_type = platform.system()

# コマンドライン引数を取得する
if len(sys.argv) > 1:
    min_word_len = int(sys.argv[1]) # ARG1: min_word_len
else:
    min_word_len = input("Enter the MINIMUM WORD LENGTH: ")

if len(sys.argv) > 2:
    directory_path = sys.argv[2]  # ARG2: directory_path
else:
    directory_path = input("Enter the INPUT 'MODEL DATA' DIRECTORY PATH: ")

# ディレクトリ内のファイル一覧を取得
file_list = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

model_file = "lib_12.model"
    
count = 0

# ファイルを開いて読み込みモードでオープンします
for  file in file_list:
    if system_type == "Windows":
        line = os.path.join(directory_path, file).replace("/", "\\") 
    elif system_type == "Linux":
        line = os.path.join(directory_path, file).replace("\\", "/")
    else:
        print("未知のオペレーティングシステム")
        exit

    if "rodata" not in file:
        continue

    if ".txt" not in file:
        continue

    tmp = file.replace("rodata_", "")
    tmp = tmp.replace("_output", "")
    tmp = tmp.replace(".txt", "")
    label = tmp.strip()
  
    print(line.strip())

    if False == doc2vec_common.check_file_size(line.strip()):
        continue

    result_label = make_label(label)
    label_1 = str(result_label[0])
    label_2 = str(result_label[1])
    label_3 = str(result_label[2])

    tagged_data = read_and_tokenize_data(line.strip(), "label1-" + str(count) + ":" + label_1, "label2-" + str(count) + ":" + label_2, "label3-" + str(count) + ":" + label_3, min_word_len)

    count = count + 1   
    if count > 1:
        count = count + 1   
        #break

# Doc2Vecモデルの学習
default_seed = 0
random.seed(default_seed) 
model = Doc2Vec(documents=tagged_data,
                seed=default_seed,
                workers=1,
                dm=1,               # dmpvで学習
                vector_size=500,    # ベクトルの次元数を指定
                window=15,          # コンテキストウィンドウのサイズ
                min_count=1,        # 出現回数がこの値以下の単語を無視
                epochs=1000)        # データセット内の文書を何回繰り返し処理するか

#model.build_vocab(tagged_data)
#model.train(tagged_data, total_examples=model.corpus_count, epochs=30)

# モデルの保存
model.save(model_file)

print('Vector count:', len(model.dv))
#print('Keys:', model.dv.index_to_key)
