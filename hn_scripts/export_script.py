import glob
import json
import logging
import os
import sys

import chardet
import coloredlogs
from file.file_util import FileUtil
from oracle.oracle_init import db_init
import PySimpleGUI as sg

logger = logging.getLogger('file_module')
coloredlogs.install(level='DEBUG')
coloredlogs.DEFAULT_FIELD_STYLES = {'levelname': {'color': 'white', 'bold': True}}

str_sql = '''
declare
 v_line varchar2(32767) := '1';
 v_status number := 1;
 v_clob clob;
 v_error exception;
 v_null_count number := 0;
begin
  delete from hls_output_lines;

  dbms_output.enable(10000000);

  {script_function}


  while v_null_count <= 2 loop
    dbms_output.get_line(v_line, v_status);
    if v_line is null then
      v_null_count := v_null_count + 1;
    else
      v_null_count := 0;
    end if;
    if length(v_line) > 4000 then
      raise v_error;
    end if;
    v_clob := v_line;
    insert into hls_output_lines values(hls_output_lines_s.nextval, v_clob, v_line);
  end loop;

  commit;

  exception
    when v_error then
      dbms_output.put_line('有行超过4000个字符');
      insert into hls_output_lines values(hls_output_lines_s.nextval, v_clob, '有行超过4000个字符');

end;
'''


def export_script_main(sf, project, env, export_path):
    conn, cursor = db_init(project, env)
    for function in sf:
        if function != '':
            script_str = ""
            file_name = get_hn_script_file_name(function)
            sql_str = str_sql.format(script_function=function)
            cursor.execute(sql_str)

            cursor.execute("select line from hls_output_lines order by line_id")

            for line in cursor:
                if line[0] is not None:
                    script_str += str(line[0]) + '\r\n'

            file_path = export_path + '/' + file_name + '.sql'
            FileUtil(file_path, f'begin\n{script_str}\ncommit;\nend;').create_file_auto()
    cursor.close()
    conn.close()


# 批量获取脚本
def batch_export_script(project="HN", env="DEV", export_path="../export/hn/scripts"):
    FileUtil.delete_dir(export_path)
    with open("../hn_scripts/batch_export_scripts.txt", encoding='utf-8') as sf:
        export_script_main(sf, project, env, export_path)


# 获取处理后的文件名
def get_hn_script_file_name(function):
    file = open("../jsons/hn_script_detail.json", "rb")
    file_json = json.load(file)
    for rec in file_json:
        if rec["script"] in function:
            return rec["name"] + "-" + function.split("'")[1].replace('/', '.')


# 获取文件夹下的所有文件名
def get_dir_file_path(file_dir):
    file_list = []
    for root, dirs, files in os.walk(file_dir):
        # 当前目录路径
        # print(root)
        # 当前路径下所有子目录
        # print(dirs)
        # 当前路径下所有非目录子文件
        for file in files:
            file_list.append(file_dir + "\\" + file)

    return file_list


# 获取文件中的文本集 并加入commit 提交
def get_file_str(file_path, encoding='utf-8'):
    with open(file_path, encoding=encoding) as f:
        sql_str = ''
        for line in f:
            sql_str += line
        return sql_str


# 批量执行SQL文件
def batch_execute_sql(file_dir='', project="HN", env="DEV"):
    if file_dir == '':
        file_dir = "..\\export\\hn\\scripts"
    conn, cursor = db_init(project, env)
    file_counts = len(glob.glob(pathname=file_dir + "\\*.*"))
    for idx, file_path in enumerate(get_dir_file_path(file_dir)):
        standardized_file_encode(file_path)
        try:
            cursor.execute(get_file_str(file_path))
        except Exception as e:
            print("文件{path}报错了，错误信息为{error}".format(path=file_path, error=e))
            exit(0)
        print("执行了{path}文件 ({index}/{all})".format(path=file_path, index=idx + 1, all=file_counts))


# 文件类型转UTF-8
def standardized_file_encode(path):
    with open(path, "rb") as f:
        data = f.read()
    res = chardet.detect(data)
    # gb2312编码的，同一个用gbk编码解析
    if res["encoding"] == "GB2312":
        res["encoding"] = "GBK"
        with open(os.path.join(path), "w", encoding="utf-8") as file:
            line = str(data, encoding=res["encoding"])
            file.write(line)


def gui_export_scripts():
    sg.theme('BlueMono')  # 设置当前主题

    file = open("../jsons/hn_script_detail.json", "rb")
    file_json = json.load(file)

    model_name = [i['name'] for i in file_json]
    model = [i['model'] for i in file_json]

    # 界面布局，将会按照列表顺序从上往下依次排列，二级列表中，从左往右依此排列
    layout = [
        [sg.Text('选择导出环境:', font=("微软雅黑", 10)), sg.Combo(['DEV', 'UAT', 'PRE', 'PROD'],
                                                         default_value='DEV', key="export_env")],
        [sg.Frame(layout=[[sg.Text('生成类型:', font=("微软雅黑", 10)), sg.Combo(model_name, default_value='工作流类型',
                                                                         key="model_name", size=(20, 10))],
                          [sg.Text('物件名:', font=("微软雅黑", 10)), sg.InputText(key='item_name'),
                           sg.Button('生成', font=("微软雅黑", 10))]],
                  title='脚本代码生成器', title_color='black', relief=sg.RELIEF_SUNKEN, tooltip='target envs')],
        [sg.Text('批量导出代码:', font=("微软雅黑", 10))],
        [sg.Multiline(size=(90, 12), key="export_sql")],
        [sg.Button('导出', font=("微软雅黑", 12))],
        [sg.Text('选择执行环境:', font=("微软雅黑", 10)), sg.Combo(['DEV', 'UAT', 'PRE', 'PROD'],
                                                         default_value='UAT', key="exec_env")],
        [sg.FolderBrowse('选择执行文件夹(默认导出文件夹)', font=("微软雅黑", 10), key='folder', target='file_path')],
        [sg.Text('文件路径:', font=("微软雅黑", 10), key="file_path"), sg.Button('批量执行', font=("微软雅黑", 10))],
        [sg.Text('程序运行记录', justification='center', font=("微软雅黑", 10))],
        [sg.Output(size=(90, 8), font=("微软雅黑", 9), key="running_log")]
    ]

    window = sg.Window('脚本导出/执行 Author: Sora', layout)
    # 事件循环并获取输入值
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):  # 如果用户关闭窗口或点击`Cancel`
            break
        elif event == '生成':
            for model in file_json:
                if model['name'] == values['model_name']:
                    script_lines = model['model'].format(item_name=values['item_name']) + values['export_sql']
                    window['export_sql'].update(script_lines)
        elif event == '批量执行':
            try:
                batch_execute_sql(file_dir=values['folder'], project="HN", env=values["exec_env"])
            except Exception as e:
                print(e)
        elif event == '导出':
            try:
                export_script_main(values['export_sql'].split("\n"), project="HN",
                                   env=values["export_env"], export_path="../export/hn/scripts")
            except Exception as e:
                print(e)

    window.close()


def main():
    file = open("../jsons/hn_script_detail.json", "rb")
    file_json = json.load(file)



if __name__ == '__main__':
    edit_path = '''C:\\Users\\Master Yi\\Desktop\\档案归档发版\\sql\\视图'''

    exec_path = '..\\export\\oracle\\plsql_script_export\\'
    batch_export_script(project="HN", env="DEV")
    batch_execute_sql(project="HN", env="UAT")
    # gui_export_scripts()
    # input("press enter to continue")
