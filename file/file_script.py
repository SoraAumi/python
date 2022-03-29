import os
import shutil

from file.file_util import check_path_exist, clean_file_dir


# 工程文件复制(不刷新文件夹)
def copy_project_file(project_path, copy_file_path="../export/file/file_script"):
    # 读取文件中的路径
    fo = open("./file_script_data/copy_project_file.txt", "r")

    check_path_exist(copy_file_path)

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


# 工程文件复制(刷新文件夹)
def refresh_project_file(project_path, copy_file_path="../export/file/file_script"):
    # clean_file_dir(copy_file_path)
    copy_project_file(project_path=project_path, copy_file_path=copy_file_path)


if __name__ == '__main__':
    refresh_project_file(project_path="D:/WorkSpace/Project/leaf-hntc/",
                         copy_file_path='file_script_data/copy_project_file')
