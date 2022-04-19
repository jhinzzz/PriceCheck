# coding:utf-8

"""
@Time   :2022/4/19
@Author :evan.fang
@File   :GetError.py
@Desc   :获取错误信息
"""
import json
import csv
import os.path

# 项目目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 错误报告目录
ERROR_PATH = os.path.join(BASE_DIR, 'errorResult')
# 错误报告文件
ERROR_FILE = os.path.join(ERROR_PATH, 'error.csv')


def write_csv(errors):
    # 如果不存在，则创建一个新的
    if not os.path.exists(ERROR_PATH):
        os.makedirs(ERROR_PATH)

    with open('./errorResult/error.csv', "a", newline='') as f:
        # 打开csv文件
        f.seek(0)  # 光标定位到最开始
        f.truncate()  # 从光标位置开始删除
        # 写内容
        writer = csv.writer(f)
        writer.writerow(["nation", "order number"])
        for i in errors:
            writer.writerow(i)


if __name__ == '__main__':
    a = [['123123123', '123'], ['mad', 'mad']]
    a.append(['ddd', 'sda'])

    write_csv(a)
