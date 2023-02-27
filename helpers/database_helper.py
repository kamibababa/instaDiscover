import mysql.connector

from enum import Enum


class TABLE(Enum):
    DISCOVER_USERS = 'discover_users'


connection = mysql.connector.connect(
    host='127.0.0.1', database='insta_discover', user='root', password=''
)
cursor = connection.cursor(dictionary=True)


def check_status():
    return connection.is_connected()


def commit():
    connection.commit()


def close():
    cursor.close()
    connection.close()


def insert(table, data):
    query = "INSERT INTO " + table + " ("
    for key in data.keys():
        query += key + ","
    query = query.rstrip(',') + ')'
    query += ' VALUES ('
    for value in data.values():
        query += "'" + str(value) + "',"
    query = query.rstrip(',') + ')'
    return cursor.execute(query)


def find_all(table, columns='*'):
    query = "SELECT " + columns + " FROM " + table + ""
    cursor.execute(query)
    return cursor.fetchall()


def find(table, criteria='', columns='*'):
    query = "SELECT " + columns + " FROM " + table + ""
    if criteria != '':
        query += ' WHERE ' + criteria
    cursor.execute(query)
    return cursor.fetchone()


def update(table, criteria, data, commit_status=True):
    query = "UPDATE " + table + " SET "
    for key, value in data.items():
        query += key + " = '" + str(value) + "',"
    query = query.rstrip(',')
    if criteria != '':
        query += ' WHERE ' + criteria
    print(query)
    result = cursor.execute(query)
    if commit_status is True:
        commit()
    return result
