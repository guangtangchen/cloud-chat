# -*- coding: utf-8 -*-
# 陈光堂 2019秋计算机网络与通信大作业 guangtangchen@gmail.com

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import socket
import threading
import time
import winreg
import os
import datetime
import hashlib
from get_all_files_relative_filepath import get_relative_filepath, get_file_size
from get_file_info import get_file_info
from my_audio import record_audio_main, run_audio_main


SERVER_IP = 'your server ip address'
SERVER_PORT = 'port of server'
FONT_0 = ('方正小标宋简体', 30, 'bold')
FONT_1 = ('微软雅黑', 20)
FONT_2 = ('宋体', 15)
FONT_3 = ('宋体', 20)
FONT_MINI = ('宋体', 14)
FONT_NO = ('宋体', 20, 'bold')
nickname = ''
password = ''
target_file = ''
target_folder = ''
relative_path = ''
abs_path = ''
count = 0
msg_all = ''
sys_msg = '----系统消息----：'
sleep_time = 0.3
size = 1000000
get_audio_name = ''
meaning = {0: '未知错误，请重新登录',
           1: '登陆成功',
           2: '密码错误,请检查用户名及密码输入是否正确',
           3: '用户不存在，请检查用户名输入是否正确',
           4: '用户名已被注册，请重新选择用户名',
           5: '注册成功！'}


def get_desktop_path():
    """获取windows桌面路径"""
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r'Software\Microsoft\Windows\CurrentVersion'
                         r'\Explorer\Shell Folders')
    return winreg.QueryValueEx(key, 'Desktop')[0]


def make_dir(formal_path):
    """
    新建路径
    :param formal_path: str
    :return: None
    """
    if os.path.exists(formal_path) or os.path.isfile(formal_path):
        pass
    else:
        os.makedirs(formal_path)


def msg_window_add(msg_add):
    """
    给文本框添加消息显示，先解除锁定再添加消息，随后恢复锁定
    :param msg_add: str, 要显示的消息
    :return: None
    """
    msg_all.config(state=NORMAL)   # msg_all运行到这里来时已经变成一个text对象，可忽略ide警告
    msg_all.insert(END, msg_add + '\n')   # 在末尾添加
    msg_all.config(state=DISABLED)
    msg_all.see(END)   # 保持最后一行始终在显示页面范围内


def run_audio():
    """播放语音"""
    run_audio_main(get_audio_name)


def record_audio():
    """录制语音"""
    current_time = '-'.join('-'.join(str(datetime.datetime.now())[:19].split()).split(":"))
    audio_name = desktop_path + "/" + current_time + '.wav'
    thr_record = threading.Thread(target=record_audio_main, args=(audio_name, ))
    thr_record.start()
    thr_record.join()   # 录制时阻塞线程
    msg_window_add(sys_msg + f'正在传输音频文件【{audio_name}】，请勿进行其他操作')
    t3 = threading.Thread(target=send_file, args=(audio_name,))
    t3.start()


def get_file_from_server():  # get_file_step2
    """收取单个文件的函数（或是文件夹中的一个文件）"""
    global count, get_audio_name
    data_3 = client.recv(size)  # 单个文件前导信息
    try:
        filename = data_3.decode()
    except UnicodeDecodeError:
        filename = 'over'
    if filename == 'over':   # 本个文件收取完成
        return
    filename, file_size_need = filename.split('}}')[0], int(filename.split('}}')[-1])
    path = desktop_path + '\\copy_' + filename
    file_info = get_file_info(path)
    make_dir(file_info[2])
    f = open(path, 'wb')
    if path.split('.')[-1] == 'wav':
        get_audio_name = path
    data_3 = client.recv(size)
    count_temp = 0
    while True:
        try:
            msg = data_3.decode()
            if msg == 'over':
                f.close()
                count += 1
                msg_window_add(sys_msg + f'已接收{count}个文件')
                break   # 本个文件收取完毕，退出返回
            else:
                print(count_temp)
                f.write(data_3)
        except UnicodeDecodeError:
            f.write(data_3)
        file_size_get = os.path.getsize(path)
        if file_size_get < file_size_need:
            data_3 = client.recv(size)   # 小于文件大小，继续收取
        else:
            data_3 = 'over'.encode()   # 完全接收，把data_3设置为over，再去循环就会退出
    return


def get_file():
    """
    客户端文件收取管理函数
    :return: None
    """
    global count
    count = 0
    msg_window_add(sys_msg + 'file transfer begin...' + '\n' + sys_msg + '传输中')
    head = client.recv(size)   # 获取文件的前导信息，路径以及大小
    head = 'copy_' + head.decode()
    head, folder_size_need = head.split('{{')[0], int(head.split('{{')[-1])
    path_get = desktop_path + '\\' + head   # 文件将保存至桌面
    while True:
        folder_size_get = get_file_size(path_get)   # 当前文件夹内所有文件的大小
        mark = 1
        if folder_size_get >= folder_size_need:    # 比较文件大小，确定是否继续接收
            mark = 0
        else:
            get_file_from_server()   # 继续收取一个文件
        if mark == 0:
            break   # 已完成所有文件的收取
    msg_window_add(sys_msg + f'传输完成!共收到{count}个文件,名为:{head}')


def send_file_client(j):
    """
    文件（单个）发送的客户端程序
    :param j: int, relative_path[j]
    :return: None
    """
    msg = relative_path[j]
    time.sleep(sleep_time)
    file_size = os.path.getsize(abs_path[j])
    msg = msg + '}}' + str(file_size)
    client.sendall(msg.encode())   # 先把单个文件路径和大小传过去
    f = open(abs_path[j], 'rb')
    while True:
        temp_1 = f.read(size)
        if not temp_1:
            msg = 'over'
            time.sleep(sleep_time*2)
            client.sendall(msg.encode())  # 当前文件传输完成标志
            break
        else:
            time.sleep(sleep_time)
            client.sendall(temp_1)


def send_file(path):
    """
    发送文件的线程，发了三次信息，第一次代表接下俩即将传输文件，第二个是文件夹的目录信息，随后每个文件还单独传一下自己的信息
    :param path: str, 目标文件/文件夹
    :return: None
    """
    global abs_path, relative_path
    head = path.split('/')[-1].split('\\')[-1]
    abs_path, no_use, relative_path = get_relative_filepath(path)
    lenth = len(relative_path)
    time.sleep(sleep_time)
    client.sendall('file transmission begin!'.encode())
    folder_size = get_file_size(path)
    head = head + '{{' + str(folder_size)
    time.sleep(sleep_time)
    client.sendall(head.encode())
    for i in range(lenth):
        send_file_client(i)   # 文件发送客户端程序
        msg_window_add(sys_msg + f'传输比例：{i + 1} / {lenth}')
    msg_window_add(sys_msg + '传输完成！')
    if path.split('.')[-1] == 'wav':     # 如果是录制的暂存语音文件，传输完成后删除它
        os.remove(path)
    else:
        pass


def destroy_all():
    """
    退出程序
    """
    client.sendall(f"'{nickname}'退出会话".encode())
    root.destroy()


def encryption(string):
    """
    将传输的密码进行md5单向加密
    :param string: str, password
    :return: str, 加密后的password
    """
    md5_inst = hashlib.md5()
    md5_inst.update(string.encode('utf-8'))
    return str(md5_inst.digest())


def sign_in(event=None):
    """
    登录函数
    """
    global nickname, password
    nickname = user_id.get()
    password = user_password.get()
    password = encryption(str(password))   # 加密
    msg = '0' + '{{' + f'{nickname}' + '{{' + f'{password}'   # 0代表登录已有账户
    client.sendall(msg.encode())
    status = int(client.recv(1024).decode())
    if status == 1:
        destory_page_0()    # 登陆成功，进入聊天室页面
    elif status in meaning:
        messagebox.showinfo(message=meaning[status])
    else:
        messagebox.showinfo(message='糟糕~，出错啦，请重启客户端~')


def register(event=None):
    """
    注册函数
    """
    global nickname, password
    nickname = user_id.get()
    password = user_password.get()
    password = encryption(str(password))   # 加密
    msg = '1' + '{{' + str(nickname) + '{{' + str(password)   # 1，代表为注册，{{为分隔符
    client.sendall(msg.encode())
    status = int(client.recv(1024).decode())   # 获取服务器返回的状态码
    if status == 5:
        destory_page_0()   # 注册成功，进入聊天页面
        messagebox.showinfo(message=meaning[5])
    elif status in meaning:
        messagebox.showinfo(message=meaning[status])
    else:
        messagebox.showinfo(message='糟糕~，出错啦，请重启客户端~')  # 未知错误


def destory_page_0(event=None):   # 主页面
    """
    销毁登陆页面，构建page_1，即聊天室页面
    """
    page_0.destroy()

    def send_text(event_1=None):    # event=None很关键，既可以让bind可以有事件绑定，也可以使command不报错
        """
        将用户输入的消息发送给服务器，服务器进行广播
        """
        msg = nickname + ': ' + text.get()
        time.sleep(0.2)
        client.sendall(msg.encode())
        text.set('')   # 发送完成，清空输入框
        msg_window_add(msg)

    def get_msg():
        """
        作为一个独立运行的线程，收取服务器转发的消息
        """
        while True:
            try:
                msg_get = client.recv(size).decode()
            except UnicodeDecodeError:
                continue
            if msg_get == 'file transmission begin!':   # 说明接下来传输的时文件，进入收文件程序
                t1 = threading.Thread(target=get_file, args=())
                t1.start()
                t1.join()   # 文件未收取完成前不得收取其他消息
            elif msg_get == 'over' or msg_get == '--copy--':
                pass
            else:
                msg_window_add(msg_get)   # 普通消息，直接显示在消息框

    def build_file_window():
        """
        用户想要发送文件，但还需要用户选择文件还是文件夹(二者调用的tkinter函数不一样)
        """
        def open_file():
            global target_file
            target_file = filedialog.askopenfilename()
            temp1.destroy()
            print(target_file)
            msg_window_add(sys_msg + f'正在传输文件【{target_file}】，请勿进行其他操作')
            t2 = threading.Thread(target=send_file, args=(target_file,))   # 启动发送文件的线程
            t2.start()

        def open_folder():
            global target_folder
            target_folder = filedialog.askdirectory()
            temp1.destroy()
            print(target_folder)
            msg_window_add(sys_msg + f'正在传输文件【{target_folder}】，请勿进行其他操作')
            t3 = threading.Thread(target=send_file, args=(target_folder,))   # 启动发送文件的线程
            t3.start()

        temp1 = Tk()
        temp1.title('请选择')
        Button(temp1, text='选择单个文件', width=30, command=open_file, font=FONT_2).pack(fill='x', pady=10)
        Button(temp1, text='选择文件夹', width=30, command=open_folder, font=FONT_2).pack(fill='x')
        temp1.mainloop()

    # 开始构建页面组件
    page_1 = Frame(root)
    frame_1 = Frame(page_1)
    frame_1.pack()
    Label(frame_1, text=f'当前用户：{nickname}', font=FONT_MINI).pack()
    global msg_all
    msg_all = Text(frame_1, height=20, width=80, font=FONT_MINI)   # msg_all是一个text文本框对象
    msg_all.config(state=DISABLED)   # 不允许用户编辑，仅用作展示消息
    msg_all.pack()
    Button(page_1, text='录制语音', font=FONT_2, command=record_audio).pack(side='left', pady=10, fill='x', padx=5)
    Button(page_1, text='播放语音', font=FONT_2, command=run_audio).pack(side='left', pady=10, fill='x', padx=5)
    text = StringVar()
    text_input = Entry(page_1, width=40, textvariable=text, font=FONT_2)
    text_input.pack(side='left', padx=5)
    text_input.bind('<Return>', send_text)   # 绑定enter，发送消息更方便
    Button(page_1, text='发送', font=FONT_2, command=send_text).pack(pady=10, side='left', fill='x', padx=5)
    Button(page_1, text='发送文件', font=FONT_2, command=build_file_window).pack(pady=10, side='left', fill='x', padx=5)
    Button(page_1, text='退出', font=FONT_2, command=destroy_all).pack(pady=10, side='left', fill='x', padx=5)
    page_1.pack()
    threading.Thread(target=get_msg, args=()).start()   # 组件构建完毕，启动接收消息的线程


root = Tk()
root.title('Cloud Chat')
# page_0  启动页
desktop_path = get_desktop_path()
page_0 = Frame(root)
page_0.pack()
frame_1 = Frame(page_0)
frame_1.pack(side='left')
im = PhotoImage(file='猫鼬.png')
Label(page_0, image=im).pack(side='right', padx=30)
Label(frame_1, text='Hello，欢迎访问云聊天！', font=FONT_0, fg='blue').pack(side='top', pady=80, expand='yes')

frame_2 = Frame(frame_1)
frame_2.pack()
Label(frame_2, text='请输入昵称:', font=FONT_3).pack(side='left', padx=30)
user_id = StringVar()
Entry(frame_2, width=30, relief='sunken', font=FONT_3, textvariable=user_id).pack()
frame_3 = Frame(frame_1)
frame_3.pack()
Label(frame_3, text='请输入密码:', font=FONT_3).pack(side='left', padx=30)
user_password = StringVar()
temp = Entry(frame_3, width=30, relief='sunken', font=FONT_3, textvariable=user_password)
temp.pack(pady=20)
temp.bind('<Return>', sign_in)   # 监控enter键，也可以触发登录

frame_4 = Frame(frame_1)
frame_4.pack()
Button(frame_4, text='登录', font=FONT_1, width=20, command=sign_in).pack(expand='yes', side='left', padx=10)
Button(frame_4, text='注册', font=FONT_1, width=20, command=register).pack(expand='yes', side='left', padx=10)
Label(frame_1, text='点击注册，将根据上述昵称和密码\n自动注册，注意昵称不能重复，不能含有空格',
      font=FONT_MINI, width=40).pack(expand='yes', pady=10)
connect_state_yes = Label(frame_1, text='已成功连接服务器！', font=FONT_MINI, width=40, fg='blue')
connect_state_no = Label(frame_1, text='服务器连接失败！请检查网络或重启客户端', font=FONT_NO, width=40, bg='red')

try:    # 进入程序便尝试连接服务器
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = SERVER_IP
    port = SERVER_PORT
    client.connect((host, port))
    data = client.recv(size).decode()
    connect_state_yes.pack()       # 成功连接
except:
    connect_state_no.pack()     # 连接失败
finally:
    Label(frame_1, text='CopyRight.@BUAA-GuangtangChen').pack()

root.mainloop()

