import os
import shutil
import uuid

import requests

from file.file_util import FileUtil
from oracle.oracle_init import db_init, execute_self_sql, special_select_head
from oracle.oracle_db_export import OracleDBExport

exec_sql = '''
declare
v_attachment_id number;
v_attachment_multi_id number;
v_template_id number;
begin
  select fnd_atm_attachment_multi_s.nextval into v_attachment_multi_id from dual;
  
  select fnd_atm_attachment_s.nextval into v_attachment_id from dual;
  
  select hls_doc_file_templet_s.nextval into v_template_id from dual;
  
  insert into hls_doc_file_templet values(v_template_id, '{templet_code}', '{templet_name}', 'CONTRACT_FILE', null, null, null, 'Y', sysdate, 1, sysdate, 1, null, null);
  
  insert into fnd_atm_attachment values(v_attachment_id, 'fnd_atm_attachment_multi', v_attachment_multi_id, '', '{templet_end}', 
                                        'application/msword', '{templet_name}.{templet_end}', {file_size}, '{file_path}', sysdate, 1, sysdate , 1,  'N', 0);
  
  insert into fnd_atm_attachment_multi values (v_attachment_multi_id, 'HLS_DOC_FILE_TEMPLET', v_template_id, v_attachment_id,
                                        sysdate, 1, sysdate, 1, null, 1, -1, -1, -1, null, null, 0, null, null);
end;
'''


def all_files_path(root_dir):
    path_list = []
    for root, dirs, files in os.walk(root_dir):  # 分别代表根目录、文件夹、文件
        for file in files:  # 遍历文件
            file_path = os.path.join(root, file)  # 获取文件绝对路径
            path_list.append(file_path)

    return path_list


def get_template_name(dir_path):
    return FileUtil.show_files(dir_path, [])


def download_file(attachment_id, file_path):
    down_res = requests.get(url=f"http://10.213.234.43:9081/atm_download.lsc?attachment_id={attachment_id}")
    with open(file_path, "wb") as code:
        code.write(down_res.content)


# 模板下载
def contract_model_download(download_path, env):
    conn, cursor = db_init('HN', env)
    sql = "select f.attachment_id, t.templet_name, f.file_type_code, f.file_name from hls_doc_file_templet t, fnd_atm_attachment_multi fm, fnd_atm_attachment f\
                                where fm.attachment_id = f.attachment_id and \
                                fm.table_name = 'HLS_DOC_FILE_TEMPLET' and t.templet_id = fm.table_pk_value " \
          "and                  t.enabled_flag = 'Y' and f.del_flag = 0"
    template_data = \
        execute_self_sql(cursor=cursor, paras=[], para_desc=[],
                         sql=sql)
    for att in template_data:
        download_file(att['ATTACHMENT_ID'], download_path + att['TEMPLET_NAME'] + '.' + att['FILE_TYPE_CODE'])


def model_replace(model_path, replace_env):
    conn, cursor = db_init('HN', replace_env)
    sql = "select f.file_path, t.templet_name, f.attachment_id from hls_doc_file_templet t, fnd_atm_attachment_multi fm, fnd_atm_attachment f\
                where fm.attachment_id = f.attachment_id and \
                fm.table_name = 'HLS_DOC_FILE_TEMPLET' and t.templet_id = fm.table_pk_value and t.enabled_flag = 'Y'\
                and f.del_flag = 0"
    template_data = \
        execute_self_sql(cursor=cursor, paras=[], para_desc=[],
                         sql=sql)

    count = 0

    for file_path in all_files_path(model_path):
        if '~$' not in file_path:
            path, file_name = os.path.split(file_path)
            file_size = os.stat(file_path).st_size
            print(file_size)


# 模板上传
def contract_model(models_path):
    sql_context = "begin "
    FileUtil.delete_dir('./export_words')
    for file_path in all_files_path('.\\14.电站类融资租赁业务合同-清洁版'):
        if '~$' not in file_path:
            path, file_name = os.path.split(file_path)
            conn, cursor = db_init('HN', 'DEV')
            sql = "select * from hls_doc_file_templet where templet_id in \
                        (select distinct table_pk_value from fnd_atm_attachment_multi fm, fnd_atm_attachment f \
                            where fm.attachment_id = f.attachment_id and \
                            fm.table_name = 'HLS_DOC_FILE_TEMPLET' and f.file_name like '{templet_name}%') and ENABLED_FLAG = 'Y'"
            template_data = \
                execute_self_sql(cursor=cursor, paras=[os.path.splitext(file_name)[0]], para_desc=["templet_name"],
                                 sql=sql)[0]
            uuid_name = str.upper(str(uuid.uuid4()).replace('-', ''))
            model_file_path = '/u01/hls_attachment/2022/06/' + uuid_name
            model_file_size = os.path.getsize(file_path)
            sql_context += exec_sql.format(templet_code=template_data['TEMPLET_CODE'],
                                           templet_name=template_data['TEMPLET_NAME'],
                                           templet_end=os.path.splitext(file_name)[1],
                                           file_size=model_file_size, file_path=model_file_path)
            shutil.copyfile(file_path, f'./export_words/{uuid_name}')
    sql_context += 'end;'
    print(sql_context)
    return sql_context


# 参数集上传
def model_para_sync():
    fp = FileUtil('./temporary_text.txt')
    conn, cursor = db_init('HN', 'DEV')
    uat_con, uat_cur = db_init('HN', 'UAT')
    for code in fp.read_file(return_type='list'):
        sql = "\
            select ft.templet_code, fp.bookmark,  fl.* from hls_doc_file_tmp_para_link fl, \
                  hls_doc_file_templet ft,\
                  hls_doc_file_templet_para fp\
           where fl.templet_id = ft.templet_id and fp.ENABLED_FLAG = 'Y'\
                 and fp.templet_para_id = fl.templet_para_id and ft.TEMPLET_CODE = '{templet_code}'\
        "
        exe_data = execute_self_sql(cursor=cursor, paras=[code], para_desc=["templet_code"],
                                    sql=sql)

        if exe_data is not None:
            for link_data in exe_data:
                ret_sql = f'''insert into hls_doc_file_tmp_para_link values(hls_doc_file_tmp_para_link_s.nextval,
                                         (select TEMPLET_PARA_ID from hls_doc_file_templet_para where BOOKMARK='{link_data['BOOKMARK']}' and HLS_DOC_FILE_TEMPLET_PARA.ENABLED_FLAG = 'Y'), 
                                         (select templet_id from hls_doc_file_templet where TEMPLET_CODE = '{link_data['TEMPLET_CODE']}'),
                                         '{link_data['ENABLED_FLAG']}', sysdate, 1, sysdate, 1, '{link_data['FONT_FAMILY']}',
                                         '{link_data['FONT_SIZE']}','{link_data['UNDERLINE']}','{link_data['IND_WIDTH']}',
                                         '{link_data['BOLD']}'); \n'''
                e_sql = "begin " + ret_sql.replace('None', '') + "commit;end;"
                uat_cur.execute(e_sql)


# 参数上传
def contract_para_sync():
    exe_sql = "select * from hls_doc_file_templet_para where  ENABLED_FLAG = 'Y'"
    dbe = OracleDBExport('HN', 'DEV')
    return dbe.export_db_data(exe_sql, 'hls_doc_file_templet_para',
                              {'creation_date': 'sysdate', 'last_update_date': 'sysdate'})


# 模板模板定义
def model_condition_head():
    exe_sql = "select * from con_clause_templet where enabled_flag = 'Y'"
    dbe = OracleDBExport('HN', 'DEV')
    return dbe.export_db_data(exe_sql, 'con_clause_templet',
                              {'creation_date': 'sysdate', 'last_update_date': 'sysdate',
                               'templet_id': "con_clause_templet_s.nextval"})


# 模板条件定义
def model_condition_line():
    dbe = OracleDBExport('HN', 'DEV')
    sql_head = special_select_head(dbe.cursor, "con_contract_tmpt_clause",
                                   {"TMPT_ID": "('(select templet_id from con_clause_templet "
                                               "where templet_code='''||(select templet_code from con_clause_templet where TEMPLET_ID = tmpt_id)||''')') as TMPT_ID"})
    exe_sql = f"select {sql_head} from con_contract_tmpt_clause where TMPT_ID in " \
              f"(select templet_id from CON_CLAUSE_TEMPLET where ENABLED_FLAG = 'Y')"
    return dbe.export_db_data(exe_sql, 'con_contract_tmpt_clause',
                              special_data={'creation_date': 'sysdate', 'last_update_date': 'sysdate'},
                              special_code=["tmpt_id"])


if __name__ == '__main__':
    # Step 0 下载模板

    contract_model_download('./model_download/', 'DEV')

    # Step1 同步模板

    # Step2 同步参数
    # conn, cursor = db_init('HN', "UAT")
    # cursor.execute(contract_para_sync())

    # Step3 同步参数集
    # model_para_sync()

    # Step4 同步模板定义
    # print(model_condition_line())
    # Step5 模板条件定义

#  model_replace('./model_download/', 'UAT')
