import sqlite3
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import glob
import platform
import matplotlib
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

DBNAME = 'RESULT.db'
TABLE_DOC2VEC_RESULT = 'table_doc2vec_result'

###########################
# MAIN
###########################
system_type = platform.system()

# コマンドライン引数を取得する
if len(sys.argv) > 1:
    output_directory_path = sys.argv[1]  # ARG1: output_directory_path
else:
    output_directory_path = input("Enter the 'RESULT OUTPUT' DIRECTORY PATH: ")

# フォルダの再作成
os.makedirs(output_directory_path, exist_ok=True)

output_directory_path = output_directory_path + '/'


if system_type == "Linux":
    matplotlib.use('Agg')  # バックエンドを設定

## -------------------------------------------------------------------------------------------------------------
def process_target_lib_name(lib_names):
    processed_name = lib_names.split('.so')[0]
    return processed_name

## -------------------------------------------------------------------------------------------------------------
# dbを参照して類似度が大きい検証結果を選択してまとめる
list_labels = {1: [], 2: [], 3: []}  # 空リストを持つ辞書を作成

conn = sqlite3.connect(DBNAME)
cur = conn.cursor()

# DBからtarget_lib_noの値を取得する
cur.execute(f"SELECT DISTINCT target_lib_no FROM {TABLE_DOC2VEC_RESULT}")
target_lib_no_list= cur.fetchall()

for label_number in range(1, 4):  # 1から3までのループ
    for target_lib_no in target_lib_no_list:
        target_lib_no = target_lib_no[0]  # タプルから値を取得
        #print("処理対象の target_lib_no:", target_lib_no)

        label = f"label{label_number}%"

        # 同じ target_lib_no を持つ行を抽出するクエリ
        cur.execute(f"SELECT * FROM {TABLE_DOC2VEC_RESULT} WHERE target_lib_no = ? AND label LIKE ?", (target_lib_no, label))
        rows = cur.fetchall()

        TOP_target_lib_no = ""
        TOP_target_fw_folder_name = ""
        TOP_target_lib_name = ""
        TOP_target_fullpath_name = ""
        TOP_target_sha1 = ""
        TOP_label = ""
        TOP_similarity_ratio = 0.0
        Top_answer = ""
        if rows:
            for row in rows:
                row_dict = dict(zip([desc[0] for desc in cur.description], row))  # 行を辞書に変換
                similarity_ratio = row_dict['similarity_ratio']  # カラム名を使って値を取得
                #print(similarity_ratio)

                if float(TOP_similarity_ratio) < float(similarity_ratio):
                    TOP_target_lib_no = row_dict['target_lib_no']
                    TOP_target_fw_folder_name = row_dict['target_fw_folder_name']
                    TOP_target_lib_name = row_dict['target_lib_name']
                    TOP_target_fullpath_name = row_dict['target_lib_fullpath_name']
                    TOP_target_sha1 = row_dict['target_sha1']
                    TOP_label = row_dict['label']
                    TOP_similarity_ratio = similarity_ratio  # row_dictから取得する代わりに直接使用
                    tmp = process_target_lib_name(TOP_target_lib_name)
                    if tmp in TOP_label:
                        Top_answer = 1
                    else:
                        Top_answer = 0

            tmp_label = TOP_label.split(":")
            list_labels[label_number].append((TOP_target_lib_no, TOP_target_fw_folder_name, TOP_target_lib_name, TOP_target_fullpath_name, TOP_target_sha1, tmp_label[1], TOP_similarity_ratio, Top_answer)) 

print(list_labels)
##cur.execute(f'SELECT * FROM {TABLE_DOC2VEC_RESULT}')
##print(cur.fetchall())

cur.close()
conn.close()

## -------------------------------------------------------------------------------------------------------------
# list_labels を整形して出力

# データを整形して表形式にする
formatted_data = []
for key, value in list_labels.items():
    for item in value:
        row = [key] + list(item)
        formatted_data.append(row)

# pandasのDataFrameに変換
df = pd.DataFrame(formatted_data, columns=["ID", "Target", "TargetFWFolderName", "TargetFileName", "TargetFullPathName", "TargetSHA1", "Label", "Similarity Score", "Answer"])
# 表形式で出力
print(df)

## ------------------------------------------------------------------
grouped_dfs = {}
for key, group_data in df.groupby("ID"):
    grouped_dfs[key] = group_data

# 各キー毎にDataFrameを出力
for key, group_df in grouped_dfs.items():
    print("-----------------------------------")
    print(f"LABEL: {key}")
    print("-----------------------------------")
    print(group_df)
    print("\n")

## ------------------------------------------------------------------
# 各キー毎にDataFrameをCSVとして出力
for key, group_df in grouped_dfs.items():
    file_name = f"final_result_TAG_{key}.csv"
    group_df.to_csv(file_name, index=False)
    print(f"CSVファイル {file_name} に保存しました。")

## ------------------------------------------------------------------
# CSVファイルからデータを読み取り、グラフをプロットする関数
def plot_graph_from_df(df, result_target):
    system_type = platform.system()

    # グラフの描画
    plt.figure(figsize=(16, 9))

    # データのプロット
    for index, row in df.iterrows():
        if row['Answer'] == 0 and result_target == False:
            plt.scatter(row['Target'], row['Similarity Score'], color='red')  # AnswerがXの場合は赤でプロット

        if row['Answer'] == 1 and result_target == True:
            plt.scatter(row['Target'], row['Similarity Score'], color='blue')  # AnswerがXでない場合は青でプロット

    # グラフの装飾
    plt.xlabel('Target')
    plt.ylabel('Similarity Score')

    if result_target == True:
        plt.title('Top Similarity Scores by Target (result True)')
    else:
        plt.title('Top Similarity Scores by Target (result False)')


    plt.xticks(rotation=90, fontsize=6)  # X軸のラベルを度回転させる
    plt.grid(False)
    plt.tight_layout()
    ##plt.show()

    # グラフをファイルに保存
    if result_target == True:
        png_file = output_directory_path + "ScoresResultTrue.png"
    else:
        png_file = output_directory_path + "ScoresResultFalse.png"

    plt.savefig(png_file)  # ファイルに保存
    plt.close()  # グラフを表示せずに閉じる

## ------------------------------------------------------------------
# データ数カウント
def result_count(df):
    count_ture = 0
    count_false = 0

    # データのプロット
    for index, row in df.iterrows():
        if row['Answer'] == 0:
            count_false += 1
        if row['Answer'] == 1:
            count_ture += 1

    print(f"TOTAL: {count_ture + count_false}  true: {count_ture}  false: {count_false}")

##===========
# LABEL 1のCSVファイルのグラフをプロットする
file_paths = glob.glob('final_result_TAG_1.csv')  # CSVファイルのパスを取得

for file_path in file_paths:
    df = pd.read_csv(file_path)  # CSVファイルをDataFrameとして読み込む
    print(f"Creating graph for file: {file_path}")
    plot_graph_from_df(df, True)
    plot_graph_from_df(df, False)
    result_count(df)

## ------------------------------------------------------------------
# LABEL 1の ROC曲線

label_no = 1
group_df = grouped_dfs[label_no]
print(group_df)
X = group_df['Similarity Score']
y = group_df['Answer']

# ROC曲線を計算
fpr, tpr, thresholds = roc_curve(y, X)
roc_auc = auc(fpr, tpr)

# ROC曲線のプロット
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (AUC = %0.3f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc='lower right')

# グラフをファイルに保存
plt.tight_layout()
plt.savefig(output_directory_path + 'ROCCurve.png')  # ファイルに保存
plt.close()  # グラフを表示せずに閉じる
