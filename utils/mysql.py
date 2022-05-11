#-*- coding: utf-8 -*-
from DBUtils.PooledDB import PooledDB
import pymysql
from utils.config import mysql_info


class DB_POOL():
    __pool = None
    def __init__(self,db_name):
        self.__pool = PooledDB(pymysql, mincached=1, maxcached=20, host=mysql_info['host'], user=mysql_info['user'],
                          passwd=mysql_info['passwd'], db=db_name, port=3306, setsession=['SET AUTOCOMMIT = 1'],
                          cursorclass=pymysql.cursors.DictCursor, charset='utf8mb4')


    def to_connect(self):
        return self.__pool.connection()

    def is_connected(self, conn):
        """Check if the server is alive"""
        try:
            conn.ping(reconnect=True)
            # print("db is connecting")
        except:
            conn = self.to_connect()
            print("db reconnect")
        return conn

    def __getInsertId(self, cursor):
        cursor.execute('select @@IDENTITY AS id')
        result = cursor.fetchall()
        return result[0]['id']

    def __query(self, sql, param=None):
        conn = self.__pool.connection()
        cursor = conn.cursor()
        if param is None:
            count = cursor.execute(sql)
        else:
            count = cursor.execute(sql, param)
        return count, cursor

    def getAll(self, sql, param=None):
        # param查询条件值(元组\列表)
        # 返回list\boolean
        count, cursor = self.__query(sql, param)
        if count >= 1:
            res = cursor.fetchall()
        else:
            res = False
        return res

    def getOne(self, sql, param=None):
        count, cursor = self.__query(sql, param)
        if count >= 1:
            res = cursor.fetchone()
        else:
            res = False
        return res

    def getMany(self, sql, num, param=None):
        count, cursor = self.__query(sql, param)
        if count >= 1:
            res = cursor.fetchmany(num)
        else:
            res = False
        return res

    def insertOne(self, sql, value):
        conn = self.__pool.connection()
        cursor = conn.cursor()
        cursor.execute(sql, value)
        return self.__getInsertId(cursor)

    def update(self, sql, param=None):
        return self.__query(sql, param)[0]

    def insert_dict(self, dic, table_name):
        placeholder = ','.join(['%s' for i in range(len(dic.values()))])
        sql = f"insert into {table_name} ({','.join(dic.keys())}) values ({placeholder})"
        # print('sql', sql)
        return self.insertOne(sql, tuple(dic.values()))

db = DB_POOL('weibo')

if __name__ == '__main__':
    db = DB_POOL('weibo')
    sql = 'select * from top100'
    res1 = db.getOne(sql)
    res2 = db.getAll(sql)
    res3 = db.getMany(sql, 100)
    res4 = db.insertOne("insert into top100(date, period_type, score, field_id, field_name, curr_rank, uid, screen_name) values (%s, %s,%s, %s, %s,%s,%s,%s)", ('20220418', 'month',96.4, 1001,'时尚美妆',2,3929704484,'美妆笔记Lucia'))
    res5 = db.update("update top100 set date='20220424' where uid=3929704484")

    print(res1)
    print(len(res2))
    print(len(res3))
    print(res4)
    print(res5)

