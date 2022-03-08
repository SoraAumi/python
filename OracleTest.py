import json
import datetime
import logging

import cx_Oracle
import tkinter.messagebox

def get_table_column(cursor, table_name):
    sql = "SELECT a.column_name FROM user_tab_columns a WHERE a.TABLE_NAME = '{}'" \
        .format(str.upper(table_name))
    cursor.execute(sql)
    return get_sql_result(cursor, 0)


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
    with open("sql/oracle_sql.txt", encoding='utf-8') as f:
        sql_str = ''
        for line in f:
            sql_str += line.strip() + '\r\n'
        return sql_str


def get_db_info(project, env):
    file = open("sql/db_setting.json", "rb")
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
    u, p, l = get_db_info()
    conn = cx_Oracle.connect(u, p, l)
    cursor = conn.cursor()
    output = cursor.callproc('sys_load_hls_doc_layout_pkg.export_all', ['FILE_ARCHIVE', 'N', None, -1])
    print(output)

    cursor.close()
    conn.close()


if __name__ == '__main__':
    try:
        main()
        tkinter.messagebox.showinfo('提示', '执行成功')
    except Exception as e:
        print(e)
        tkinter.messagebox.showerror('提示', e)


