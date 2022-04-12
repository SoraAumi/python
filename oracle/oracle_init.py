import json
import datetime
import logging

import xlrd, xlwt
from faker import Faker

import cx_Oracle
import tkinter.messagebox


def get_table_column(cursor, table_name):
    sql = "SELECT a.column_name, a.data_type FROM user_tab_columns a WHERE a.TABLE_NAME = '{}' order by COLUMN_ID" \
        .format(str.upper(table_name))
    cursor.execute(sql)
    return get_sql_result(cursor, 0)


def export_data_to_excel(cursor, file_path='../hn_scripts/excels'):
    data = cursor.fetchall()
    title = [i[0] for i in cursor.description]
    faker = Faker(locale='zh_CN')
    xls_path = file_path + faker.file_path(depth=0, extension='xlsx')
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sql_query_sheet')
    for idx, column in enumerate(title):
        worksheet.write(0, idx, column)
    for row, record in enumerate(data):
        for line, column_data in enumerate(list(record)):
            worksheet.write(row + 1, line, column_data)
    workbook.save(xls_path)


def get_sql_result(cursor, row_number=-1):
    results = []
    while 1:
        row = cursor.fetchone()
        if row is None:
            break
        row_list = []
        for data in row:
            if type(data) is datetime.datetime:
                row_list.append(data.strftime('%Y-%b-%d'))
            else:
                row_list.append(data)
        results.append(row_list)
    return results


def trans_json(result, columns):
    data_list = []
    if len(result[0]) != len(columns):
        print("列数不匹配")
    else:
        for record in result:
            data_record = {}
            for i in range(len(record)):
                data_record[str(columns[i][0])] = record[i]
            data_list.append(data_record)
    return data_list


def get_text_sql():
    with open("../sql/oracle_sql.txt", encoding='utf-8') as f:
        sql_str = ''
        for line in f:
            sql_str += line.strip() + '\r\n'
        return sql_str


def get_db_info(project, env):
    file = open("../jsons/db_setting.json", "rb")
    file_json = json.load(file)
    for project_list in file_json:
        if project == project_list["project"]:
            for env_info in project_list["env_info"]:
                if env == env_info["env"]:
                    return env_info["db_username"], env_info["db_password"], env_info["db_url"]


def db_init(project, env):
    if env in ["DEV", "UAT", "PROD"]:
        user, password, link = get_db_info(project, env)
        conn = cx_Oracle.connect(user, password, link)
        cursor = conn.cursor()
        return conn, cursor
    else:
        logging.error("环境变量配置错误")
        exit(0)


def main():
    u, p, l = get_db_info("HN", "DEV")
    conn = cx_Oracle.connect(u, p, l)
    cursor = conn.cursor()
    cursor.execute("select * from prj_project where project_id = 12159")
    data = cursor.fetchall()
    title = [i[0] for i in cursor.description]

    print(title)
    print(data)
    cursor.close()
    conn.close()


if __name__ == '__main__':
    fake = Faker(locale='zh_CN')
    print(fake.file_path(depth=0, extension='xls'))
    # try:
    #     main()
    #     tkinter.messagebox.showinfo('提示', '执行成功')
    # except Exception as e:
    #     print(e)
    #     tkinter.messagebox.showerror('提示', e)
