import cx_Oracle as co


import csv


# 连接

orcl = co.connect('dbuser/dbpwd@ip_address:port/tns')

#创建游标

curs = orcl.cursor()

#编写sql语句

sql = "select * from table_name"

#执行sql语句

curs = curs.execute(sql)

#查看数据库数据

data = curs.fetchall()

# print(data)

#获取表的列名

title = [i[0] for i in curs.description]

#将数据写入csv文件

try:

with open("table_name.csv",'w') as csvfile:

writer = csv.writer(csvfile)

writer.writerow(title)

writer.writerows(data)

except:

print("文件写入数据错误")

finally:

finally :

curs.close()

orcl.close()