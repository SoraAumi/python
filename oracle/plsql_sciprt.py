import logging

from oracle.oracle_init import db_init, get_db_info, execute_self_sql, seq_generator_sql
from file.file_util import FileUtil


def capital_to_lower(dict_info):
    new_dict = {}
    for i, j in dict_info.items():
        new_dict[i.lower()] = j
    return new_dict


def list_to_lower(target_list):
    for item in target_list:
        target_list[target_list.index(item)] = capital_to_lower(item)
    return target_list


def column_property_str(type, length):
    if type == 'DATE':
        context = "DATE"
    else:
        context = f"{type}({length})"
    return context


# 导出plsql内容 type可为package body, package, view
def export_plsql_item_str(item_name, item_type, project, env):
    conn, cursor = db_init(project=project, env=env)

    '''  user_source 方法(只能支持 package, function, procedure等) '''
    # cursor.execute("select text from user_source "
    #                "where type = '{type}' and name = '{name}'".format(type=str.upper(item_type),
    #                                                                   name=str.upper(item_name)))

    ''' dbms_metadata 方法(可以支持 的 自己去看 https://blog.csdn.net/Loiterer_Y/article/details/84984416) '''
    sql_str = "SELECT DBMS_METADATA.GET_DDL(upper('{item_type}'),upper('{item_name}')) FROM DUAL" \
        .format(item_name=item_name, item_type=item_type)

    cursor.execute(sql_str)
    return cursor.fetchall()[0][0].read()


# 导出pck文件 用于包
def export_pck(item_name, export_path='../export/oracle/plsql_script_export', project="HN", env="DEV"):
    export_str = export_plsql_item_str(item_name=item_name, item_type="package",
                                       project=project, env=env) + '\r\n'

    file_path = f"{export_path}/package-{str.upper(item_name)}.pck"
    FileUtil(file_path, export_str).create_file_auto()


# 导出sql文件 用于view视图, table架构
def export_sql(item_name, export_path='../export/oracle/plsql_script_export',
               project="HN", env="DEV", item_type="view"):
    user, pwd, link = get_db_info(project, env)
    export_str = export_plsql_item_str(item_name=item_name, item_type=item_type, project=project, env=env) \
        .replace(f'"{user}".', '')

    file_path = f"{export_path}/{item_type}-{str.upper(item_name)}.sql"
    FileUtil(file_path, export_str).create_file_auto()
    logging.info(f"已导出{file_path}")


def sync_exec_sql(project, sync_envs, item_type, original_env):
    user, pwd, link = get_db_info(project, original_env)
    for env in sync_envs:
        logging.info(f"开始同步环境{env}")
        conn, cursor = db_init(project, env)
        for item in FileUtil('sync_items.txt').read_file(return_type="list"):
            sql = export_plsql_item_str(item, item_type, project, original_env).replace(f'"{user}".', '')
            if item_type == 'package':
                cursor.execute(sql[:sql.index("CREATE OR REPLACE PACKAGE BODY")])
                cursor.execute(sql[sql.index("CREATE OR REPLACE PACKAGE BODY"):])
            else:
                cursor.execute(sql)
            logging.info(f"已同步{env}.{item}")
    logging.info("同步完成 感谢您的使用 ^_^")


def sync_table(table_name, project, origin_env, sync_envs):
    logging.info(f"开始同步表 {table_name}")

    table_name = str.upper(table_name)
    user = get_db_info(project, origin_env)[0]
    conn, cursor = db_init(project, origin_env)
    e_sql = "select c.column_name, c.comments, p.DATA_TYPE, p.DATA_LENGTH \
             from user_col_comments c, user_tab_columns p where c.column_name = p.COLUMN_NAME\
            and c.table_name = p.TABLE_NAME and c.table_name = '{table_name}'"
    data = list_to_lower(execute_self_sql(cursor=cursor, paras=[table_name], para_desc=["table_name"], sql=e_sql))
    exe_sql_context = ""
    if len(data) == 0:
        logging.error("原表不存在")
    else:
        for env in sync_envs:
            sync_conn, sync_cursor = db_init(project, env)
            sync_user = get_db_info(project, env)[0]
            sync_data = list_to_lower(execute_self_sql(cursor=sync_cursor, paras=[table_name],
                                                       para_desc=["table_name"],
                                                       sql="select c.column_name, c.comments, p.DATA_TYPE, "
                                                           "p.DATA_LENGTH "
                                                           "from user_col_comments c, user_tab_columns p where c.column_name = p.COLUMN_NAME\
                                                        and c.table_name = p.TABLE_NAME and c.table_name = '{table_name}'"))
            sync_column_names = [i['column_name'] for i in sync_data]
            if len(sync_data) == 0:
                sync_cursor.execute(export_plsql_item_str(table_name, "table", project, origin_env)
                                    .replace(user, sync_user))
                sync_cursor.execute(seq_generator_sql(table_name))
                for column in data:
                    sync_cursor.execute(f"comment on column {table_name}.{column['column_name']} "
                                        f"is '{column['comments'] if column['comments'] is not None else ''}'")
                logging.info(f"{table_name} 表在{env}下不存在，已在{env}环境建立")
            else:
                for column in data:
                    comment = column['comments'] if column['comments'] is not None else ''
                    column_property = column_property_str(column['data_type'], column['data_length'])
                    if column not in sync_data:
                        if column["column_name"] not in sync_column_names:
                            exe_sql_context += f"alter table {table_name} add {column['column_name']} " \
                                               f"{column_property};\n"
                            exe_sql_context += f"comment on column {table_name}.{column['column_name']} is " \
                                               f"'{comment}';\n"
                        else:
                            exe_sql_context += f"alter table {table_name} modify {column['column_name']} " \
                                               f"{column_property};\n"
                            exe_sql_context += f"comment on column {table_name}.{column['column_name']} is " \
                                               f"'{comment}';\n"

                if exe_sql_context != '':
                    logging.info(f"存在{env}原表没有 {origin_env}现表有的列 需要修改 执行SQL如上 请自行执行")
                    print(exe_sql_context)
                else:
                    logging.info(f"{origin_env}表存在的列 {env}现表目前都有啦 (๑•̀ㅂ•́)و✧")


if __name__ == '__main__':
    # 同步视图 包
    # sync_exec_sql("HN", ['UAT'], item_type="view", original_env="DEV")

    # 生成视图 包的同步文件
    # FileUtil.delete_dir('../export/oracle/plsql_script_export/')
    # for pck in ['sdic_content_bookmark_pkg']:
    #     export_sql(item_name=pck, env="DEV", item_type="package")

    # 同步表
    sync_table("prj_project", "HN", "DEV", ["UAT"])
