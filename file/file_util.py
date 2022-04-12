import logging
import coloredlogs
import os
import shutil

logger = logging.getLogger('file_module')
coloredlogs.install(level='DEBUG')


# 创建文件写文件(自动覆盖)
def create_file(file_path, file_content):
    (fp, temp_filename) = os.path.split(file_path)

    if os.path.exists(file_path):
        logger.warning(f"   🌸 文件{temp_filename}已经存在 将会被覆盖啦")

    f = open(file_path, 'w+', encoding='utf-8')
    f.write(file_content)
    f.close()

    logger.info(f"   🍀 文件 {temp_filename} 已经生成 路径为 {fp}")


# 创建文件(没有路径自动生成)
def create_file_auto(file_path, file_content):
    (fp, temp_filename) = os.path.split(file_path)
    check_path_exist(fp)
    create_file(file_path, file_content)


# 检验路径是否存在 不存在自动生成
def check_path_exist(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        logger.warning(f"🏵️ 路径不存在，已经自动创建路径{file_path}啦")


# 清空文件夹
def delete_dir(path='../sql/auto_script_generator/scripts/'):
    if not os.path.exists(path):
        logger.warning(f"💮  哎呀 删除的文件夹不存在呢")
    else:
        shutil.rmtree(path)
        os.mkdir(path)
    logger.info(f"   🌼 {path} 文件夹的文件已经被清空啦")


# 读文件
def read_file(file_path, encoding='utf-8', return_type='str'):
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


# 获取文件夹下的所有文件名
def get_dir_file_path(file_dir):
    file_list = []
    for root, dirs, files in os.walk(file_dir):
        # 当前目录路径
        # print(root)
        # 当前路径下所有子目录
        # print(dirs)
        # 当前路径下所有非目录子文件
        for file in files:
            file_list.append(file_dir + "\\" + file)

    return file_list


# 清空文件夹 以及子目录
def clean_file_dir(path):
    static_files = ['FilePaths.txt', 'FileUpdate.py', 'FileUpdate.exe']
    for file in os.listdir(path):
        if file not in static_files:
            shutil.rmtree("./" + file)
