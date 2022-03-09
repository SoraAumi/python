import os
import shutil

# 工程文件复制
from file.file_util import clean_file_dir


def copy_project_file(project_path, copy_file_path):
    # 读取文件中的路径
    fo = open("./file_script_data/copy_project_file.txt", "r")

    for line in fo:
        line = line.strip()
        copy_path = copy_file_path + '/' + line[line.index('main'):]
        if not os.path.exists(copy_path):
            (filepath, temp_filename) = os.path.split(copy_path)
            if not os.path.exists(filepath):
                os.makedirs(filepath)

            open('./' + copy_path, 'w')

        shutil.copyfile(project_path + line, './' + copy_path)
    fo.close()


if __name__ == '__main__':
    # clean_file_dir("file_script_data/copy_project_file/")
    copy_project_file("D:/WorkSpace/Project/leaf-hntc/",
                      'file_script_data/copy_project_file')
