# Lib Detector

## Summary
Lib Detector extracts specified shared library files from multiple firmware binary files and compares them with pre-trained models of shared libraries using machine learning. It outputs the similarity scores as percentages.

With this approach, it becomes possible to detect the use of identical shared libraries—even if their filenames include different version numbers—after being extracted from firmware.

The comparison leverages model data generated through prior machine learning on known shared libraries. Firmware and extracted libraries are analyzed against these models to determine similarity.

Results are provided in the SPDX (Software Package Data Exchange) format as a Software Bill of Materials (SBOM), helping to visualize the software composition effectively.

## Getting Started
### Recommended environment
OS: "Ubuntu"

VERSION: "20.04.5 LTS (Focal Fossa)"

### Installation
1. Prerequisites
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

2. Clone the repo
   ```sh
   git clone https://github.com/nict-csl/libdetector.git
   ```

## Sample Data Usage
1. Preparation and execution
   ```sh
   cd libdetector/venv
   tar -xf venv_nict_sbom_tool.tar.xz
   source venv_nict_sbom_tool/bin/activate
   cd ../sbom_tool
   ./quick_run_all.sh
   ```
2. Check the results
   The analysis results are output to the ./output folder.

   | File  |  Contents   |
   | -------- | ----------  |
   | spdx.txt | SPDX-format list of shared libraries identified as similar, with scores. |
   | ROCCurve.png | ROC curve of similarity model.  |
   | ScoresResultTrue.png | Similarity scores for matching shared library file names.  |
   | ScoresResultFalse.png | Similarity scores for non-matching shared library file names. |


## Custom Data Usage
Example: Creating a data folder under the libdetector directory
   
1. Prepare firmware and shared library files for creating machine learning models
   ```sh
   cd libdetector
   mkdir -p data/model   #Create a folder named ‘model’ with a fixed name.
   cd data/model
   mkdir fw_1            #Folder names are created with the fixed prefix ‘fw_’.
   cp [Compressed firmware binary file (extension changed to .zipfw) or unzipped firmware binary folder or .so file]　. 
   mkdir fw_2
   cp [Compressed firmware binary file (extension changed to .zipfw) or unzipped firmware binary folder or .so file]　. 
   ・
   ・
   ```

2. Create a list to search for shared library files that create machine learning models.
   ```sh
   Edit libdetector/sbom_tool/script_parse/model_s.list
   
   #Example description (describe the search pattern)　　
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

3. Prepare the firmware and shared library files to be verified
   ```sh
   cd libdetector
   mkdir -p data/test    #Create a folder named ‘test’ with a fixed name.
   cd data/test
   mkdir fw_1            #Folder names are created with the fixed prefix ‘fw_’.
   cp [Compressed firmware binary file (extension changed to .zipfw) or unzipped firmware binary folder or .so file]　. 
   mkdir fw_2
   cp [Compressed firmware binary file (extension changed to .zipfw) or unzipped firmware binary folder or .so file]　. 
   ・
   ・
   ```

4. Create a list to search for shared library files to verify
   ```sh
   Edit libdetector/sbom_tool/script_parse/test_s.list
   
   #Example description (describe the search pattern)　　
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

5. Extract rodata section data from shared library files and save it to a file in order to create a machine learning model
   ```sh
   cd libdetector/sbom_tool/script_parse
   python3 parse_main.py model ../../data/model ./model_s.list #The second argument is the folder created in step 1.

   # The libdetector/work/model folder is created and files are saved.
   ```

6. In order to compare the shared library files to be verified with the machine learning model, extract the rodata section data from the shared library files and save it to a file
   ```sh
   cd libdetector/sbom_tool/script_parse
   python3 parse_main.py test ../../data/test ./test_s.list　 #The second argument is the folder created in step 3.

   # The libdetector/work/model folder is created and files are saved.
   ```

7. Machine learning model data creation
   ```sh
   cd libdetector/sbom_tool/script_analysis
   dir_path="../../work/model"      #Folder names are fixed 
   
   #The minimum word data size can be changed to between 2 and 5 bytes for learning.
   for min_word_len in 2 3 4 5; do
     python3 doc2vec_lerning_dmpv.py "$min_word_len" "$dir_path"
   done
   ```

8. Enter verification data and compare it with machine learning model data
   ```sh
   cd libdetector/sbom_tool/script_analysis
   select_tag=1                     #Type of model data tags: currently fixed at 1
   dir_path="../../work/test"       #Folder names are fixed 

   #The minimum word data size can be changed to between 2 and 5 bytes for learning.
   for min_word_len in 2 3 4 5; do
     python3 doc2vec_lerning_dmpv.py "$min_word_len" "$select_tag" "$dir_path" 
   done
   ```

9. Output of analysis results
   ```sh
   cd libdetector/sbom_tool/script_analysis
   python3 make_result.py ../output #Analysis result file creation
   python3 make_spdx.py ../output   #Creating SPDX files

   #The output folder for files is libdetector/sbom_tool/output.
   ```
## License
Distributed under the MIT License. See `LICENSE.txt` for more information.




