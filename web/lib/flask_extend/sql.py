import pymysql
from datetime import datetime


class SimplifyMysql(object):
    db = None
    sql_hostname = ''
    sql_username = ''
    sql_password = ''
    sql_database = ''

    def __init__(self, sql_hostname, sql_username, sql_password, sql_database):
        self.sql_hostname = sql_hostname
        self.sql_username = sql_username
        self.sql_password = sql_password
        self.sql_database = sql_database

        self.cursor = None

    def connect(self):
        self.db = pymysql.connect(self.sql_hostname, self.sql_username, self.sql_password, self.sql_database)
        self.cursor = self.db.cursor()

    def close(self):
        self.db.close()

    def insert(self, table, data):
        sql = 'INSERT INTO ' + table
        keys = ''
        f = ''
        values = []

        for key, value in data.items():
            if keys:
                keys += ','
            keys += key
            if f:
                f += ','
            if type(value) == int:
                f += '%s'
            elif type(value) == str:
                f += '%s'
                # value = pymysql.escape_string(value)
            elif type(value) == datetime:
                f += '''str_to_date(%s, '%%Y-%%m-%%d %%H:%%i:%%S')'''
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            values.append(value)

        sql += ' (' + keys + ') VALUES (' + f + ')'

        self.cursor.execute(sql, tuple(values))

    def delete(self, table, conditions):
        sql = 'DELETE FROM ' + table + ' WHERE '
        where = ''
        values = []

        for condition in conditions:
            if where:
                where += ' AND '
            where += condition[0] + condition[1]
            if type(condition[2]) == int:
                where += '%s'
            elif type(condition[2]) == str:
                where += '%s'
            values.append(condition[2])

        sql += where

        self.cursor.execute(sql, tuple(values))

    def select(self, table, conditions=None, limit=0, offset=0, order_by='', reverse=False):
        sql = 'SELECT * FROM ' + table + ' WHERE '
        where = ''
        values = []

        if conditions:
            for condition in conditions:
                if where:
                    where += ' AND '
                where += condition[0] + condition[1]
                if type(condition[2]) == int:
                    where += '%s'
                elif type(condition[2]) == str:
                    where += '%s'
                values.append(condition[2])
        else:
            where += 'TRUE'

        sql += where

        if order_by:
            sql += ' ORDER BY ' + order_by
            if reverse:
                sql += ' DESC'
            else:
                sql += ' ASC'

        sql += ' LIMIT ' + str(limit) if limit else ''
        sql += ' OFFSET ' + str(offset) if offset else ''

        self.cursor.execute(sql, tuple(values))

        return self.cursor.fetchall()

    def update(self, table, data, conditions):
        sql = 'UPDATE ' + table + ' SET '
        set_ = ''
        where = ''
        values = []

        for key, value in data.items():
            if isinstance(value, type(None)):
                continue

            if set_:
                set_ += ','
            set_ += key + '='
            if type(value) == int:
                set_ += '%s'
            elif type(value) == str:
                set_ += '%s'
            values.append(value)

        for condition in conditions:
            if where:
                where += ' AND '
            where += condition[0] + condition[1]
            if type(condition[2]) == int:
                where += '%s'
            elif type(condition[2]) == str:
                where += '%s'
            values.append(condition[2])

        sql += set_ + ' WHERE ' + where

        self.cursor.execute(sql, tuple(values))

    def execute(self, *sql):
        self.cursor.execute(*sql)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        self.db.commit()

    def cursor(self):
        return self.db.cursor()

    def create_table(self, table, key_list, items):
        sql = 'CREATE TABLE IF NOT EXISTS ' + table + '('

        for key in key_list:
            column = key
            column += ' ' + items[key]['value_type']
            column += ' PRIMARY KEY' if items[key]['primary_key'] else ''
            column += ' UNIQUE' if items[key]['unique'] else ''
            column += ' NOT NULL' if items[key]['not_null'] else ''
            column += ' AUTO_INCREMENT' if items[key]['auto_increment'] else ''
            column += ' DEFAULT ' + str(items[key]['default']) if items[key]['default'] else ''
            sql += column + ','

        sql = sql[:-1] + ')'

        self.execute(sql)
