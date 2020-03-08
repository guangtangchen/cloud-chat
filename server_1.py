# -*- coding: utf-8 -*-

import socket
import threading
import pymysql
import time

PORT = 9999
SLEEP_TIME = 5
SIZE = 100000
MYSQL_USERNAME = 'your_name'   # 比如root
MYSQL_PASSWORD = 'password'
MYSQL_DATABASE = 'cloud_chat'
HARM_STRING = [' ', 'select', 'SELECT', '-', ';', 'DROP', 'drop']

con_list = []
name_list = []


def sql_injection_safe(string):
    """
    检测目标字符串是否含有可能引起sql注入攻击的字符串
    :param string: 待检测字符串
    :return: bool
    """
    for key in HARM_STRING:
        if key in string:
            return False
    return True


def trans(con1):
    """
    接收该连接发送的消息，无情的转发机器
    """
    con1.sendall(f'----系统消息----：您已进入聊天室，这里面目前有{len(con_list)}位成员\n'.encode())
    for item in con_list:   # 为每一位在线成员广播
        if item == con1:
            pass
        else:
            item.sendall(f"----系统消息----：'{name_list[con_list.index(con1)]}'已进入聊天室".encode())
    while True:
        data = con1.recv(SIZE)
        remove_list = []
        for item in con_list:
            if item == con1:
                continue
            try:
                item.sendall(data)   # 尝试转发
            except:
                remove_list.append(item)   # 客户端已断开，准备移除
        for item in remove_list:
            name_list.remove(con_list.index(item))
            con_list.remove(item)   # 移除


def begin(con):
    """已建立连接，但处于待登录状态"""
    global con_list, name_list
    mark = 0   # 初始化为非正常状态
    info = con.recv(1024).decode()   # 此为用户发来的账号和密码
    ty, name, pwd = info.split('{{')
    if ty == '0':      # 登录
        mark = sign_in(name, pwd)
    elif ty == '1':    # 注册
        mark = register(name, pwd)
    else:
        pass           # 不知道是啥，可能发生了什么错误
    con.sendall(str(mark).encode())   # 回复登录或者注册状态
    if mark in (1, 5):   # 登录成功，加入聊天室列表
        con_list.append(con)
        name_list.append(name)
    return mark


def sign_in(name, pwd):
    """
    用户登录的处理函数
    :param name: str, 账户名
    :param pwd: str, 账户密码（加密后）
    :return: int, 登陆结果状态
    """
    if not sql_injection_safe(name):   # 检测sql注入攻击
        mark = 3
        return mark
    db = pymysql.connect('localhost', MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE)
    cursor = db.cursor()
    command = "SELECT password FROM user_info WHERE username='" + name + "'"
    cursor.execute(command)
    data = cursor.fetchall()
    if data:
        if data[0][0] == pwd:
            mark = 1    # 密码和用户名均正确
        else:
            mark = 2    # 密码错误
    else:
        mark = 3        # 用户不存在
    cursor.close()
    db.close()
    return mark


def register(name, pwd):
    """
    用户注册的处理函数
    :param name: str, 账户名
    :param pwd: str, 账户密码(已加密)
    :return: int, 注册状态代码
    """
    if not sql_injection_safe(name):   # 检测sql注入攻击
        mark = 4
        return mark
    db = pymysql.connect('localhost', MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE)
    cursor = db.cursor()
    command = "SELECT password FROM user_info WHERE username='" + name + "'"
    cursor.execute(command)
    data = cursor.fetchall()
    if data:
        mark = 4   # 用户名已被注册
    else:
        try:
            command = f"INSERT user_info(username, password) VALUES('{name}', '{pwd}')"
            cursor.execute(command)   # 将注册信息写入数据库
            command = f"UPDATE user_info SET file_name = " \
                      f"'cloud_chat_data/msg_record/{name}.txt' WHERE username = '{name}'"
            cursor.execute(command)    # 新建一个该用户聊天记录文件
            db.commit()
            mark = 5   # 注册成功
        except:
            mark = 6   # 未知错误，重新注册
    cursor.close()
    db.close()
    return mark


def connection(con):
    """建立连接，但还需要校验登录或者注册状态"""
    con.sendall('成功连接服务器！'.encode())
    status_1 = 0   # 初始化状态为非正常状态
    while status_1 not in (1, 5):  # 1和5分别代表登录成功和注册成功
        status_1 = begin(con)   # 如果处于非正常状态，会一直循环处理该连接（比如一直密码输错等）
    threading.Thread(target=trans, args=(con,)).start()   # 登陆成功，新建一个线程监听该用户的发出消息


def main():
    global con_list
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    print('server host is:', host)
    serversocket.bind((host, PORT))
    print('server is listen at port:', PORT)
    serversocket.listen(100)
    con_list = []
    while True:
        while len(con_list) <= 100:
            con1, addr1 = serversocket.accept()
            print('connected by:', addr1)
            threading.Thread(target=connection, args=(con1,)).start()   # 有新的连接尝试建立，新建线程进入用户校验状态
        time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    main()
