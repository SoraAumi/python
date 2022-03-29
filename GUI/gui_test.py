import easygui as e
import sys

from file.file_script import refresh_project_file


def gui_init():
    return_type = e.buttonbox(msg='发版神器GUI V0.1', title='发版神器GUI V0.1', choices=['系统代码导出', '其他脚本导出', '工程文件导出'])
    export_type = ''
    export_info = {}
    if return_type in ['系统代码导出', '其他脚本导出']:
        export_type = '脚本导出'
    elif return_type == '工程文件导出':
        export_info = e.multenterbox(msg='导出目录不填会自动创建', title='发版神器GUI V0.1', fields=['工程目录', '导出目录'])
        export_type = return_type
    return export_type, export_info


if __name__ == '__main__':
    ep_type, ep_info = gui_init()
    if ep_type == '工程文件导出':
        refresh_project_file(ep_info[0], ep_info[1])
        e.msgbox("导出成功")
