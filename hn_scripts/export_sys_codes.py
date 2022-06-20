# 导出系统编码
from file.file_util import FileUtil
from oracle.oracle_init import db_init

code_sql_str = '''
                sys_code_pkg.delete_sys_code('{code}');
                sys_code_pkg.insert_sys_code('{code}','{code_name}','{code_name}','{code_name}','ZHS','', 'N');
                sys_code_pkg.update_sys_code('{code}','{code}','{code}','{code}','US','', 'N');
            '''

code_value_sql = '''
                    sys_code_pkg.insert_sys_code_value(p_code => '{code}', 
                                                       p_code_value => '{code_value}', 
                                                       p_code_value_name =>'{code_value_name}',
                                                       p_language_code => 'ZHS',
                                                       p_enabled_flag => '{enabled_flag}',
                                                       p_order_seq => {order_seq});
                    sys_code_pkg.update_sys_code_value(p_code => '{code}', 
                                                       p_code_value => '{code_value}', 
                                                       p_code_value_name =>'{code_value_name}',
                                                       p_language_code => 'ZHS',
                                                       p_enabled_flag => '{enabled_flag}',
                                                       p_order_seq => {order_seq});
                '''


# 获取系统代码脚本
def get_sys_codes_script(in_code):
    sql_str = '''begin'''

    code_value_sql_str = ''''''

    conn, cursor = db_init("HN", "DEV")
    cursor.execute("select s.code, (select description_text from fnd_descriptions where description_id = " +
                   "s.code_name_id and language = 'ZHS') code_name from sys_codes s where code = upper('{code}')".format(
                       code=in_code))
    code, code_name = cursor.fetchone()

    cursor.execute(f'''select v.code_value,
                   (select description_text from fnd_descriptions where description_id = 
                   code_value_name_id and language = 'ZHS') code_value_name,
                   v.ENABLED_FLAG,
                   v.ORDER_SEQ
                   from sys_codes s, sys_code_values v 
                   where s.code_id = v.code_id
                   and s.code = '{in_code}'
                  ''')
    for rec in cursor:
        code_value, code_value_name, enabled_flag, order_seq = rec
        code_value_sql_str += code_value_sql.format(code=code, code_value=code_value, code_value_name=code_value_name,
                                                    enabled_flag=enabled_flag, order_seq=order_seq) + '\r\n'

    sql_str += code_sql_str.format(code=code, code_name=code_name) + code_value_sql_str + "commit;\r\nexception when " \
                                                                                          "others then null; end; "
    return sql_str


def export_sys_codes(codes):
    FileUtil.delete_dir("..\\export\\hn\\scripts\\")
    for code in codes:
        sql_str = get_sys_codes_script(code)
        FileUtil('..\\export\\hn\\scripts\\' + "系统代码" + code + '.sql', sql_str).create_file_auto()


def batch_export_sys_codes(path):
    batch_file = FileUtil(path)
    codes = batch_file.read_file(return_type='list')
    export_sys_codes(codes)


if __name__ == '__main__':
    batch_export_sys_codes("./batch_sys_codes_export.txt")
