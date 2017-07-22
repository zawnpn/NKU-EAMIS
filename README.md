## Introduction
A simple tool to help get information in NKU-EAMIS(NKU Education Affairs Management Information System).

## Install & Use
Use command `sudo pip3 install nkueamis` to install, then just execute `nkueamis` with some options in your terminal;

Or you can just clone this project and execute `python3 nkueamis.py` with options.(If you use this method, make sure the dependencies are satisfied!)

To upgrade this program, just execute `sudo pip3 install nkueamis --upgrade` .

## To be added
 - Elect courses

## Usage
    nkueamis -g <course_category> [-u <username> -p <password>]
    nkueamis -c [-s <semester>]
    nkueamis -c [-u <username> -p <password>]
    nkueamis -c -s <semester> -u <username> -p <password>
    nkueamis -e [-s <semester>]
    nkueamis -e [-u <username> -p <password>]
    nkueamis -e -s <semester> -u <username> -p <password>
    nkueamis --elect-course

## Arguments
    course_category      the category of courses which you want to query(only can be combination of A,B,C,D,E)
    semester             the semester you want to query, must be in '[Year]-[Year]:[Semester]' type
    username             your username in NKU-EAMIS system
    password             your password in NKU-EAMIS system

## Options
    -g                   grade query
    -c                   course query
    -e                   exam query
    -s                   semester
    -u                   username
    -p                   password
    --elect-course       elect-course
    -h, --help           guidance

## Examples
    nkueamis -g BCD
    nkueamis -g ABCDE -u your_username -p your_password
    nkueamis -c
    nkueamis -c -s 2016-2017:2
    nkueamis -e -u your_username -p your_password
    
## Author
Blog:[Wanpeng Zhang](http://www.oncemath.com)

E-mail:zawnpn@gmail.com

## Others
See more information in [http://www.oncemath.com/nku-eamis.html](http://www.oncemath.com/nku-eamis.html).

