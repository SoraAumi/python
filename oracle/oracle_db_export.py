import cx_Oracle

from oracle_init import db_init, get_table_pk
from file.file_util import create_file_auto

insert_sql = '''
declare
{declare_sql}
begin
{insert_sql}
end;

'''


def data_map(data_type):
    map_str = ""
    if data_type == cx_Oracle.DB_TYPE_CLOB:
        map_str = "CLOB"
    elif data_type == cx_Oracle.DB_TYPE_VARCHAR:
        map_str = "VARCHAR"
    elif data_type == cx_Oracle.DB_TYPE_NUMBER:
        map_str = "NUMBER"
    elif data_type == cx_Oracle.DB_TYPE_DATE:
        map_str = 'DATE'
    return map_str


def insert_map(data_type, data, column_name, table_name, table_pk):
    map_str = ""
    if data_type == "CLOB":
        map_str = f"v_{column_name}"
    elif column_name == table_pk:
        map_str = f'{table_name}_s.nextval'
    elif data_type == "VARCHAR":
        map_str = f"'{data}'"
    elif data_type == "NUMBER":
        map_str = data
    elif data_type == 'DATE':
        map_str = f"to_date('{data}', 'yyyy-mm-dd HH24:mi:ss')"

    return map_str


def get_sql_data(sql, project, env):
    conn, cursor = db_init(project, env)
    cursor.execute(sql)
    result = cursor.fetchall()
    list_result = []
    column_property = []
    for i in result:
        list_list = list(i)
        des = cursor.description  # 获取表详情，字段名，长度，属性等

        t = ",".join([item[0] for item in des])

        table_head = t.split(',')  # # 查询表列名 用,分割

        dict_result = dict(zip(table_head, list_list))  # 打包为元组的列表 再转换为字典
        column_property = dict(zip(table_head, [data_map(item[1]) for item in des]))

        list_result.append(dict_result)  # 将字典添加到list_result中

    return list_result, column_property, cursor


def set_declare_str(column_property):
    declare_str = ""
    for column in column_property.keys():
        if column_property[column] == 'CLOB':
            declare_str += f"V_{column};\n"

    return declare_str


def set_insert_str(result_data, column_property, table_name, table_pk):
    insert_str_all = ""

    for data in result_data:
        insert_str = ""

        clob_set = "\n"
        for column in column_property.keys():
            if column_property[column] == 'CLOB':
                clob_set += f"\t\tV_{column} := {data[column]};\n"

        for column in data.keys():
            insert_str += f"{insert_map(column_property[column], data[column], column, table_name, table_pk)},"
        insert_str_all += f"\tbegin \n\t\t{clob_set} \t\tinsert into {table_name} values ({insert_str[:-1]});" \
                          f"\n    end;\n"
    return insert_str_all


def export_db_data(sql, table_name, project, env, file_path="../export/script/"):
    result, column, cursor = get_sql_data(sql, project, env)
    table_pk = get_table_pk(cursor, table_name)
    execute_sql = insert_sql.format(declare_sql=set_declare_str(column),
                                    insert_sql=set_insert_str(result, column, table_name, table_pk))
    create_file_auto(f"{file_path}表{table_name}数据插入.sql", execute_sql)


if __name__ == '__main__':
    export_db_data("select * from HN_PAYMENT_CONDITION_HISTORY where rownum < 100", 'HN_PAYMENT_CONDITION_HISTORY', 'HN',
                   'DEV')
