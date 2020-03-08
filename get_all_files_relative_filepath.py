import os
# 输入一个文件夹路径，返回文件夹下所有文件的绝对路径以及除去输入部分的相对路径
# relative_path_2为包含的path最后一级目录的相对目录


def get_file_size(path):
    """
    获取目标文件夹的所有文件大小之和
    :param path: str, 文件夹路径
    :return: int
    """
    size = 0
    for item in get_relative_filepath(path)[0]:
        size += os.path.getsize(item)
    return size


def get_relative_filepath(path):
    """
    获取文件夹内文件的相关信息
    :param path: str, eg c:/users/guang/desktop/2020寒假
    :return: tuple, eg
    (['c:/users/guang/desktop/2020寒假\\Flask学习笔记.docx'],
    ['Flask学习笔记.docx'],
    ['2020寒假\\Flask学习笔记.docx'])
    """
    abs_path = []
    relative_path = []
    relative_path_2 = []
    head = path.split('/')[-1].split('\\')[-1]
    if os.path.isfile(path):
        abs_path.append(path)
        relative_path.append(head)
        relative_path_2.append(head)
        return abs_path, relative_path, relative_path_2
    lenth = len(path) + 1
    for root, dirs, files in os.walk(path):   # 游走文件夹获取文件
        for name in files:
            temp = root + '\\' + name
            abs_path.append(temp)
            relative_path.append(temp[lenth:])
            relative_path_2.append(head + '\\' + temp[lenth:])
    return abs_path, relative_path, relative_path_2




