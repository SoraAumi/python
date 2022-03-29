from file.file_util import create_file_auto, read_file, clean_file_dir, delete_dir
from oracle.oracle_init import db_init, get_table_column, get_sql_result

sql_str = '''
    begin
        {del_code}
        {insert_sql}
        commit;
    end;
'''


def layout_ds_table_export(project, env, layout_code, tab_code):
    conn, cursor = db_init(project, env)
    del_code = f''' delete from HLS_DOC_LAYOUT_CONFIG where tab_code = '{tab_code}' and layout_code = '{layout_code}'
                          and enabled_flag = 'Y'; '''
    cursor.execute(
        f'''select * from HLS_DOC_LAYOUT_CONFIG where tab_code = '{tab_code}' and layout_code = '{layout_code}'
                          and enabled_flag = 'Y' ''')
    layout_data = get_sql_result(cursor)
    # 查出来的第一个是列名 第二个是列类型
    layout_column = get_table_column(cursor, 'HLS_DOC_LAYOUT_CONFIG')

    insert_code = ''
    for idx, rec in enumerate(layout_data):
        insert_data = ""
        insert_clob = ""
        insert_declare = ""

        for index, data in enumerate(rec):
            if index == 0:
                insert_data += "hls_doc_layout_config_s.nextval,"
                continue

            if data is None:
                insert_data += 'null,'
            elif layout_column[index][1] == 'VARCHAR' or layout_column[index][1] == 'VARCHAR2':
                insert_data += f"'{data}',"
            elif layout_column[index][1] == 'CLOB':
                insert_declare += f"v_{layout_column[index][0]} clob;\r\n"
                insert_clob += f"      v_{layout_column[index][0]} := q'/{data.read()}/';\r\n"
                insert_data += f"v_{layout_column[index][0]},"
            elif layout_column[index][1] == 'DATE':
                insert_data += 'sysdate,'
            else:
                insert_data += f"{data},"
        insert_data = insert_data[:-1]
        insert_sql = f"insert into HLS_DOC_LAYOUT_CONFIG values({insert_data});\r\n"
        insert_model = \
            f'''
            declare
                {insert_declare}
            begin
                {insert_clob}
                {insert_sql}
            end;
            '''
        insert_code += insert_model

    create_file_auto(f"../export/hn/scripts/页面布局-{layout_code}-{tab_code}.sql",
                     sql_str.format(insert_sql=insert_code, del_code=del_code))


# 批量导出动态页面
def batch_layout_tab_export(project, env, export_list='./batch_export_layout_tab.txt', reg='-'):
    layout_list = read_file(file_path=export_list, return_type='list')
    delete_dir('../export/hn/scripts')
    for layout in layout_list:
        layout_ds_table_export(project, env, layout.split(reg)[0], layout.split(reg)[1])


if __name__ == '__main__':
    batch_layout_tab_export(project="HN", env='DEV')
