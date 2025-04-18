# Lib Detector

## 概要
本ツールは、複数のファームウェアバイナリファイルから、予め指定した共有ライブラリファイルを抽出し、抽出した共有ライブラリファイルと機械学習済の共有ライブラリファイルを照合して、ファイルの類似度をパーセンテージで出力します。

これにより、ファームウェアバイナリから展開された状態の共有ライブラリファイル名に付加されているバージョン番号に関わらず、同一の共有ライブラリが使用されているかを検出することが可能です。

比較に使用する基準データは、共有ライブラリからあらかじめ機械学習により生成されたモデルデータを使用します。解析対象のファームウェアや共有ライブラリはこのモデルと照合され、分析が行われます。

検出結果は、SPDX形式のSBOM（Software Bill of Materials）として出力され、ソフトウェア構成の可視化に活用できます。

## 事前準備
### 推奨環境
OS: "Ubuntu"

VERSION: "20.04.5 LTS (Focal Fossa)"

### インストール
1. 前提条件
   ```sh
   sudo apt install binwalk
   ```

   ```sh
   pip install \
   cycler==0.12.1 \
   fonttools==4.47.2 \
   gensim==4.3.2 \
   importlib-resources==6.1.1 \
   joblib==1.3.2 \
   kiwisolver==1.4.5 \
   matplotlib==3.7.4 \
   numpy==1.24.4 \
   packaging==23.2 \
   pandas==2.0.3 \
   pillow==10.2.0 \
   pyparsing==3.1.1 \
   python-dateutil==2.8.2 \
   pytz==2023.3.post1 \
   scikit-learn==1.3.2 \
   scipy==1.10.1 \
   six==1.16.0 \
   smart-open==6.4.0 \
   threadpoolctl==3.2.0 \
   tzdata==2023.4 \
   zipp==3.17.0
   ```

2. リポジトリクローン
   ```sh
   git clone https://github.com/nict-csl/libdetector.git
   ```

## サンプルデータを用いて実行する手順
1. 準備と実行
   ```sh
   cd libdetector/venv
   tar -xf venv_nict_sbom_tool.tar.xz
   source venv_nict_sbom_tool/bin/activate
   cd ../sbom_tool
   ./quick_run_all.sh
   ```
2. 実行結果確認
   ./outputフォルダに分析結果が出力される

   | File  |  Contents   |
   | -------- | ----------  |
   | spdx.txt | 入力した共有ライブラリと、機械学習済みの共有ライブラリのモデルと比較した結果、類似していると判定した共有ライブラリ名と類似度をSPDX形式で出力 |
   | ROCCurve.png | ROC Curveのグラフ |
   | ScoresResultTrue.png | 入力した共有ライブラリと、共有ライブラリを機械学習済みのモデルと比較した結果、共有ライブラリファイル名が一致した結果だけを集計した、入力ファイル毎の類似度グラフ |
   | ScoresResultFalse.png | 入力した共有ライブラリと、共有ライブラリを機械学習済みのモデルと比較した結果、共有ライブラリファイル名が不一致の結果だけを集計した、入力ファイル毎の類似度グラフ |


## カスタムデータを用いて実行する手順
ex. libdetectorフォルダ直下にdataフォルダを作成する場合
   
1. 機械学習のモデルを作成するファームウェア及び共有ライブラリファイルを準備
   ```sh
   cd libdetector
   mkdir -p data/model   #フォルダ名modelは固定の名前で作成
   cd data/model
   mkdir fw_1            #フォルダ名fw_*は固定のプリフィックス名で作成
   cp [圧縮された状態のファームウェアバイナリファイル(拡張子は.zipfwに変更する) or 解凍済みのファームウェアバイナリのフォルダ or .soファイル]　.  #ファイルまたはフォルダをコピー
   mkdir fw_2
   cp [圧縮された状態のファームウェアバイナリファイル(拡張子は.zipfwに変更する) or 解凍済みのファームウェアバイナリのフォルダ or .soファイル]　.  #ファイルまたはフォルダをコピー
   ・
   ・
   ```

2. 機械学習のモデルを作成する共有ライブラリファイルを検索するためのリストを作成
   ```sh
   libdetector/sbom_tool/script_parse/model_s.list を編集する
   
   #記述例　（検索パターンを記述する）　
   libpthread.so*    
   libpthread-*.so*  
   libgcc.so.*       
   libgcc*.so        
   ld-uClibc.so*     
   ld-uClibc-*.so*   
   libc.so*          
   libc-*.so*        
   libz.so*          
   libz-*.so* 
   ```

3. 検証するファームウェア及び共有ライブラリファイルを準備
   ```sh
   cd libdetector
   mkdir -p data/test    #フォルダ名testは固定の名前で作成
   cd data/test
   mkdir fw_1            #フォルダ名fw_*は固定のプリフィックス名で作成
   cp [圧縮された状態のファームウェアバイナリファイル(拡張子は.zipfwに変更する) or 解凍済みのファームウェアバイナリのフォルダ or .soファイル]　.  #ファイルまたはフォルダをコピー
   mkdir fw_2
   cp [圧縮された状態のファームウェアバイナリファイル(拡張子は.zipfwに変更する) or 解凍済みのファームウェアバイナリのフォルダ or .soファイル]　.  #ファイルまたはフォルダをコピー
   ・
   ・
   ```

4. 検証する共有ライブラリファイルを検索するためのリストを作成
   ```sh
   libdetector/sbom_tool/script_parse/test_s.list を編集する
   
   #記述例　（検索パターンを記述する）　
   libpthread.so*    
   libpthread-*.so*  
   libgcc.so.*       
   libgcc*.so        
   ld-uClibc.so*     
   ld-uClibc-*.so*   
   libc.so*          
   libc-*.so*        
   libz.so*          
   libz-*.so* 
   ```

5. 機械学習のモデルを作成するため、共有ライブラリファイルからrodataセクションデータを抽出してファイルへ保存
   ```sh
   cd libdetector/sbom_tool/script_parse
   python3 parse_main.py model ../../data/model ./model_s.list #第2引数はフォルダは手順1で作成したフォルダ

   # libdetector/work/model フォルダが作成されてファイルが保存される
   ```

6. 検証する共有ライブラリファイルを機械学習のモデルと照合するため、共有ライブラリファイルからrodataセクションデータを抽出してファイルへ保存
   ```sh
   cd libdetector/sbom_tool/script_parse
   python3 parse_main.py test ../../data/test ./test_s.list　 #第2引数はフォルダは手順3で作成したフォルダ

   # libdetector/work/test フォルダが作成されてファイルが保存される
   ```

7. 機械学習モデルデータ作成
   ```sh
   cd libdetector/sbom_tool/script_analysis
   dir_path="../../work/model"      #フォルダ名は固定 

   #最小単語データサイズは2から5バイトの範囲で変更して学習
   for min_word_len in 2 3 4 5; do
     python3 doc2vec_lerning_dmpv.py "$min_word_len" "$dir_path"
   done
   ```

8. 検証データを入力して機械学習モデルデータと照合
   ```sh
   cd libdetector/sbom_tool/script_analysis
   select_tag=1                     #モデルデータのタグの種類、現在は1固定 
   dir_path="../../work/test"       #フォルダ名は固定 

   #最小単語データサイズはモデルデータ作成時と同様に、2から5バイトの範囲で変更して照合
   for min_word_len in 2 3 4 5; do
     python3 doc2vec_lerning_dmpv.py "$min_word_len" "$select_tag" "$dir_path" 
   done
   ```

9. 分析結果出力と実行結果確認
   ```sh
   cd libdetector/sbom_tool/script_analysis
   python3 make_result.py ../output #分析結果ファイル作成
   python3 make_spdx.py ../output   #SPDXファイル作成

   #ファイル出力先のフォルダは libdetector/sbom_tool/output
   ```

## ライセンス
MIT Licenseに基づいて配布されます。詳細については、`LICENSE.txt`を参照してください。





