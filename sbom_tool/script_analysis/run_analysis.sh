#!/bin/bash

rm -f RESULT.db

#-------------------------------------------------------------------------
run_no12_dmpv() {
  local min_word_len="$1"
  local model_input_data_folder="$2"
  local select_tag="$3"
  local test_input_data_folder="$4"

  # model data作成
	python3 doc2vec_lerning_dmpv.py "$min_word_len" "$model_input_data_folder"

  # testl dataを使用して類似度判定
	python3 doc2vec_run.py "$min_word_len" "$select_tag" "$test_input_data_folder"
}


#-------------------------------------------------------------------------
# 実行する関数
run_no12_dmpv 2 ../../work/model 1 ../../work/test
run_no12_dmpv 3 ../../work/model 1 ../../work/test
run_no12_dmpv 4 ../../work/model 1 ../../work/test
run_no12_dmpv 5 ../../work/model 1 ../../work/test

run_no12_dmpv 2 ../../work/model 2 ../../work/test
run_no12_dmpv 3 ../../work/model 2 ../../work/test
run_no12_dmpv 4 ../../work/model 2 ../../work/test
run_no12_dmpv 5 ../../work/model 2 ../../work/test

run_no12_dmpv 2 ../../work/model 3 ../../work/test
run_no12_dmpv 3 ../../work/model 3 ../../work/test
run_no12_dmpv 4 ../../work/model 3 ../../work/test
run_no12_dmpv 5 ../../work/model 3 ../../work/test

#-------------------------------------------------------------------------
# 結果作成
python3 make_result.py ../output

# SPDX作成
python3 make_spdx.py ../output

