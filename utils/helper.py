import csv
import datetime
import os
import re
import time

def ensureDir(dir_path):
    d = os.path.dirname(dir_path)
    if not os.path.exists(d):
        os.makedirs(d)

def format_time(date, old_format, new_format):
    # 将时间转换成timeArray
    timeArray = time.strptime(date, old_format)
    # 用strftime转换成特定格式
    new_date = time.strftime(new_format, timeArray)
    return new_date

def write2csv(path, data):
    """将一维数据追加到csv文件"""
    with open(path, "a+", newline="", encoding='utf_8_sig') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(data)

def read_csv_line_num(path):
    """获取csv文件的行数"""
    # 确保文件存在，这里不能用w模式，因为会覆盖原文件的数据
    with open(path, "a+", encoding='utf_8_sig', newline="") as writefile:
        pass
    with open(path, 'r', encoding='utf_8_sig', newline="") as csvfile:
        reader = csv.reader(csvfile)
        return len(list(reader))

def get_file_size(path):
    """获取文件大小"""
    # 确保文件存在，这里不能用w模式，因为会覆盖原文件的数据
    with open(path, "a+", encoding='utf_8_sig', newline="") as writefile:
        pass
    return os.path.getsize(path)

def clear_html(str):
    """清除HTML标签"""
    alt = re.findall('alt="(.*?)"', str)
    alt = ''.join(alt)
    dr = re.compile(r'<[^>]+>', re.S)
    dd = dr.sub('', str)
    if '☞' in dd:
        dd = dd.replace('☞', '<')
    dd = dr.sub('', dd)
    return alt+dd

def time2str(f):
    """将时间转为标准时间格式：YYYY-mm-dd HH:MM:SS"""
    # f = 'Fri Jan 24 00:19:02 +0800 2020'
    year = f.split(' ')[-1]
    str2 = f[0:-10] + year
    dt = datetime.datetime.strptime(str2, '%a %b %d %H:%M:%S %Y')
    t=dt.strftime("%Y-%m-%d %H:%M:%S")
    return t

def textNumber2int(init_number):
    """将带有文字的数字转为纯数字"""
    init_number = str(init_number)  #  先统一化成str
    if len(init_number) == 0:
        return 0
    if '千' in init_number:
        number = int(float(init_number[:-1]) * 1000)
    elif '万' in init_number:
        number = int(float(init_number[:-1])*10000)
    elif '亿' in init_number:
        number = int(float(init_number[:-1])*100000000)
    elif '.' in init_number:
        number = float(init_number)
    else:
        number = int(init_number)

    return number

if __name__ == '__main__':
    print(textNumber2int(20.1))
    print(textNumber2int(20))
    print(textNumber2int('20千'))
    print(textNumber2int('20万'))
    print(textNumber2int('20亿'))