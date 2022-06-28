import logging
import coloredlogs
import os
import shutil

logger = logging.getLogger('file_module')
coloredlogs.install(level='DEBUG')


class FileUtil:
    def __init__(self, target_path='', target_content=''):
        self.target_path = target_path
        self.fp, self.file_name = os.path.split(target_path)
        self.target_content = target_content

    # 读文件
    def read_file(self, encoding='utf-8', return_type='str'):
        with open(self.target_path, encoding=encoding) as f:
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

    # 创建文件写文件(自动覆盖)
    def create_file(self):
        (fp, temp_filename) = os.path.split(self.target_path)

        if os.path.exists(self.target_path):
            print(f"文件-{temp_filename}已经存在 将会被覆盖啦")

        f = open(self.target_path, 'w+', encoding='utf-8')
        f.write(self.target_content)
        f.close()

        print(f"文件-{self.file_name} 已经生成 路径为 {self.fp}")

    # 检验路径是否存在 不存在自动生成
    def check_path_exist(self, dirs=None):
        dirs = self.fp if dirs is None else dirs
        if not os.path.exists(dirs):
            os.makedirs(dirs)
            print(f"路径不存在，已经自动创建路径{dirs}啦")

    # 清空文件夹
    @staticmethod
    def delete_dir(dirs):
        if not os.path.exists(dirs):
            logger.warning(f"哎呀 删除的文件夹不存在呢")
        else:
            shutil.rmtree(dirs)
            os.mkdir(dirs)
        print(f"{dirs}-文件夹的文件已经被清空啦")

    # 获取文件夹下的所有文件名
    @staticmethod
    def show_files(path, all_files):
        file_list = os.listdir(path)
        for file in file_list:
            cur_path = os.path.join(path, file)
            if os.path.isdir(cur_path):
                FileUtil.show_files(cur_path, all_files)
            else:
                all_files.append(file)
        return all_files

    # 创建文件(没有路径自动生成)
    def create_file_auto(self):
        self.check_path_exist()
        self.create_file()

    def set_file_property(self, path, content):
        self.target_path = path
        self.fp, self.file_name = os.path.split(path)
        self.target_content = content

    # 设置文件内容
    def set_content(self, content):
        self.target_content = content

    # 设置文件路径
    def set_path(self, path):
        self.target_path = path
        self.fp, self.file_name = os.path.split(path)
