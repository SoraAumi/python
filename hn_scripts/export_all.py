import json
import logging

from hn_scripts.export_sys_codes import get_sys_codes_script
from hn_scripts.synchronize_sys_config import sync_func_code_sql
from oracle.oracle_init import db_init
from oracle.plsql_sciprt import export_plsql_item_str, sync_table

export_sql = '''
begin
    {ultra_sql}
commit;
end;
'''


def sql_main(json_path, project, env):
    with open(json_path) as f:
        export_json = json.load(f)

        sql = {}

        # 系统代码
        for code in export_json['sys_codes']:
            sql['sys_code_sql'][code] = get_sys_codes_script(code, project, env) + "\n"

        # 系统功能
        sql['function_code_sql'] = {}
        for function in export_json['function_codes']:
            sql['function_code_sql'][function] = sync_func_code_sql(function, project, env) + '\n'

        # 视图
        sql['view_sql'] = {}
        for view in export_json['views']:
            sql['view_sql'][view] = export_plsql_item_str(view, 'view', project, env)

        # 包
        sql['package'] = []
        sql['package_body'] = []
        for package in export_json['packages']:
            package_sql = export_plsql_item_str(package, 'package', project, env)
            sql['package'][package] = package_sql[:package_sql.index("CREATE OR REPLACE PACKAGE BODY")]
            sql['package_body'][package] = package_sql[package_sql.index("CREATE OR REPLACE PACKAGE BODY"):]

        return sql, export_json


def auto_main(json_file_path, project, ori_env, target_envs):
    sql_all, json_data = sql_main(json_file_path, project, ori_env)
    for env in target_envs:
        cursor = db_init(project, env)
        for ex_type in sql_all.keys():
            for item_name in sql_all[ex_type]:
                logging.info(f"开始在{env}环境下执行{ex_type}:{item_name}")
                cursor.execute(sql_all[ex_type][item_name])
                logging.info(f"{env}.{ex_type}.{item_name}执行完毕")

    for table in json_data['tables']:
        sync_table(table, project, ori_env, target_envs)

