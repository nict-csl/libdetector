from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import strip_tags, strip_numeric
import sys
import random
import os
import re
import doc2vec_common
import platform
import csv
import sqlite3
import pandas as pd

DBNAME = 'RESULT.db'
TABLE_DOC2VEC_RESULT = 'table_doc2vec_result'
conn = 0
cur = 0
TEST_FILE_INFO_CSV = "../script_parse/file_info_test.csv"

#------------------------------------
def close_db():
    global conn
    global cur
    cur.close()
    conn.close()

#------------------------------------
def insert_db(val_1, val_2, val_3, val_4, val_5, val_6, val_7):
    global conn
    global cur
    cur.execute(f'INSERT INTO {TABLE_DOC2VEC_RESULT} (target_lib_no, target_fw_folder_name, target_lib_name, target_lib_fullpath_name, target_sha1, label, similarity_ratio) \
                VALUES (?, ?, ?, ?, ?, ?, ?)', (val_1, val_2, val_3, val_4, val_5, val_6, val_7))
    conn.commit()
#------------------------------------
def open_db():
    global conn
    global cur
    # dbファイルを削除する
    ##if os.path.exists(DBNAME):  # ファイルが存在するか確認
    ##    os.remove(DBNAME)

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    # テーブルを作成
    # テーブル存在確認
    cur.execute(f'SELECT COUNT(*) FROM sqlite_master WHERE TYPE="table" AND NAME="{TABLE_DOC2VEC_RESULT}"')
    if cur.fetchone()[0] == 0:  # 存在しないとき
        cur.execute(f'CREATE TABLE {TABLE_DOC2VEC_RESULT}( \
                    id INTEGER PRIMARY KEY AUTOINCREMENT, \
                    target_lib_no STRING, \
                    target_fw_folder_name STRING, \
                    target_lib_name STRING, \
                    target_lib_fullpath_name STRING, \
                    target_sha1 STRING, \
                    label STRING, \
                    similarity_ratio REAL \
                    )')

#------------------------------------
# テキストファイルからデータを読み込む関数
def read_data(file_path, data_clean_flg):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()

    if data_clean_flg == "true":
        clean_data = doc2vec_common.clean_text(data)
        data_len = str(len(clean_data))
    else:
        clean_data = data
        data_len = str(len(clean_data))

    return clean_data

#------------------------------------
# file_info_test.csvからTARGETのファイル情報を取得
def get_target_lib_info(key):
    index_adjustment = 1

    # CSVファイルを読み込む
    df = pd.read_csv(TEST_FILE_INFO_CSV, header=None)
    
    # 抽象化したファイル名の列をキーとして検索し、ファイル名を取得
    file_name = df[df[2+index_adjustment] == key][3+index_adjustment].astype(str).values
    file_name = file_name.astype(str)

    # 抽象化したファイル名の列をキーとして検索し、FW FOLDER名を取得
    fw_folder_name = df[df[2+index_adjustment] == key][0+index_adjustment].astype(str).values
    fw_folder_name = fw_folder_name.astype(str)

    # 抽象化したファイル名の列をキーとして検索し、SHA1を取得
    sha1 = df[df[2+index_adjustment] == key][0].astype(str).values
    sha1 = sha1.astype(str)

    # 抽象化したファイル名の列をキーとして検索し、ファイルPATHを取得
    fullpath_name = df[df[2+index_adjustment] == key][4+index_adjustment].astype(str).values
    fullpath_name = fullpath_name.astype(str)

    return str(file_name[0]), str(fw_folder_name[0]), str(sha1[0]), str(fullpath_name[0])

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
    SELECT_TAG = int(sys.argv[2]) # ARG2: SELECT_TAG
else:
    SELECT_TAG = input("Enter the TAG NUMBER (1 - 3): ")
    
if len(sys.argv) > 3:
    directory_path = sys.argv[3]  # ARG3: directory_path
else:
    directory_path = input("Enter the INPUT 'WORK DATA' DIRECTORY PATH: ")

# ディレクトリ内のファイル一覧を取得
file_list = file_list = os.listdir(directory_path)

# ファイルを昇順に並べ替え
file_list.sort()

model_file = "lib_12.model"
data_clean_flg = "true"

# 学習済みモデルを読み込む
model = Doc2Vec.load(model_file)

open_db()

# 検証LOOP
for filename in file_list:
    if system_type == "Windows":
        filename = os.path.join(directory_path, filename).replace("/", "\\") 
    elif system_type == "Linux":
        filename = os.path.join(directory_path, filename).replace("\\", "/")
    else:
        print("非対応のオペレーティングシステム")
        close_db()
        exit()

    if "rodata" not in filename:
        continue

    if ".txt" not in filename:
        continue

    print("==================================")
    print(filename.strip())
    if False == doc2vec_common.check_file_size(filename.strip()):
        print("size err: "+ filename.strip())
        continue

    # 新しい文書に対するベクトル表現を取得
    new_text = read_data(filename.strip(), data_clean_flg)

    # 文字列を単語のリストに分割
    preprocessed_text = doc2vec_common.tokenize(new_text, min_word_len)

    default_seed = 0
    random.seed(default_seed) 
    os.environ["PYTHONHASHSEED"] = str(default_seed)
    model.random.seed(default_seed)
    inferred_vector = model.infer_vector(preprocessed_text)
    ##print(inferred_vector)

    ##result = model.dv.most_similar(inferred_vector)
    vector_count = len(model.dv)
    similar_documents = model.dv.most_similar(inferred_vector, topn=vector_count)

    tmp = filename.strip()
    if system_type == "Windows":
        tmp2 = tmp.split("\\")
    else:
        tmp2 = tmp.split("/")
    target_lib_no = tmp2[-1]
    target_lib_no = target_lib_no.replace("rodata_", "")
    target_lib_no = target_lib_no.replace("_output.txt", "")

    # 選択したTAG種別で類似な文書を１つ出力
    detect_flg = 0
    detect_result = "X"
    for tag, similarity in similar_documents:
        if SELECT_TAG == 1 and "label1-" in tag:
            detect_flg = 1
            #print(f"{modified_tag}, {similarity}")
            break

        if SELECT_TAG == 2 and "label2-" in tag:
            detect_flg = 1
            #print(f"{modified_tag}, {similarity}")
            break

        if SELECT_TAG == 3 and "label3-" in tag:
            detect_flg = 1
            #print(f"{modified_tag}, {similarity}")
            break

    if detect_flg == 0:
        tag = "TAG no match"
        similarity = 0.0
    
    target_lib_name, target_fw_folder_name, target_sha1, fullpath_name = get_target_lib_info(target_lib_no)

    insert_db(target_lib_no, target_fw_folder_name, target_lib_name, fullpath_name, target_sha1, tag, float(similarity))
    continue

close_db()
