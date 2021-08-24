import pymysql
from warnings import filterwarnings
from config.readconfig import ReadConfig

# 忽略mysql告警
filterwarnings("ignore", category=pymysql.Warning)


class MysqlDb(object):
    readconfig = ReadConfig(filepath='/Users/jijianfeng/Desktop/pythoncode/activity_decorate/config.ini')
    host = readconfig.get_db("Mysql-Database", "host")
    user = readconfig.get_db("Mysql-Database", "user")
    password = readconfig.get_db("Mysql-Database", "password")
    db = readconfig.get_db("Mysql-Database", "db")

    def __init__(self):
        # 建立数据库连接
        self.conn = pymysql.connect(host=MysqlDb.host, user=MysqlDb.user, password=MysqlDb.password,
                                    database=MysqlDb.db)
        #  使用cursor方法操作游标，得到一个可以操作sql语句，并且操作结果作为字典返回的游标
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def __del__(self):
        # 关闭游标
        self.cursor.close()
        # 关闭连接
        self.conn.close()

    def query(self, sql, state="all"):
        """
        查询
        @param sql:
        @param state: 默认查询全部
        @return:
        """
        self.cursor.execute(sql)
        if state == "all":
            data = self.cursor.fetchall()
        else:
            data = self.cursor.fetchone()
        return data

    def execute(self, sql):
        """
        新增，删除，修改
        @param sql:
        @return:
        """
        try:
            # 使用execute方法处理sal
            rows = self.cursor.execute(sql)
            # 提交事务
            self.conn.commit()
            return rows
        except Exception as e:
            print("数据库操作异常:{0}".format(e))
            # 异常后回滚
            self.conn.rollback()


if __name__ == '__main__':
    mydb = MysqlDb()
    # 查询
    # sql = "select * from `case`"
    # result = mydb.query(sql)

    # 新增
    # sql = "insert into `case`  (app) value ('测试')"
    # result = mydb.execute(sql)

    # 修改
    # sql = "update `case` set app = '测试123' where app = '测试' "
    # result = mydb.execute(sql)

    # 删除
    sql = "delete from `case` where app = '测试123' "
    result = mydb.execute(sql)
    print(result)

