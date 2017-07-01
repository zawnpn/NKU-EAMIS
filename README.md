## Introduction
A simple tool to help get information in NKU-EAMIS(NKU Education Affairs Management Information System).

## Install & Use
Use command `sudo pip3 install nkueamis` to install, then just execute `nkueamis` with some options in your terminal;

Or you can just clone this project and execute `python3 eamis.py` with options.(If you use this method, make sure the dependencies are satisfied!)

To upgrade this program, just execute `sudo pip3 install nkueamis --upgrade` .

## To be added
 - Elect courses

## Usage
    nkueamis (-g | --grade) <course_category> [-u <username> -p <password>]
    nkueamis (-c | --course) [-u <username> -p <password>]

## Arguments
    course_category      the category of courses which you want to query(only can be combination of A,B,C,D,E)
    username             your username in NKU-EAMIS system
    password             your password in NKU-EAMIS system

## Options
    -g, --grade          grade query
    -c, --course         course query
    -u                   username
    -p                   password
    -h, --help           guidance

## Examples
    nkueamis -c
    nkueamis -g BCD
    nkueamis -g BCD -u your_username -p your_password
    
## Author
Blog:[Wanpeng Zhang](http://www.oncemath.com)

E-mail:zawnpn@gmail.com
