import datetime
import logging
import xlrd


# 获取xls文档行列
def get_excel_row_col(path, sheet_name):
    read_book = xlrd.open_workbook(path)

    sheet = read_book.sheet_by_name(sheet_name)

    n_rows = sheet.nrows
    n_cols = sheet.ncols

    sheet_data = []

    for i in range(n_rows):
        xls_list = []
        for j in range(n_cols):
            if sheet.cell(i, j).ctype == 3:
                time_str = xlrd.xldate_as_datetime(sheet.cell(i, j).value, 0).strftime('%Y/%m/%d %H:%M:%S')
                xls_list.append(time_str)
            elif sheet.cell(i, j).ctype == 2:
                xls_list.append(int(sheet.cell(i, j).value))
            else:
                xls_list.append(sheet.cell(i, j).value)
        sheet_data.append(xls_list)

    return sheet_data


# 获取sql查询数据
def get_query_data(sheet_data):
    data_column = []

    data_list = []

    for idx, row in enumerate(sheet_data):
        data_dict = {}
        if idx == 0:
            for col in row:
                data_column.append(str.lower(col))
        else:
            for index, col in enumerate(row):
                data_dict[data_column[index]] = col
            data_list.append(data_dict)

    return data_list, data_column


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    excel_list, excel_column = get_query_data(get_excel_row_col("excels/担保额度历史数据收集表0520.xls", "担保总额申请收集"))
    for rec in excel_list:
        print(rec)


