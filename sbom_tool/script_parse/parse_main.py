import os
import sys
import glob
import shutil
import subprocess
import platform
import csv
import subprocess
import parse_section_dara_for_sharedlib
import hashlib

WORK_FOLDER = "../../work"

def run_firmware_parse(target_dir):
    # 対象ディレクトリ以下を再帰的に検索
    for root, dirs, files in os.walk(target_dir):
        for target_file in files:
            # *.zipfw ファイルを検索
            if target_file.endswith('.zipfw'):
                found_file_path = os.path.join(root, target_file)
                print(found_file_path)

                # target_fileのディレクトリに移動
                original_dir = os.getcwd()
                os.chdir(os.path.dirname(found_file_path))

                # extractedを含むフォルダを削除
                for item in os.listdir(os.getcwd()):
                    if os.path.isdir(item) and '.extracted' in item:
                        shutil.rmtree(item)

                # binwalkコマンドを実行
                subprocess.run(['binwalk', '-Mre', os.path.basename(found_file_path)])

                # 元のディレクトリに戻る
                os.chdir(original_dir)

def get_target_files(target_list_file):
    target_files = []

    # model_s.list ファイルからパターンを取得
    with open(target_list_file, "r") as list_file:
        lines = list_file.readlines()
        for line in lines:
            line = line.strip()  # 余分な空白文字を削除
            if line:  # 空行でない場合のみ追加
                target_files.append(line)

    return target_files

def find_files(target_dir, target_files):
    src_dir_base = os.getcwd()

    list_files = []

    dir_tmp = target_dir
    cur_dir = dir_tmp ##os.path.join(src_dir_base, dir_tmp)

    # 対象ディレクトリ以下を再帰的に検索
    for root, dirs, files in os.walk(cur_dir):
        for target_file in target_files:
            found_files = glob.glob(os.path.join(root, target_file))
            list_files.extend(found_files)
            # 重複を取り除いたリストを生成
            list_files = list(set(list_files))

    return list_files

def remove_symbolic_links(list_files):
    cleaned_list = []
    for file in list_files:
        if not os.path.islink(file):
            cleaned_list.append(file)

    return cleaned_list

def remove_readelf_error_files(list_files):
    cleaned_list = []
    for file in list_files:
        if platform.system() != 'Windows':
            readelf_output = subprocess.run(['readelf', '-h', file], capture_output=True, text=True)
            if "Error:" not in readelf_output.stderr:
                cleaned_list.append(file)
            else:
                os.remove(file)
        else:
            cleaned_list.append(file)  # Windowsであればエラーのチェックをせずに追加

    return cleaned_list

def get_file_cmd_info(cleaned_list, list_file):
    if os.path.exists(list_file):
        os.remove(list_file)

    count = 1;    
    for filename in cleaned_list:
         with open(list_file, "a") as output_file:
            filename = str(filename)
            filename = filename.strip()
            so_name = os.path.basename(filename)

            internal_file_id = str(target_base_folder_name) + "_" + str(count).zfill(4)
            if platform.system() != 'Windows':
                result = subprocess.run(['file', filename], capture_output=True, text=True)
                output_file.write(f"{internal_file_id},{so_name},{result.stdout.strip().replace(':', ',')}\n")
            else:
                # Windowsの場合は何らかの代替処理を実行する（今回は空の文字列を書き込む）
                output_file.write(f"{internal_file_id},{so_name},{filename},Windows does not support 'file' command\n")
            count += 1
    
def rename_file_copy(target_work_folder_name, list_file):
    with open(list_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # 3カラム目がファイルパスを表している
            src_file = str(row[2])
            dst_file = str(row[0]) + ".so"
 
            if platform.system() == 'Windows':
                src_file = src_file.replace("/", "\\")
            else:
                src_file = src_file.replace("\\", "/")

            # WORKフォルダへファイルをコピー
            if os.path.exists(src_file):  # ファイルが存在するか確認
                destination = os.path.join(target_work_folder_name, dst_file)  # WORKフォルダ内のパス
                shutil.copy(src_file, destination)  # ファイルをコピー

def get_rodata(target_work_folder_name, list_file):
    with open(list_file, 'r') as csv_file:
        lines = csv_file.readlines()
        for line in lines:
            line = line.strip()
            DST_FILE = line.split(',')[0] + ".so"
            subprocess.run(['python3', 'parse_section_dara_for_sharedlib.py', f'{target_work_folder_name}/{DST_FILE}', '.rodata'])
 
def get_rodata_size(target_work_folder_name, list_file):
    temp_file = f"{list_file}.temp"  # 一時ファイルを作成

    with open(list_file, 'r') as f, open(temp_file, 'w') as temp_f:
        for line in f.readlines():
            line = line.strip()
            SRC_FILE = f"rodata_{line.split(',')[0]}_output.txt"
            file_path = f"{target_work_folder_name}/{SRC_FILE}"

            if platform.system() == 'Windows':
                file_path = file_path.replace("/", "\\")
            else:
                file_path = file_path.replace("\\", "/")

            if os.path.exists(file_path):  # ファイルが存在するか確認
                DATA_SIZE = os.path.getsize(file_path)
                temp_f.write(f"{DATA_SIZE},{line}\n")
            else:
                temp_f.write(f"0,{line}\n")

    # 一時ファイルを元のファイルにコピー
    os.replace(temp_file, list_file)

def make_model_add_info(target_type, list_file):
    temp_file = f"{list_file}.temp"  # 一時ファイルを作成

    with open(list_file, 'r') as f, open(temp_file, 'w') as temp_f:
        for line in f.readlines():
            line = str(line.strip())

            # TAG作成
            DATA_LIB_NAME = line.split(',')[2].split('.')[0]
            DATA_LIB_VER = line.split(',')[2].split('.so')[1].lstrip('.')
            DATA_FW_NAME = line.split(',')[3].split(target_type)[1].split(os.path.sep)[1]

            # 書き込み
            temp_f.write(f"{DATA_LIB_NAME},{DATA_LIB_VER},{DATA_FW_NAME},{line}\n")

    # 一時ファイルを元のファイルにコピー
    os.replace(temp_file, list_file)

def make_test_add_info(target_type, list_file):
    temp_file = f"{list_file}.temp"  # 一時ファイルを作成

    with open(list_file, 'r') as f, open(temp_file, 'w') as temp_f:
        for line in f.readlines():
            line = str(line.strip())

            # FW FOLDER　NAME取得
            DATA_FW_NAME = line.split(',')[3].split(target_type)[1].split(os.path.sep)[1]

            # 書き込み
            temp_f.write(f"{DATA_FW_NAME},{line}\n")

    # 一時ファイルを元のファイルにコピー
    os.replace(temp_file, list_file)

def calculate_file_sha1(file_path):
    # ファイルをバイナリ読み込みモードで開く
    with open(file_path, 'rb') as file:
        # ファイルからデータを読み込み、SHA-1ハッシュを計算
        sha1 = hashlib.sha1()
        while True:
            data = file.read()  # ファイルを読み込むバイト数を指定（ここでは64KB）
            if not data:
                break
            sha1.update(data)

    # ハッシュ値を16進数文字列として取得
    return sha1.hexdigest()

def make_test_sha1(target_type, list_file):
    if target_type == "model":
        fileptah_idx = 6
    else:
        fileptah_idx = 4

    temp_file = f"{list_file}.temp"  # 一時ファイルを作成 

    with open(list_file, 'r') as f, open(temp_file, 'w') as temp_f:
        for line in f.readlines():
            line = str(line.strip())

            # SHA1取得
            file_path = line.split(',')[fileptah_idx]
            file_sha1 = calculate_file_sha1(file_path)

            # 書き込み
            temp_f.write(f"{file_sha1},{line}\n")

    # 一時ファイルを元のファイルにコピー
    os.replace(temp_file, list_file)

def align_columns_and_overwrite(file_path):
    # CSVファイルを読み込む
    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        data = list(reader)

    # 最大のカラム数を見つける
    max_columns = max(len(row) for row in data)

    # カラム数を空白で揃える
    for row in data:
        while len(row) < max_columns:
            row.append('')  # 空白を追加してカラム数を揃える

    # ファイルを上書きして書き込む
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

# ===============================================================
# MAIN Entry
# ===============================================================
# コマンドライン引数を取得する
if len(sys.argv) > 1:
    target_type = sys.argv[1]  # ARG1: target_type
else:
    target_type = input("Enter the TARGET TYPE (model or test): ")

# コマンドライン引数を取得する
if len(sys.argv) > 2:
    target_inuput_data_directory = sys.argv[2]  # ARG2: target_inuput_data_directory
else:
    target_inuput_data_directory = input("Enter the TARGET INPUT DATA DIRECTORY: ")  # ユーザーから入力データディレクトリ名を取得

# コマンドライン引数を取得する
if len(sys.argv) > 3:
    target_list_file = sys.argv[3]  # ARG3: target_list_file
else:
    target_list_file = input("Enter the TARGET LIST FILE (*.list): ")  # ユーザーからLISTファイル名を取得

"""
if target_type == "model":
    target_list_file = "model_s.list"
else:
    target_list_file = "test_s.list"
"""

target_files = get_target_files(target_list_file)
target_base_folder_name = os.path.basename(os.path.dirname(target_inuput_data_directory + "/"))
target_work_folder_name = f"{WORK_FOLDER}/{target_base_folder_name}"

target_csv_file = f"file_info_{target_type}.csv"

# FW解凍（拡張子zipfwのファイルをBINWALKの固定パラメータで解凍）
run_firmware_parse(target_inuput_data_directory)

# ファイルサーチ及びサーチファイルリスト生成
found_files = find_files(target_inuput_data_directory, target_files)

# シンボリックリンクを削除
cleaned_list_files = remove_symbolic_links(found_files)

# Windowsではreadelfチェックをスキップ
if platform.system() != 'Windows':
    cleaned_list_files = remove_readelf_error_files(cleaned_list_files)

# リストの出力
for file in cleaned_list_files:
    print(file)

# FILE CMDの情報を取得
get_file_cmd_info(cleaned_list_files, target_csv_file)    

# フォルダの削除
shutil.rmtree(target_work_folder_name, ignore_errors=True)

# フォルダの再作成
os.makedirs(target_work_folder_name, exist_ok=True)

# RENAMEしてコピー
rename_file_copy(target_work_folder_name, target_csv_file)

# rodata取得
get_rodata(target_work_folder_name, target_csv_file)

# rodataサイズ取得
get_rodata_size(target_work_folder_name, target_csv_file)

# modelデータのときTAGを作成
if target_type == "model":
    make_model_add_info(target_type, target_csv_file)

# testデータのときTAGを作成
if target_type == "test":
    make_test_add_info(target_type, target_csv_file)

# SHA1を取得
make_test_sha1(target_type, target_csv_file)

# カラムを揃える
align_columns_and_overwrite(target_csv_file)