# 导出系统编码
from file.file_util import FileUtil
from oracle.oracle_init import db_init

import PySimpleGUI as sg

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
def get_sys_codes_script(in_code, project="HN", env="DEV"):
    sql_str = '''begin'''

    code_value_sql_str = ''''''

    conn, cursor = db_init(project, env)
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


def sync_sys_codes(code, project, target_envs=None):
    if target_envs is None:
        target_envs = ["UAT", "PRE"]
    for env in target_envs:
        conn, cursor = db_init(project, env)
        cursor.execute(get_sys_codes_script(code))


def export_sys_codes(codes):
    FileUtil.delete_dir("..\\export\\hn\\scripts\\")
    for code in codes:
        sql_str = get_sys_codes_script(code)
        FileUtil('..\\export\\hn\\scripts\\' + "系统代码" + code + '.sql', sql_str).create_file_auto()


def gui_sys_codes():
    sg.theme('BlueMono')  # 设置当前主题
    # 界面布局，将会按照列表顺序从上往下依次排列，二级列表中，从左往右依此排列
    layout = [
        [sg.Frame(layout=[[sg.Text('选择导出环境:', font=("微软雅黑", 10)), sg.Combo(['DEV', 'UAT', 'PRE', 'PROD'],
                                                                           default_value='DEV', key="export_env")],
                          [sg.Text('系统代码:', font=("微软雅黑", 10)), sg.InputText(key='sys_code'), sg.Button("导出")]],
                  title='脚本代码生成器', title_color='black', relief=sg.RELIEF_SUNKEN, tooltip='target envs')],
        [sg.Text("导出系统代码 一行一个: ")],
        [sg.Multiline(size=(90, 16), key="export_sql")],
        [sg.Text('程序运行记录', justification='center', font=("微软雅黑", 10))],
        [sg.Output(size=(90, 8), font=("微软雅黑", 9), key="running_log")]
    ]

    # 创造窗口
    window = sg.Window('系统代码导出 Author: Sora', layout)
    # 事件循环并获取输入值
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):  # 如果用户关闭窗口或点击`Cancel`
            break
        elif event == '导出':
            try:
                window['export_sql'].update(get_sys_codes_script(values['sys_code'], project="HN",
                                                                 env=values["export_env"]))

                print(f"系统代码{values['sys_code']}已从{values['export_env']}环境导出！^_^")
            except Exception as e:
                print(e)


def batch_export_sys_codes(path):
    batch_file = FileUtil(path)
    codes = batch_file.read_file(return_type='list')
    export_sys_codes(codes)


if __name__ == '__main__':
    # batch_export_sys_codes("./batch_sys_codes_export.txt")

    gui_sys_codes()
