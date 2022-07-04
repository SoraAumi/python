import PySimpleGUI as sg

from hn_scripts.export_script import gui_export_scripts
from oracle.plsql_sciprt import plsql_gui

sg.theme('BlueMono')  # 设置当前主题
# 界面布局，将会按照列表顺序从上往下依次排列，二级列表中，从左往右依此排列
layout = [
    [sg.Button('脚本导入导出工具', size=(8, 3), font=('微软雅黑', 12)),
     sg.Button('数据库同步工具Beta', size=(8, 3), font=('微软雅黑', 12)),
     sg.Button('常用查询', size=(8, 3), font=('微软雅黑', 12))],
    [sg.Frame(layout=[[sg.Text("作者: Sora")], [sg.Text("带有Beta的功能用的时候需要格外注意")],
                      [sg.Text("操作方法详情请见readme.md文档, 本项目已开源\n"
                               "Github仓库地址: https://github.com/jjyilinfeng/python-scripts")]],
              title='注意啦注意啦', title_color='black', relief=sg.RELIEF_SUNKEN, tooltip='target envs')]
]

# 创造窗口
window = sg.Window('华能业务系统发版工具包 V0.1', layout)
# 事件循环并获取输入值
while True:
    event, values = window.read()
    if event in (None, 'Cancel'):  # 如果用户关闭窗口或点击`Cancel`
        break
    elif event == '脚本导入导出工具':
        gui_export_scripts()
    elif event == '数据库同步工具Beta':
        plsql_gui()

window.close()
