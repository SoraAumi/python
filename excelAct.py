# coding=utf-8
import json
import logging
import os
import glob

import chardet as chardet
import xlrd
import shutil

from OracleTest import db_init


# 获取xls文档行列
def get_excel_row_col(path, sheet_name):
    read_book = xlrd.open_workbook(path)

    sheet = read_book.sheet_by_name(sheet_name)

    n_rows = sheet.nrows
    n_cols = sheet.ncols

    sheet_data = []

    for i in range(n_rows):
        xls_list = []
        for j in range(n_cols):
            xls_list.append(sheet.cell(i, j).value)
        sheet_data.append(xls_list)

    return sheet_data


# 获取sql查询数据
def get_query_data(sheet_data):
    data_column = []

    data_list = []

    for idx, row in enumerate(sheet_data):
        data_dict = {}
        if idx == 0:
            for col in row:
                data_column.append(str.lower(col))
        else:
            for index, col in enumerate(row):
                data_dict[data_column[index]] = col
            data_list.append(data_dict)

    return data_list, data_column


# 批量获取脚本
def auto_script_generator():
    conn, cursor = db_init("HN", "DEV")
    delete_file()
    with open("sql/auto_script_generator/script_functions.txt", encoding='utf-8') as sf:
        for function in sf:
            if function != '':
                script_str = ""

                file_name = get_hn_script_file_name(function)

                with open("sql/auto_script_generator/set_lines.sql", encoding='utf-8') as f:
                    sql_str = ''
                    for line in f:
                        sql_str += (line.strip() + '\r\n').format(script_function=function)
                cursor.execute(sql_str)
                f.close()

                cursor.execute("select line from hls_output_lines order by line_id")

                for line in cursor:
                    if line[0] is not None:
                        script_str += str(line[0]) + '\r\n'

                creat_file(file_name, script_str)
                logging.info(file_name + "已生成")
    cursor.close()
    conn.close()


# 获取处理后的文件名
def get_hn_script_file_name(function):
    file = open("jsons/hn_script_detail.json", "rb")
    file_json = json.load(file)
    for rec in file_json:
        if rec["script"] in function:
            return rec["name"] + "-" + function.split("'")[1].replace('/', '.')


# 创建文件写文件
def creat_file(file_name, file_content):
    file_path = 'sql/auto_script_generator/scripts/' + file_name + '.sql'
    f = open(file_path, 'w+', encoding='utf-8')
    f.write(file_content)


# 清空脚本文件夹
def delete_file():
    filepath = './sql/auto_script_generator/scripts/'
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    else:
        shutil.rmtree(filepath)
        os.mkdir(filepath)


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


# 获取文件中的文本集
def get_file_str(file_path):
    with open(file_path, encoding='utf-8') as f:
        sql_str = ''
        for line in f:
            if "END" in str.upper(line):
                line = "commit;" + line
            sql_str += line.strip() + '\r\n'
        return sql_str


# 批量执行SQL文件
def batch_execute_sql(file_dir="sql\\auto_script_generator\\scripts", project="HN", env="DEV"):
    conn, cursor = db_init(project, env)
    file_counts = len(glob.glob(pathname=file_dir + "\\*.*"))
    for idx, file_path in enumerate(get_dir_file_path(file_dir)):
        # standardized_file_encode(file_path)
        try:
            cursor.execute(get_file_str(file_path))
        except Exception as e:
            logging.error("文件{path}报错了，错误信息为{error}".format(path=file_path, error=e))
            exit(0)
        logging.info("执行了{path}文件 ({index}/{all})".format(path=file_path, index=idx + 1, all=file_counts))


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


# 导出系统编码
def export_sys_codes(in_code):
    conn, cursor = db_init("HN", "DEV")
    cursor.execute("select s.code, (select description_text from fnd_descriptions where description_id = s.code_name_id and language = 'ZHS') code_name from sys_codes s where code = {code}".format(code=in_code))
    return cursor.fetchone()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # auto_script_generator()
    # batch_execute_sql(project="HN", env="UAT")

    print(export_sys_codes("PRJ_PROJECT_TYPE"))
