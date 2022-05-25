import sys
import os

from file.file_util import FileUtil
from oracle.oracle_db_export import OracleDBExport
from oracle.oracle_init import db_init

sys.path.append(os.getcwd() + 'oracle/oracle_init')


def layout_ds_table_export(project, env, layout_code, tab_code):
    dbe = OracleDBExport(project=project, env=env)
    insert_data_sql = dbe.export_db_data(sql=f'''select * from HLS_DOC_LAYOUT_CONFIG where tab_code = '{tab_code}' 
                            and layout_code = '{layout_code}' and enabled_flag = 'Y' ''',
                                         table_name='HLS_DOC_LAYOUT_CONFIG')

    return f''' begin delete from HLS_DOC_LAYOUT_CONFIG where tab_code = '{tab_code}' 
                            and layout_code = '{layout_code}' and enabled_flag = 'Y';\n{insert_data_sql}\n 
                            commit;\n end; '''


# 批量导出动态页面
def batch_layout_tab_export(project, env, export_list='./batch_export_layout_tab.txt',
                            reg='-', export_file_path='../export/hn/scripts/'):
    ft = FileUtil(export_list)
    layout_list = ft.read_file(return_type='list')
    FileUtil.delete_dir(export_file_path)
    for layout in layout_list:
        [layout_code, tab_code] = layout.split(reg)
        FileUtil(f"{export_file_path}页面布局-{layout_code}-{tab_code}.sql",
                 layout_ds_table_export(project, env, layout_code, tab_code)).create_file_auto()


if __name__ == '__main__':
    batch_layout_tab_export(project="HN", env='DEV')
