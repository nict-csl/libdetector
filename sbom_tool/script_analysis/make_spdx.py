import sys
import os
import platform
import uuid
from datetime import datetime, timedelta
import pytz
import pandas as pd
import hashlib
from datetime import datetime

# CSVファイルのパス
csv_file_path = 'final_result_TAG_1.csv'
## ------------------------------------------------------------------------------------
def get_random_sha1(input_string):
    # 今日の日付、現在の時間を取得
    today_date = datetime.today().strftime('%Y-%m-%d')
    current_time = datetime.today().strftime('%H:%M:%S')

    # 文字列、日付、時間を結合
    data_to_hash = f"{input_string}{today_date}{current_time}"

    # SHA-1ハッシュを計算
    sha1_hash = hashlib.sha1(data_to_hash.encode()).hexdigest()
    return sha1_hash

## ------------------------------------------------------------------------------------
def get_utc_jpn_cur_time():
    # UTC時間を取得
    utc_time = datetime.utcnow()

    # UTC時間から日本時間に変換
    jst = pytz.timezone('Asia/Tokyo')
    japan_time = utc_time.replace(tzinfo=pytz.utc).astimezone(jst)

    japan_time_str = japan_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    return japan_time_str

## ------------------------------------------------------------------------------------
def get_utc_cur_time():
    current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return current_time

## ------------------------------------------------------------------------------------
def get_uuid():
    return uuid.uuid4()

## ------------------------------------------------------------------------------------
def file_write(f, str):
    f.write(str + '\n')

## ------------------------------------------------------------------------------------
def make_creation_info(f):
    DOCNAME = f'NICT_sbom_tool'
    
    file_write(f, f'## +++++++++++++++++++++++++')
    file_write(f, f'## Creation Information')
    file_write(f, f'## +++++++++++++++++++++++++')
 
    file_write(f, f'SPDXVersion: SPDX-2.3')
    file_write(f, f'DataLicense: CC0-1.0')
    file_write(f, f'SPDXID: SPDXRef-DOCUMENT')
    file_write(f, f'DocumentName:' + DOCNAME)
    file_write(f, f'DocumentNamespace: http://spdx.org/spdxdocs/' + DOCNAME + '-' + str(get_uuid()) )
    file_write(f, f'Creator: Organization: National Institute of Information and Communications Technology')
    file_write(f, f'Created: ' + str(get_utc_jpn_cur_time()))
    file_write(f, '')

## ------------------------------------------------------------------------------------
def make_file_info_hedder(f):
    file_write(f, f'## -------------------------')
    file_write(f, f'## File Information')
    file_write(f, f'## -------------------------')
 
## ------------------------------------------------------------------------------------
def make_file_info_body(f, currentTargetFWFolderName):
     # CSVファイルを読み込む
    df = pd.read_csv(csv_file_path)

    # 各セルの値を取得する
    for index, row in df.iterrows():
        TargetFWFolderName = row['TargetFWFolderName']
        if currentTargetFWFolderName != TargetFWFolderName:
            continue

        ID = row['ID']
        Target = row['Target']
        TargetFileName = row['TargetFileName']
        TargetFullPathName = row['TargetFullPathName']
        TargetSHA1 = row['TargetSHA1']
        Label = row['Label']
        SimilarityScore = row['Similarity Score']
        Answer = row['Answer']

        file_write(f, f'FileName: ' + TargetFullPathName)
        file_write(f, f'SPDXID: SPDXRef-file-' + TargetFileName.replace('.','-').replace('_','-') + '-' + TargetSHA1[:7])
        file_write(f, f'FileType: BINARY')
        file_write(f, f'FileChecksum: SHA1: ' + TargetSHA1)
        file_write(f, f'LicenseConcluded: NOASSERTION')
        file_write(f, f'LicenseInfoInFile: NOASSERTION')
        file_write(f, f'LicenseComments: <text></text>')
        file_write(f, f'FileCopyrightText: NOASSERTION')
        file_write(f, f'FileComment: <text></text>')

        file_write(f, f'FileNotice: <text>')
        percent_string = "{:.2%}".format(SimilarityScore)
        file_write(f, f'This file is similar to the following file.')
        file_write(f, f'    Similar model file: ' + Label)
        file_write(f, f'    Similarity score  : ' + percent_string)
        file_write(f, f'</text>')

        file_write(f, '')
        file_write(f, f'## -------------------------')
     

## ------------------------------------------------------------------------------------
def make_pkg_info_hedder(f):
    file_write(f, f'## =========================')
    file_write(f, f'## Package Information')
    file_write(f, f'## =========================')
 
## ------------------------------------------------------------------------------------
def make_pkg_info_body(f):
     # CSVファイルを読み込む
    df = pd.read_csv(csv_file_path)

    # 'TargetFWFolderName'列で昇順にソートする
    df.sort_values(by='TargetFWFolderName', inplace=True)

    prev_TargetFWFolderName = None
    
    # 各セルの値を取得する
    for index, row in df.iterrows():
        TargetFWFolderName = row['TargetFWFolderName']

        # 以降の処理をスキップする条件
        if TargetFWFolderName == prev_TargetFWFolderName:
            continue
   
        prev_TargetFWFolderName = TargetFWFolderName

        make_pkg_info_hedder(f)

        file_write(f, f'PackageName: ' + TargetFWFolderName)
        file_write(f, f'SPDXID: SPDXRef-Package-' + TargetFWFolderName.replace('.','-').replace('_','-') )
        file_write(f, f'PackageDownloadLocation: NOASSERTION')
        file_write(f, f'FilesAnalyzed: true')
        file_write(f, f'PackageVerificationCode: ' + str(get_random_sha1(TargetFWFolderName)))
        file_write(f, f'PackageLicenseConcluded: NOASSERTION')
        file_write(f, f'PackageLicenseInfoFromFiles: NOASSERTION')
        file_write(f, f'PackageLicenseDeclared: NOASSERTION')
        file_write(f, f'PackageCopyrightText: NOASSERTION')

        file_write(f, '')
   
        make_file_info_hedder(f)
        make_file_info_body(f, TargetFWFolderName)

## ------------------------------------------------------------------------------------
###########################
# MAIN
###########################
system_type = platform.system()

# コマンドライン引数を取得する
if len(sys.argv) > 1:
    output_directory_path = sys.argv[1]  # ARG1: output_directory_path
else:
    output_directory_path = input("Enter the 'RESULT OUTPUT' DIRECTORY PATH: ")

# フォルダの作成
os.makedirs(output_directory_path, exist_ok=True)

output_directory_path = output_directory_path + '/'

# ファイル名の作成
output_file = output_directory_path + 'spdx.txt'

f = open(output_file, 'w')

# SPDXデータの作成
make_creation_info(f)

make_pkg_info_body(f)

f.close()


