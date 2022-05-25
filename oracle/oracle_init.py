import json
import logging
import cx_Oracle
from jsons.pretty_print import pretty_print


def trans_json(result, columns):
    data_list = []
    if len(result[0]) != len(columns):
        print("列数不匹配")
    else:
        for record in result:
            data_record = {}
            for i in range(len(record)):
                data_record[str(columns[i][0])] = record[i]
            data_list.append(data_record)
    return data_list


def get_db_info(project, env):
    file = open("../jsons/db_setting.json", "rb")
    file_json = json.load(file)
    for project_list in file_json:
        if project == project_list["project"]:
            for env_info in project_list["env_info"]:
                if env == env_info["env"]:
                    return env_info["db_username"], env_info["db_password"], env_info["db_url"]


def db_init(project, env):
    if env in ["DEV", "UAT", "PROD"]:
        user, password, link = get_db_info(project, env)
        conn = cx_Oracle.connect(user, password, link)
        cursor = conn.cursor()
        return conn, cursor
    else:
        logging.error("环境变量配置错误")
        exit(0)


def exec_sql_ultra(cursor, sql):
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        res = []
        column_property = []
        for i in result:
            list_list = list(i)
            des = cursor.description  # 获取表详情，字段名，长度，属性等
            dict_result = dict(zip([item[0] for item in des], list_list))  # 打包为元组的列表 再转换为字典
            column_property = dict(zip([item[0] for item in des], [item[1] for item in des]))
            res.append(dict_result)
        if len(res) > 0:
            return res, column_property
        else:
            logging.warning(f"未查询到数据，查询SQL为 {sql}")
    except Exception as e:
        logging.error(f"发生错误{e}，错误SQL为:\n{sql}")


def get_sp_sql(desc, project="currency"):
    file = open("../jsons/db_sql.json", "rb")
    file_json = json.load(file)
    for project_list in file_json:
        if project == project_list["project"]:
            for data in project_list["data"]:
                if data["description"] == desc:
                    return data["sql"], data["para"]


def format_split(para, para_value):
    split_str = ""
    if len(para) != len(para_value):
        logging.error('参数个数不匹配')

    elif len(para) == 0 or len(para_value) == 0:
        return ''
    else:
        for i in range(len(para)):
            split_str += f"{para[i]}='{para_value[i]}', "

        return f".format({split_str[:-2]})"


def execute_model_sql(cursor, model_desc, model_paras, sql_type='currency'):
    sql, para = get_sp_sql(model_desc, sql_type)
    return exec_sql_ultra(cursor, eval(f''' "{sql}" ''' + format_split(para, model_paras)))[0]


def get_table_pk(cursor, table_name):
    res = execute_model_sql(cursor, model_desc="get_table_pk", model_paras=[table_name])
    return res[0][0]['COLUMN_NAME']


def main():
    conn, cursor = db_init('HN', 'DEV')
    # 获取工作流参数
    pretty_print(execute_model_sql(cursor=cursor, sql_type="HN",
                                   model_desc="get_instance_info", model_paras=["52559"]))
    #
    # # 获取表列描述信息
    # pretty_print(execute_model_sql(cursor=cursor, sql_type="currency",
    #                                model_desc="get_column_description", model_paras=["hls_bp_master", "bp_name"]))
    #
    # # 获取错误日志
    # pretty_print(execute_model_sql(cursor=cursor, sql_type="HN",
    #                                model_desc="get_error_log", model_paras=[]))
    #
    # # 获取工作流日志
    # pretty_print(execute_model_sql(cursor=cursor, sql_type="HN",
    #                                model_desc="get_instance_log", model_paras=["57038"]))


if __name__ == '__main__':
    main()
