def get_file_info(path):
    """
    获取单个文件的信息
    :param path: str, eg "c:/users/guang/desktop/2020寒假/Flask学习笔记.docx"
    :return: tuple, eg
    ('Flask学习笔记.docx', 'docx', 'c:/users/guang/desktop/2020寒假/')
    """
    frame = []
    temp1 = path.split('\\')
    for item in temp1:
        temp2 = item.split('/')
        for i in temp2:
            frame.append(i)
    file_name = frame[-1]
    file_type = frame[-1].split('.')[-1]
    formal_path = '/'.join(frame[:-1])
    return file_name, file_type, formal_path


