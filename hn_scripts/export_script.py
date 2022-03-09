import glob
import json
import logging
import os
import chardet
import coloredlogs
from file.file_util import delete_dir, create_file_auto
from oracle.oracle_init import db_init

logger = logging.getLogger('file_module')
coloredlogs.install(level='DEBUG')


# 批量获取脚本
def batch_export_script(export_path="../export/hn/scripts"):
    conn, cursor = db_init("HN", "DEV")
    delete_dir(export_path)
    with open("../batch_export_scripts.txt/script_functions.txt", encoding='utf-8') as sf:
        for function in sf:
            if function != '':
                script_str = ""
                file_name = get_hn_script_file_name(function)

                with open("../sql/auto_script_generator/export_script.sql", encoding='utf-8') as f:
                    sql_str = ''
                    for line in f:
                        sql_str += (line.strip() + '\r\n').format(script_function=function)
                cursor.execute(sql_str)
                f.close()

                cursor.execute("select line from hls_output_lines order by line_id")

                for line in cursor:
                    if line[0] is not None:
                        script_str += str(line[0])

                file_path = export_path + '/' + file_name + '.sql'
                create_file_auto(file_path, script_str)
    cursor.close()
    conn.close()


# 获取处理后的文件名
def get_hn_script_file_name(function):
    file = open("../jsons/hn_script_detail.json", "rb")
    file_json = json.load(file)
    for rec in file_json:
        if rec["script"] in function:
            return rec["name"] + "-" + function.split("'")[1].replace('/', '.')


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


# 获取文件中的文本集 并加入commit 提交
def get_file_str(file_path):
    with open(file_path, encoding='utf-8') as f:
        sql_str = ''
        for line in f:
            if "END" in str.upper(line):
                line = "commit;" + line
            sql_str += line.strip() + '\r\n'
        return sql_str


# 批量执行SQL文件
def batch_execute_sql(file_dir="..\\sql\\auto_script_generator\\scripts", project="HN", env="DEV"):
    conn, cursor = db_init(project, env)
    file_counts = len(glob.glob(pathname=file_dir + "\\*.*"))
    for idx, file_path in enumerate(get_dir_file_path(file_dir)):
        # standardized_file_encode(file_path)
        try:
            cursor.execute(get_file_str(file_path))
        except Exception as e:
            logger.error("文件{path}报错了，错误信息为{error}".format(path=file_path, error=e))
            exit(0)
        logger.info("执行了{path}文件 ({index}/{all})".format(path=file_path, index=idx + 1, all=file_counts))


# 文件类型转UTF-8
def standardized_file_encode(path):
    with open(path, "rb") as f:
        data = f.read()
    res = chardet.detect(data)
    # gb2312编码的，同一个用gbk编码解析
    if res["encoding"] == "GB2312":
        res["encoding"] = "GBK"
    with open(os.path.join(path), "w", encoding="utf-8") as file:
        line = str(data, encoding=res["encoding"])
        file.write(line)


if __name__ == '__main__':
    batch_export_script()
    # batch_execute_sql(project="HN", env="UAT")
