from oracle.oracle_init import db_init
from file.file_util import create_file_auto, delete_dir


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
    create_file_auto(file_path, export_str)


# 导出sql文件 用于view视图, table架构
def export_sql(item_name, export_path='../export/oracle/plsql_script_export',
               project="HN", env="DEV", item_type="view"):
    export_str = export_plsql_item_str(item_name=item_name, item_type=item_type, project=project, env=env)

    file_path = f"{export_path}/{item_type}-{str.upper(item_name)}.sql"
    create_file_auto(file_path, export_str)


if __name__ == '__main__':
    delete_dir('../export/oracle/plsql_script_export/')
    for pck in ['archive_info_entrance_lv','con_file_archive_detail_lv','con_file_archive_detail_wfl_lv','con_file_archive_file_lv','file_archive_batch_manual_lv']:
        export_sql(item_name=pck, env="DEV", item_type="view")
