import logging

from file.file_util import FileUtil
from oracle.oracle_init import db_init, execute_self_sql, execute_sql_envs, exec_sql_ultra


def synchronize_func_code_by_service(service_name, project, env):
    conn, cursor = db_init(project, env)

    sql = "select f.function_code, s.TITLE from sys_function_service fs, sys_service s, sys_function f\
            where fs.service_id = s.service_id and s.service_name = '{service_name}'\
            and f.function_id = fs.function_id"
    function_codes = execute_self_sql(cursor=cursor, paras=[service_name], para_desc=["service_name"], sql=sql)
    for code in function_codes:
        exec_sql = f''' 
                   begin  
                        sys_function_assign_pkg.service_load('{service_name}','{code['TITLE']}');
                        sys_function_assign_pkg.func_service_load('{code['FUNCTION_CODE']}', 
                                                                   '{service_name}'); 
                   commit;
                   end;'''
        execute_sql_envs(exec_sql, project)



def synchronize_func_code_by_bm(bm_name, project, env):
    conn, cursor = db_init(project, env)
    sql = '''
        select * from sys_function_bm_access sb, sys_function f
            where sb.bm_name = '{bm_name} ' and f.function_id = sb.function_id'''
    function_codes = execute_self_sql(cursor=cursor, paras=[bm_name], para_desc=["bm_name"], sql=sql)
    for code in function_codes:
        exec_sql = f''' 
                   begin  
                        sys_function_assign_pkg.func_bm_load('{code['FUNCTION_CODE']}','{bm_name}');
                   commit;
                   end;'''
        execute_sql_envs(exec_sql, project)


def sync_func_code_sql(function_code, project, env):
    conn, cursor = db_init(project, env)

    sql = f"select s.SERVICE_NAME, s.TITLE from sys_function_service fs, sys_service s, sys_function f\
                where fs.service_id = s.service_id and f.function_code = '{function_code}'\
                and f.function_id = fs.function_id"

    bm_sql = f'''
            select sb.BM_NAME from sys_function_bm_access sb, sys_function f
            where f.function_code='{function_code}' and f.function_id = sb.function_id'''

    views = exec_sql_ultra(cursor, sql)[0]

    bms = exec_sql_ultra(cursor, bm_sql)[0]

    exec_sql = "begin {func_sql} end;"

    func_sql = ""

    for view in views:
        service_sql = "begin sys_function_assign_pkg.service_load('{service_name}','{title}');" \
                      "sys_function_assign_pkg.func_service_load('{function_code}','{service_name}');" \
                      " commit;end;"

        func_sql += service_sql.format(service_name=view['SERVICE_NAME'], title=view['TITLE'],
                                       function_code=function_code)

    for bm in bms:
        exe_bm_sql = "begin sys_function_assign_pkg.func_bm_load('{function_code}','{bm_name}');" \
                     "commit;end;"
        func_sql += exe_bm_sql.format(function_code=function_code, bm_name=bm['BM_NAME'])


    return exec_sql.format(func_sql=func_sql)


def synchronize_function_code(function_code, project, env, target_envs=None):
    if target_envs is None:
        target_envs = ['UAT', 'PRE']

    for t_env in target_envs:
        conn, cursor = db_init(project, t_env)
        cursor.execute(sync_func_code_sql(function_code, project, env))
        logging.info(f"{t_env}环境{function_code}功能已经同步完毕")


if __name__ == '__main__':
    # 同步服务
    # synchronize_func_code_by_service("hn/atm/lose/synchronousByDate", "HN", "DEV")

    # 同步功能
    synchronize_function_code("PRJ506", "HN", "DEV")
