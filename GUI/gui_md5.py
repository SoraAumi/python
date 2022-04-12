#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
from tkinter import *
import cx_Oracle
import time
import easygui as e
import xlwt

LOG_LINE_NUM = 0


def get_current_time():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return current_time


def get_db_info(project, env):
    file = open("./db_setting/db_setting.json", "rb")
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


archive_sql_model = \
    '''
    begin
        hn_simple_util_pkg.ARCHIVE_BATCH_AUTO();
        commit;
    end;
'''


class MY_GUI():
    def __init__(self, init_window_name, cursor):
        self.init_window_name = init_window_name
        self.cursor = cursor
        self.current_data = []

    # 设置窗口
    def set_init_window(self):
        self.init_window_name.title("文本处理工具_v1.2")  # 窗口名
        # self.init_window_name.geometry('320x160+10+10')                         #290 160为窗口大小，+10 +10 定义窗口弹出时的默认展示位置
        self.init_window_name.geometry('1068x681+10+10')
        # self.init_window_name["bg"] = "pink"
        # #窗口背景色，其他背景色见：blog.csdn.net/chl0000/article/details/7657887 self.init_window_name.attributes("-alpha",
        # 0.9)                          #虚化，值越小虚化程度越高 标签
        self.init_data_label = Label(self.init_window_name, text="待处理数据")
        self.init_data_label.grid(row=0, column=0)
        self.result_data_label = Label(self.init_window_name, text="输出结果")
        self.result_data_label.grid(row=0, column=12)
        self.log_label = Label(self.init_window_name, text="日志")
        self.log_label.grid(row=12, column=0)
        # 文本框
        self.init_data_Text = Text(self.init_window_name, width=67, height=35)  # 原始数据录入框
        self.init_data_Text.grid(row=1, column=0, rowspan=10, columnspan=10)
        self.result_data_Text = Text(self.init_window_name, width=70, height=49)  # 处理结果展示
        self.result_data_Text.grid(row=1, column=12, rowspan=15, columnspan=10)
        self.log_data_Text = Text(self.init_window_name, width=66, height=9)  # 日志框
        self.log_data_Text.grid(row=13, column=0, columnspan=10)
        # 按钮
        self.str_trans_to_md5_button = Button(self.init_window_name, text="执行", bg="lightblue", width=10,
                                              command=self.str_execute_sql)  # 调用内部方法  加()为直接调用
        self.str_trans_to_md5_button.grid(row=1, column=11)
        self.export_excel_button = Button(self.init_window_name, text="导出EXCEL", bg="lightblue", width=10,
                                          command=self.export_data_to_excel)  # 调用内部方法  加()为直接调用
        self.export_excel_button.grid(row=2, column=11)
        self.export_excel_button = Button(self.init_window_name, text="档案归档模板", bg="lightblue", width=10,
                                          command=self.set_model)  # 调用内部方法  加()为直接调用
        self.export_excel_button.grid(row=3, column=11)

    def set_model(self):
        self.init_data_Text.delete(1.0, 'end')
        self.init_data_Text.insert(1.0, archive_sql_model)

    def export_data_to_excel(self, file_path=''):
        try:
            data = self.current_data
            title = [i[0] for i in self.cursor.description]
            xls_path = file_path + 'export.xls'
            workbook = xlwt.Workbook(encoding='utf-8')
            worksheet = workbook.add_sheet('sql_query_sheet')
            for idx, column in enumerate(title):
                worksheet.write(0, idx, column)
            for row, record in enumerate(data):
                for line, column_data in enumerate(list(record)):
                    worksheet.write(row + 1, line, column_data)
            workbook.save(xls_path)
        except Exception as ex:
            self.result_data_Text.delete(1.0, END)
            self.result_data_Text.insert(1.0, ex)

    # 功能函数
    def str_execute_sql(self):
        src = self.init_data_Text.get(1.0, END).strip().replace("\n", "").encode()
        if "where" not in str(src) and "select" in str(src):
            e.msgbox("请在查询条件里面增加where否则加载的速度比较慢")
            return
        if src:
            try:
                self.cursor.execute(src)
                self.init_data_Text.delete(1.0, 'end')
                src = str(src)
                if "begin" not in src:
                    self.current_data = self.cursor.fetchall()
                self.result_data_Text.insert(1.0, self.current_data)
                self.write_log_to_Text(src + '执行成功')
            except Exception as ex:
                src = str(src)
                self.result_data_Text.delete(1.0, END)
                self.write_log_to_Text(src + '执行失败')
                self.write_log_to_Text(ex)
                print(ex)
        else:
            self.write_log_to_Text("ERROR:str_trans_to_md5 failed")

    # 日志动态打印
    def write_log_to_Text(self, log_msg):
        global LOG_LINE_NUM
        current_time = get_current_time()
        log_msg_in = str(current_time) + " " + str(log_msg) + "\n"  # 换行
        if LOG_LINE_NUM <= 7:
            self.log_data_Text.insert(END, log_msg_in)
            LOG_LINE_NUM = LOG_LINE_NUM + 1
        else:
            self.log_data_Text.delete(1.0, 2.0)
            self.log_data_Text.insert(END, log_msg_in)


def gui_start(cursor):
    init_window = Tk()  # 实例化出一个父窗口
    ZMJ_PORTAL = MY_GUI(init_window, cursor)
    # 设置根窗口默认属性
    ZMJ_PORTAL.set_init_window()

    init_window.mainloop()  # 父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示


if __name__ == '__main__':
    return_type = e.buttonbox(msg='请选择运行环境', title='Oracle运行 V0.1', choices=['DEV', 'UAT', 'PROD'])
    db_conn, db_cursor = db_init('HN', return_type)
    gui_start(db_cursor)
    db_cursor.close()
    db_conn.close()
