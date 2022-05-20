import pymysql as mysql
import pandas as pd
con = mysql.connect(host="数据库地址",port=端口号,user="用户名",passwd="密码",db="数据库名称",charset="utf8mb4")
mycursor = con.cursor()
print("连接成功")

# 查询
sql = "select * from 数据库表名 where 字段名=xx and .."
result = pd.read_sql(sql,con=con)
print(result)
#删除
sql = "delete from 数据库表名"
mycursor.execute(sql)
print("删除数据长度：",mycursor.rowcount)
