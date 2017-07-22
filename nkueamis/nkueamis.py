#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2017-07-01 11:03
# @Author  : Wanpeng Zhang
# @Site    : http://www.oncemath.com
# @File    : nkueamis.py
# @Project : NKU-EAMIS

"""
Usage:
    nkueamis -g <course_category> [-u <username> -p <password>]
    nkueamis -c [-s <semester>]
    nkueamis -c [-u <username> -p <password>]
    nkueamis -c -s <semester> -u <username> -p <password>
    nkueamis -e [-s <semester>]
    nkueamis -e [-u <username> -p <password>]
    nkueamis -e -s <semester> -u <username> -p <password>
    nkueamis --elect-course

A simple tool to help get information in NKU-EAMIS(NKU Education Affairs Management Information System).

Arguments:
    course_category      the category of courses which you want to query(only can be combination of A,B,C,D,E)
    semester             the semester you want to query, must be in '[Year]-[Year]:[Semester]' type
    username             your username in NKU-EAMIS system
    password             your password in NKU-EAMIS system

Options:
    -g                   grade query
    -c                   course query
    -e                   exam query
    -s                   semester
    -u                   username
    -p                   password
    --elect-course       elect course
    -h, --help           guidance

Examples:
    nkueamis -g BCD
    nkueamis -g ABCDE -u your_username -p your_password
    nkueamis -c
    nkueamis -c -s 2016-2017:2
    nkueamis -e -u your_username -p your_password

"""

from docopt import docopt
import re
import os
import requests
from bs4 import BeautifulSoup
import prettytable
import getpass
import _pickle

HOME_URL = 'http://eamis.nankai.edu.cn'
LOGIN_URL = HOME_URL + '/eams/login.action'
STD_DETAIL_BASIC_URL = HOME_URL + '/eams/stdDetail.action'
STD_DETAIL_URL = HOME_URL + '/eams/stdDetail!innerIndex.action'
GRADE_URL = HOME_URL + '/eams/myPlanCompl!innerIndex.action'
COURSETABLE_QUERY_URL = HOME_URL + '/eams/dataQuery.action'
COURSETABLE_CLASS_URL = HOME_URL + '/eams/courseTableForStd.action'
COURSETABLE_ID_URL = HOME_URL + '/eams/courseTableForStd!innerIndex.action'
COURSETABLE_URL = HOME_URL + '/eams/courseTableForStd!courseTable.action'
EXAM_ID_URL = HOME_URL + '/eams/stdExam.action'
EXAM_URL = HOME_URL + '/eams/stdExam!examTable.action'
ELECT_URL = HOME_URL + '/eams/stdElectCourse!innerIndex.action'
ELECT_PAGE_URL = HOME_URL + '/eams/stdElectCourse!defaultPage.action'
ELECT_DATA_URL = HOME_URL + '/eams/stdElectCourse!data.action'
ELECT_POST_URL = HOME_URL + '/eams/stdElectCourse!batchOperator.action'
COURSE_CAT = ['校公共必修课', '院系公共必修课', '专业必修课', '专业选修课', '任选课']


# test the network
def test_net():
    conn = requests.get(LOGIN_URL)
    response_status = conn.status_code
    if response_status == '200':
        return False
    else:
        return True


# login to the system
def log_in(username, password):
    login_data = {
        'username': username,
        'password': password
    }
    s = requests.session()
    s.post(LOGIN_URL, data=login_data)
    return s


# find student's detail
def get_std_detail(content):
    pattern = re.compile(
        '姓名：</td>.*?<td>(.+?)</td>.*?院系：</td>.*?<td>(.+?)</td>.*?专业：</td>.*?<td>(.+?)</td>', re.S)
    detail = pattern.findall(content)
    return detail


# print detail of student on screen
def print_std_detail(sess):
    resp = sess.get(STD_DETAIL_URL + '?projectId=1')
    result = get_std_detail(resp.content.decode())
    if result:
        std_detail = result[0]
        print('\n姓名:%s\n院系:%s\n专业:%s\n' % (std_detail[0], std_detail[1], std_detail[2]))


# find the category of course
def find_course_cat(i, content):
    pattern = re.compile(COURSE_CAT[i-1])
    result = pattern.findall(content)
    return result


# convert str tuple into num tuple
def tuple_conv(strtuple):
    inttuple = []
    for i in strtuple:
        inttuple.append(int(i))
    return tuple(inttuple)


# replace some irregular words
def replace_some_word(text):
    replace_origin = ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ']
    replace_target = ['I', 'II', 'III', 'IV']
    for i in range(4):
        text = text.replace(replace_origin[i], replace_target[i])
    return text


# find the information of semester
def get_semester_info(data):
    pattern = re.compile('{id:(.+?),schoolYear:"(.+?)",name:"(.+?)"}', re.S)
    result = pattern.findall(data)
    return result


# determine the semester_id based on the <semester> arg
def determine_semester_id(sess, semester):
    semester = semester.split(':')
    semester_data = {'dataType': 'semesterCalendar'}
    resp = sess.post(COURSETABLE_QUERY_URL, data=semester_data)
    semester_info = get_semester_info(resp.content.decode())
    for i in semester_info:
        if list(i)[1:] == semester:
            semester_id = i[0]
            return semester_id
    print('Failed to find your semester, please make sure that you\'ve correctly inputed!')
    exit()


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
    cat_list_num = [ord(i)-65 for i in cat_list_str]
    soup = BeautifulSoup(resp.content.decode(), 'html.parser')
    for i in cat_list_num:
        result.append(get_grade_info(i+1, soup('tr')))
    return result


# calculate the avg and sum of grade
def grade_calc(table):
    gradesum = 0
    scoresum = 0
    for cat in table:
        for i in cat:
            try:
                if i[2] and i[2] != '--':
                    gradesum += float(i[1])*float(i[2].split(' ')[0])
                    scoresum += float(i[1])
            except ValueError:
                continue
    if scoresum:
        avg = gradesum/scoresum
    else:
        avg = 0
    return avg, scoresum


# get the necessary id to post data for course table
def get_std_course_id(resp):
    std_id_pattern = \
        re.compile('bg\.form\.addInput\(form,"ids","(.+?)"\);')
    std_id = std_id_pattern.findall(resp.content.decode())
    return std_id


# get information of courses
def get_course_info(resp):
    teacher_pattern = re.compile('var teachers = \[{id:.*?,name:"(.+?)",lab:.*?}\];')
    course_info_pattern = re.compile('\)","(.+?)\(.+?\)",".*?","(.*?)","0*1*0*"')
    course_time_pattern = re.compile('=(.+?)\*unitCount\+(.+?);')
    teacher_name = teacher_pattern.findall(resp.content.decode())
    course_info_iter = course_info_pattern.finditer(resp.content.decode())
    # test = course_info_pattern.findall(resp.content.decode())
    course_info = course_info_pattern.findall(resp.content.decode())
    course_pos = [i.start() for i in course_info_iter]
    course_info = [list(i) for i in course_info]
    course = []
    i = 0
    if course_pos:
        for i in range(len(course_pos) - 1):
            course.append([tuple_conv(i) for i in course_time_pattern.findall(resp.content.decode(),
                                                                              course_pos[i], course_pos[i+1])])
        course.append([tuple_conv(i) for i in course_time_pattern.findall(resp.content.decode(), course_pos[i+1])])
    result = []
    for i in range(len(course_info)):
        result.append(course_info[i] + [teacher_name[i]] + course[i])
    return result


# print the grade table on screen
def print_grade_table(resp, cat_list_str):
    cat_list_str_list = [i for i in cat_list_str.upper() if ord(i) in range(65, 70)]
    cat_list_str_list = list(set(cat_list_str_list))
    cat_list_str_list.sort()
    cat_list_str = ''.join(cat_list_str_list)
    n = 1
    table = prettytable.PrettyTable(['', '课程名称', '学分', '成绩'])
    grade_table = get_specified_grade(resp, cat_list_str)
    flag = False
    for i in grade_table:
        if i:
            flag = True
            break
    if flag:
        for cat in grade_table:
            for i in cat:
                table.add_row([str(n)] + i)
                n += 1
        table.align['成绩'] = 'l'
        print('\n%s类成绩表:' % cat_list_str)
        print(table)
        output_grade = grade_calc(get_specified_grade(resp, cat_list_str))
        print('%s类已修学分:%.1f' % (cat_list_str, output_grade[1]))
        print('%s类学分绩:%.4f\n' % (cat_list_str, output_grade[0]))
    else:
        print('Failed to get your grades, please check your username and password!')


# struct course data to help make course table
def struct_course_data(sess, project_id, semester_id=None):
    project_id = str(project_id)
    sess.get(COURSETABLE_CLASS_URL + '?projectId=%s' % project_id)
    response = sess.get(COURSETABLE_ID_URL + '?projectId=%s' % project_id)
    if not semester_id:
        try:
            semester_id = re.findall('semester\.id=(.+?);', response.headers['Set-Cookie'])[0]
        except KeyError:
            print('Failed to get your courses, please check your username and password!')
            exit()
    result = get_std_course_id(response)
    if not result:
        print('Sorry, something went wrong, please close and try again!')
    else:
        course_ids = result[0]
        course_data = {
            'setting.kind': 'std',
            'semester.id': semester_id,
            'ids': course_ids
        }
        return course_data


# struct the course table, be ready for printing
def struct_course_table(course_info):
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
                row.append('%s\n%s@%s' % (replace_some_word(j[0]), j[2], j[1]))
            else:
                row.append(j)
        table.add_row(row)
        row = []
        n += 1
    return table


# print the course table on screen
def print_course_table(sess, semester_id=None):
    course_data1 = struct_course_data(sess, '1', semester_id)
    courses1 = get_course_info(sess.post(COURSETABLE_URL, data=course_data1))
    sess.get(HOME_URL + '/eams/home.action')
    course_data2 = struct_course_data(sess, '2', semester_id)
    courses2 = get_course_info(sess.post(COURSETABLE_URL, data=course_data2))
    courses = struct_course_table(courses1 + courses2)
    print('课程表:')
    print(courses)


# get the exam id
def get_exam_id(sess, semester_id):
    headers = {'Cookie': 'JSESSIONID=%s; semester.id=%s' % (sess.cookies.items()[0][1], semester_id)}
    response = requests.get(EXAM_ID_URL, headers=headers)
    pattern = re.compile('\'/eams/stdExam!examTable\.action\?examBatch\.id=(.+?)\'')
    exam_id = pattern.findall(response.content.decode())
    if exam_id:
        return exam_id[0]
    else:
        print('Sorry, there are not any exam arrangement now '
              '(or for the semester you just typed in).\nYou may try another semester.\n')
        exit()


# print the exam table on screen
def print_exam_table(sess, semester_id=None):
    if not semester_id:
        response = sess.get(EXAM_ID_URL)
        try:
            semester_id =re.findall('semester\.id=(.+?);', response.headers['Set-Cookie'])[0]
        except KeyError:
            print('Failed to get your exams, please check your username and password!')
    response = sess.get(EXAM_URL + '?examBatch.id=%s' % get_exam_id(sess, semester_id))
    text = response.content.decode()
    text = re.sub('<font color="BBC4C3">exam.*?noArrange</font>', '><', text)
    pattern = re.compile('<td>\d{4}</td><td>(.*?)</td><td>.*?</td>.*?<td>>*'
                         '(.*?)<*</td>.*?<td>>*(.*?)<*</td>.*?<td>.*?>(.*?)<.*?</td>.*?<td>正常</td>', re.S)
    exam_info = pattern.findall(text)
    table = prettytable.PrettyTable(['', '课程名称', '考试日期', '考试时间', '考试地点'])
    n = 1
    for row in exam_info:
        row = list(row)
        row[0] = replace_some_word(row[0])
        table.add_row([str(n)] + list(row))
        n += 1
    print('考试安排:')
    print(table)


# get elect url-id to open elect page
def get_elect_urlid(sess):
    response = sess.get(ELECT_URL + '?projectId=1')
    pattern = re.compile('/eams/stdElectCourse!defaultPage\.action\?electionProfile\.id=(\d+)')
    url_ids = pattern.findall(response.content.decode())
    if url_ids:
        return url_ids
    else:
        print('Failed to find the url to elect course, please check that if the system is open!')
        exit()


# get the semester-id for electing course
def get_elect_semester_id(sess):
    response = sess.get(ELECT_PAGE_URL + '?electionProfile.id=%s' % get_elect_urlid(sess)[0])
    pattern = re.compile('&semesterId=(\d+)')
    elect_semester_id = pattern.findall(response.content.decode())
    return elect_semester_id[0]


# get the id of elected course
def get_elected_course_id(sess):
    response = sess.get(ELECT_PAGE_URL + '?electionProfile.id=%s' % get_elect_urlid(sess)[0])
    pattern = re.compile('electedIds\["l(\d+)"\] = true;')
    elected = pattern.findall(response.content.decode())
    return elected


# tool for converting no to id
def course_no2id(sess, course_no):
    data = get_course_data(sess)
    for i in data:
        if i[1] == course_no:
            course_id = i[0]
            return course_id
    print('Failed to elect your course, please make sure you\'re able to elect this course!')
    exit()


# print the elected courses
def show_elected_courses(sess):
    data = get_course_data(sess)
    print('\n当前已选课程:\n')
    for i in get_elected_course_id(sess):
        for j in data:
            if j[0] == i:
                print(j[1], j[2])


# get information of electable courses
def get_course_data(sess):
    if os.path.isfile('elect_data'):
        with open('elect_data', 'rb') as f:
            data = _pickle.load(f)
    else:
        url_ids = get_elect_urlid(sess)
        sess.get(ELECT_PAGE_URL + '?electionProfile.id=%s' % url_ids[0])
        response = sess.get(ELECT_DATA_URL + '?profileId=%s' % url_ids[0])
        pattern = re.compile('id:(\d+),no:\'(\d+)\',name:\'(.*?)\',.*?teachers:\'(.*?)\'.*?rooms:\'(.*?)\'', re.S)
        data = pattern.findall(response.content.decode())
        with open('elect_data', 'wb') as f:
            _pickle.dump(data, f)
    return data


# post data to elect course
def elect_course(sess, course_id, course_status):
    sess.get(ELECT_URL + '?projectId=1')
    sess.get(ELECT_PAGE_URL + '?electionProfile.id=121')
    data = {'operator0': '%s:%s' % (course_id, course_status)}
    url_ids = get_elect_urlid(sess)
    response = sess.post(ELECT_POST_URL + '?profileId=%s' % url_ids[0], data=data)
    pattern = re.compile('<div.*?>(.+?\[\d+\].+?)</br>.*?</div>', re.S)
    result = pattern.findall(response.content.decode())
    if result:
        print(result[0].strip())
        if re.findall('成功|已经选过|冲突', result[0].strip()):
            result.append('1')
    else:
        print('本次操作失败，请务必确保是正确操作(如不要退选不存在的课程等)！')
        result.append('0')
    return result


# elect course
def elect_course_interact(sess):
    show_elected_courses(sess)
    course_no = input('Input course ID (use sapce to separate):').split(' ')
    course_status = input('input  option ([y]:elect course / [n]:drop course):')

    course_id = [course_no2id(sess, i) for i in course_no]
    if course_status.lower() == 'y':
        cycle_num = input('input the cycles to elect course:')
        if cycle_num == 'always':
            print('\n已开启无限刷课模式(刷到自动结束)，如需提前终止请按Ctrl+C\n' + '='*60)
            while course_id:
                for j in course_id:
                    result = elect_course(sess, j, 'true')
                    if result[-1] == '1':
                        course_id.remove(j)
        else:
            print('\n开始选课\n' + '=' * 60)
            for i in range(int(cycle_num)):
                for j in course_id:
                    result = elect_course(sess, j, 'true')
                    if result[-1] == '1':
                        course_id.remove(j)
        print('=' * 60 + '\nFinish!')
    elif course_status.lower() == 'n':
        for i in course_id:
            elect_course(sess, i, 'false')
    else:
        print('Please input correct option!')


# main
def main():
    if test_net():
        args = docopt(__doc__)  # get program args
        if args['<username>'] and args['<password>']:
            sess = log_in(args['<username>'], args['<password>'])
        else:
            username = input('Input your Student ID:')
            password = getpass.getpass('Input your password:')
            sess = log_in(username, password)
        print('='*80)
        print_std_detail(sess)
        semester_id = None
        if args['<semester>']:
            semester_id = determine_semester_id(sess, args['<semester>'])

        # get the grade
        if args['-g']:
            response = sess.get(GRADE_URL)
            print_grade_table(response, args['<course_category>'])

        # get the course table
        if args['-c']:
            print_course_table(sess, semester_id)

        # get the exams
        if args['-e']:
            print_exam_table(sess, semester_id)

        # elect course
        if args['--elect-course']:
            elect_course_interact(sess)

        sess.close()
        if os.path.isfile('elect_data'):
            os.remove('elect_data')
    else:
        print('Failed to connect the NKU-EAMIS system!\n')

if __name__ == '__main__':
    main()

