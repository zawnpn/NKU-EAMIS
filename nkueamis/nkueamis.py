#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2017-07-01 11:03
# @Author  : Wanpeng Zhang
# @Site    : http://www.oncemath.com
# @File    : nkueamis.py
# @Project : nkueamis

"""
Usage:
    nkueamis (-g | --grade) <course_category> [-u <username> -p <password>]
    nkueamis (-c | --course) [-u <username> -p <password>]

A simple tool to help get information in NKU-EAMIS(NKU Education Affairs Management Information System).

Arguments:
    course_category      the category of courses which you want to query(only can be combination of A,B,C,D,E)
    username             your username in NKU-EAMIS system
    password             your password in NKU-EAMIS system

Options:
    -g, --grade          grade query
    -c, --course         course query
    -u                   username
    -p                   password
    -h, --help           guidance

Examples:
    nkueamis -c
    nkueamis -g BCD
    nkueamis -g BCD -u your_username -p your_password
"""

from docopt import docopt
import re
import requests
from bs4 import BeautifulSoup
import prettytable
import getpass

COURSE_CAT = ['校公共必修课', '院系公共必修课', '专业必修课', '专业选修课', '任选课']
HOME_URL = 'http://eamis.nankai.edu.cn/eams/login.action'
GRADE_URL = 'http://eamis.nankai.edu.cn/eams/myPlanCompl.action'
COURSETABLE_QUERY_URL = 'http://eamis.nankai.edu.cn/eams/dataQuery.action'
COURSETABLE_ID_URL = 'http://eamis.nankai.edu.cn/eams/courseTableForStd.action'
COURSETABLE_URL = 'http://eamis.nankai.edu.cn/eams/courseTableForStd!courseTable.action'


# test the network
def test_net():
    conn = requests.get(HOME_URL)
    response_status = conn.status_code
    if response_status == '200':
        return False
    else:
        return True


# login to the system
def log_in(username=None, password=None):
    if not username or not password:
        username = input('Input your Student ID:')
        password = getpass.getpass('Input your password:')
    login_data = {
        'username': username,
        'password': password
    }
    s = requests.session()
    s.post(HOME_URL, data=login_data)
    return s


# find the category of course
def find_course_cat(i, content):
    pattern = re.compile(COURSE_CAT[i-1])
    result = pattern.findall(content)
    return result


# replace some irregular words
def replace_some_word(text):
    replace_origin = ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ']
    replace_target = ['I', 'II', 'III', 'IV']
    for i in range(4):
        text = text.replace(replace_origin[i], replace_target[i])
    return text


# get information of grades
def get_grade_info(i, table):
    result = []
    for info in table:
        if len(info('td')) == 8:
            result.append([replace_some_word(info('td')[2].text), info('td')[3].text, info('td')[5].text])
        if find_course_cat(i, info.text):
            result = []
        if i < 5 and find_course_cat(i+1, info.text):
            return result
    return result


# get grade information of specified courses
def get_specified_grade(resp, cat_list_str):
    result = []

    cat_list_num = [ord(i)-65 for i in cat_list_str.upper() if ord(i) in range(65,70)]
    soup = BeautifulSoup(resp.content.decode('utf-8'), 'html.parser')
    for i in cat_list_num:
        result.append(get_grade_info(i+1, soup('tr')))
    return result


# calculate the avg and sum of grade
def grade_calc(table):
    gradesum = 0
    scoresum = 0
    for cat in table:
        for i in cat:
            if i[2] != '--':
                gradesum += float(i[1])*float(i[2])
                scoresum += float(i[1])
    if scoresum:
        avg = gradesum/scoresum
    else:
        avg = 0
    return avg, scoresum


# convert str tuple into num tuple
def tuple_conv(strtuple):
    inttuple = []
    for i in strtuple:
        inttuple.append(int(i))
    return tuple(inttuple)


# get the necessary id to post data for course table
def get_std_course_id(resp):
    std_id_pattern = \
        re.compile('if\(jQuery\("#courseTableType"\)\.val\(\)=="std"\).*?form\.addInput\(form,"ids","(.+?)"\);', re.S)
    std_id = std_id_pattern.findall(resp.content.decode('utf-8'))
    return std_id


# get information of courses
def get_course_info(resp):
    teacher_pattern = re.compile('var teachers = \[{id:.*?,name:"(.+?)",lab:.*?}\];')
    course_info_pattern = re.compile(r"""\)","(.+?)\(.+?\)",".+?","(.+?)","01{3,}0{3,}""", re.X)
    course_time_pattern = re.compile('=(.+?)\*unitCount\+(.+?);')
    teacher_name = teacher_pattern.findall(resp.content.decode('utf-8'))
    course_info_iter = course_info_pattern.finditer(resp.content.decode('utf-8'))
    course_info = course_info_pattern.findall(resp.content.decode('utf-8'))
    course_pos = [i.start() for i in course_info_iter]
    course_info = [list(i) for i in course_info]
    course = []
    i = 0
    for i in range(len(course_pos) - 1):
        course.append([tuple_conv(i) for i in course_time_pattern.findall(resp.content.decode('utf-8'),
                                                                          course_pos[i], course_pos[i+1])])
    course.append([tuple_conv(i) for i in course_time_pattern.findall(resp.content.decode('utf-8'), course_pos[i+1])])
    result = []
    for i in range(len(course_info)):
        result.append(course_info[i] + [teacher_name[i]] + course[i])
    return result


# print the grade table on screen
def print_grade_table(resp, cat_list_str):
    n = 1
    table = prettytable.PrettyTable(['', '课程名称', '学分', '成绩'])
    for cat in get_specified_grade(resp, cat_list_str):
        for i in cat:
            table.add_row([str(n)] + i)
            n += 1
    table.align['成绩'] = 'l'
    print('\n%s类成绩表:' % cat_list_str)
    print(table)
    output_grade = grade_calc(get_specified_grade(resp, cat_list_str))
    print('%s类已修学分:%.1f' % (cat_list_str, output_grade[1]))
    print('%s类学分绩:%.4f\n' % (cat_list_str, output_grade[0]))


# print the course table on screen
def print_course_table(course_info):
    row = []
    n = 1
    table = prettytable.PrettyTable([''] + [str(i+1) for i in range(7)], hrules=prettytable.ALL)
    mat = [['' for i in range(7)] for j in range(14)]
    for i in course_info:
        for j in i[3:]:
            mat[j[1]][j[0]] = i[:3]
    for i in mat:
        row.append(str(n))
        for j in i:
            if j:
                row.append('%s\n%s@%s' % (j[0], j[2], j[1]))
            else:
                row.append(j)
        table.add_row(row)
        row = []
        n += 1
    print(table)


# main
def main():
    if test_net():
        args = docopt(__doc__)  # get program args
        test_net()
        sess = log_in(args['<username>'], args['<password>'])

        # get the grade
        if args['--grade']:
            response = sess.get(GRADE_URL)
            print_grade_table(response, args['<course_category>'])

        # get the course table
        if args['--course']:
            response = sess.get(COURSETABLE_ID_URL)
            course_data = {
                'setting.kind': 'std',
                'ids': '%s' % get_std_course_id(response)[0]
            }
            sess.post(COURSETABLE_QUERY_URL)
            response = sess.post(COURSETABLE_URL, data=course_data)
            courses = get_course_info(response)
            print_course_table(courses)

        sess.close()
    else:
        print('Failed to connect the NKU-EAMIS system!\n')


if __name__ == '__main__':
    main()

