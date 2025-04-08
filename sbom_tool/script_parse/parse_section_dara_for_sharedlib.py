import subprocess
import sys

def run_strings_command(bin_file, text_file):
    command = f"strings {bin_file} > {text_file}"
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return output
    except subprocess.CalledProcessError as e:
        print(f"Error running readelf command: {e}")
        return None

def run_readelf_command(library_file, section_name):
    command = f"readelf -x {section_name} {library_file}"
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return output
    except subprocess.CalledProcessError as e:
        print(f"Error running readelf command: {e}")
        return None


def is_valid_hex(input_string):
    try:
        int(input_string, 16)
        return True
    except ValueError:
        return False

def extract_section_data(library_file, section_name):
    output = run_readelf_command(library_file, section_name)

####--------------------------------------
##    file_path = "../99.test/readdata.txt"  # 読み込むファイルのパスを指定
##
##    try:
##        with open(file_path, "r") as file:
##            output = file.read()
##            # ファイルの内容を使った処理
##    except FileNotFoundError:
##        print(f"ファイルが見つかりません: {file_path}")
##    except IOError as e:
##        print(f"ファイルを読み込めませんでした: {e}")
####--------------------------------------

    if output is None:
        return None
    
    hex_data = ""

    # 出力から16進数データの部分だけを取得してバイト列に変換する
    for line in output.splitlines():
        if 'Hex dump of section' in line:
            continue

        tmp = line.strip().split()[1:5]

        for i in range(len(tmp)):
            if False == is_valid_hex(tmp[i]):
                tmp[i] = ''

        hex_data += ' '.join(tmp)
 
    hex_data = hex_data.replace(' ', '')
    byte_data = bytes.fromhex(hex_data)
    
    return byte_data

def create_binary_file(library_file, section_name, output_file):
    data = extract_section_data(library_file, section_name)
    if data is not None:
        with open(output_file, "wb") as f:
            f.write(data)
        print(f"Data from section '{section_name}' extracted and saved to '{output_file}'")
    else:
        print(f"Failed to extract data from section '{section_name}'")

if __name__ == "__main__":
    library_file = "../01.data/libz/libz_0001.so"
    section_name = ".rodata"  # 抽出したいセクションの名前を指定してください
  
    tmplist = library_file.split("/")
    tmp_basename = tmplist[-1].split(".")
    output_file = "./"+tmp_basename[0] + "_output.bin"
 
    args = sys.argv
    if 3 <= len(args):
        library_file = args[1]
        section_name = args[2]
        tmplist = library_file.split("/")
        tmp_basename = tmplist[-1].split(".")
        tmplist[-1] = tmp_basename[0] + "_output.bin"
        output_file = ""
        for i in range(len(tmplist)-1):
            output_file = output_file + tmplist[i] + "/"
        output_file = output_file + section_name.replace('.', '') + "_" +tmplist[-1]

    print(library_file)
    print(section_name)

    create_binary_file(library_file, section_name, output_file)

    text_file = output_file.replace("output.bin", "output.txt")
    run_strings_command(output_file, text_file)
    