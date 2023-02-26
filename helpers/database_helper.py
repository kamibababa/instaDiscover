import logging

import mysql.connector

from enum import Enum


class TABLE(Enum):
    DISCOVER_USERS = 'discover_users'


connection = mysql.connector.connect(
    host='127.0.0.1', database='insta_discover', user='root', password=''
)
cursor = connection.cursor()


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
        print(key)
        query += key + ","
    query = query.strip(',') + ')'
    query += ' VALUES ('
    for value in data.values():
        print(value)
        if type(value) is int:
            query += str(value) + ","
        else:
            query += "'" + str(value) + "',"
    query = query.strip(',') + ')'
    cursor.execute(query)
