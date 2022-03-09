import os
import shutil


# 创建文件写文件
def creat_file(file_path, file_content):
    f = open(file_path, 'w+', encoding='utf-8')
    f.write(file_content)
    f.close()


# 清空文件夹
def delete_dir(path='../sql/auto_script_generator/scripts/'):
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        shutil.rmtree(path)
        os.mkdir(path)


# 读文件
def read_file_str(file_path, encoding='utf-8', return_type='str'):
    with open(file_path, encoding=encoding) as f:
        file_str = ''
        file_list = []
        for line in f:
            file_str += line.strip()
            file_list.append(line.strip())
        if return_type == 'str':
            f.close()
            return file_str
        elif return_type == 'list':
            f.close()
            return file_list


# 清空文件夹 以及子目录
def clean_file_dir(path):
    static_files = ['FilePaths.txt', 'FileUpdate.py', 'FileUpdate.exe']
    for file in os.listdir(path):
        if file not in static_files:
            shutil.rmtree("./" + file)
