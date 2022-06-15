from file.file_util import FileUtil
from oracle.oracle_init import db_init, execute_self_sql, execute_sql_envs


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


def synchronize_function_code(function_code, project, env):
    return None


if __name__ == '__main__':
    synchronize_func_code_by_service("hn/atm/lose/synchronousByDate", "HN", "DEV")
