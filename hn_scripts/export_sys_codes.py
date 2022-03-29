# 导出系统编码
from file.file_util import create_file, delete_dir, read_file, create_file_auto
from oracle.oracle_init import db_init

code_sql_str = '''
                sys_code_pkg.insert_sys_code('{code}','{code_name}','{code_name}','{code_name}','ZHS','');
                sys_code_pkg.update_sys_code('{code}','{code}','{code}','{code}','US','');
            '''

code_value_sql = '''
                    sys_code_pkg.insert_sys_code_value('{code}','{code_value}','{code_value_name}','ZHS','');
                    sys_code_pkg.update_sys_code_value('{code}','{code_value}','{code_value}','US','');
                '''


# 获取系统代码脚本
def get_sys_codes_script(in_code):
    sql_str = '''begin'''

    code_value_sql_str = ''''''

    conn, cursor = db_init("HN", "DEV")
    cursor.execute("select s.code, (select description_text from fnd_descriptions where description_id = " +
                   "s.code_name_id and language = 'ZHS') code_name from sys_codes s where code = '{code}'".format(
                       code=in_code))
    code, code_name = cursor.fetchone()

    cursor.execute(f'''select v.code_value,
                   (select description_text from fnd_descriptions where description_id = 
                   code_value_name_id and language = 'ZHS') code_value_name
                   from sys_codes s, sys_code_values v 
                   where s.code_id = v.code_id
                   and s.code = '{in_code}'
                   and v.enabled_flag = 'Y' ''')
    for rec in cursor:
        code_value, code_value_name = rec
        code_value_sql_str += code_value_sql.format(code=code, code_value=code_value, code_value_name=code_value_name) \
                              + '\r\n'

    sql_str += code_sql_str.format(code=code, code_name=code_name) + code_value_sql_str + "commit;\r\nexception when " \
                                                                                          "others then null; end; "
    return sql_str


def export_sys_codes(codes):
    delete_dir("..\\export\\hn\\scripts\\")
    for code in codes:
        sql_str = get_sys_codes_script(code)
        create_file_auto('..\\export\\hn\\scripts\\' + "系统代码" + code + '.sql', sql_str)


def batch_export_sys_codes(path):
    codes = read_file(file_path=path, return_type='list')
    export_sys_codes(codes)


if __name__ == '__main__':
    batch_export_sys_codes("./batch_sys_codes_export.txt")
