from jsons.pretty_print import pretty_print
from oracle.oracle_init import db_init, execute_self_sql

conn, cursor = db_init("HN", "DEV")


def query_plan_by_plan_number(plan_number):
    sql = "select l.project_id, p.plan_id from hn_prj_plan_ln l, hn_prj_plan p " \
          "where l.plan_id = p.plan_id and l.plan_id = '{plan_number}'"
    return execute_self_sql(cursor=cursor, paras=[plan_number], para_desc=["plan_number"], sql=sql)


def query_content_by_content_number(content_number):
    sql = "select c.*, p.project_id from con_contract_content c, prj_project p " \
          "where p.VIRTUAL_CON_NUMBER = '{content_number}' and c.project_id = p.project_id"
    return execute_self_sql(cursor=cursor, paras=[content_number], para_desc=["content_number"], sql=sql)


def main_func(document_number):
    type_dic = [
        {"key": "PLAN", "desc": "项目方案"},
        {"key": "PRJ", "desc": "项目"},
        {"key": "HT", "desc": "合同"},
        {"key": "PLAN", "desc": "项目方案"}
    ]


if __name__ == '__main__':
    print(pretty_print(query_content_by_content_number('HT-HZ-2022016')))
