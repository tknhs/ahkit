#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Active History of Research for K.I.T.

usage:
    ahkit new_report [--date=yyyymmdd]
    ahkit deploy [--file=filename]
    ahkit -h | --help
    ahkit --version

options:
    -h, --help          ヘルプ表示
    --version           バージョン表示
    [--date=yyyymmdd]   yyyymmdd の週初から週末までのレポートファイル作成
                        デフォルト：現在の週初から週末までのレポートファイル作成
    [--file=filename]   指定したファイルに基づいて活動記録に登録する
                        デフォルト：コミットしていないすべてのファイル
"""

from AutoRegister import AutoRegister
from docopt import docopt
from git import *
import datetime
import calendar
import sys
import os
import re


NAME = ''
ID = ''
PASS = ''

TEMPLATE = """# Weekly Report
# name: %s

activity_time: 
activity_content:
- 
- 
- 

guidance_time: 
guidance_content:
- 
- 
""" % NAME


def version():
    print '0.1'


def new_report(arg_date):
    calendar.setfirstweekday(calendar.MONDAY)
    if arg_date:
        d = datetime.datetime.strptime(arg_date, '%Y%m%d')
    else:
        d = datetime.date.today()

    if d.weekday() == calendar.SUNDAY:
        s_date = d.strftime('%Y%m%d')
        e_date = d + datetime.timedelta(6)
        e_date = e_date.strftime('%Y%m%d')
    else:
        s_date = d - datetime.timedelta(d.weekday() + 1)
        e_date = s_date + datetime.timedelta(6)
        s_date = s_date.strftime('%Y%m%d')
        e_date = e_date.strftime('%Y%m%d')

    filename = s_date + '_' + e_date + '.yaml'
    if os.path.isfile(filename):
        print 'Info: File already exists. : ' + filename
        sys.exit(0)
    f = open(filename, 'w')
    f.write(TEMPLATE)
    print 'Info: Created a file. : ' + filename


def deploy(arg_file):
    try:
        repo = Repo(os.getcwd())
        assert repo.bare == False
    except InvalidGitRepositoryError:
        print 'Error: Cannot find a git repo. \n**Hint** `git init`'
        sys.exit(0)

    index = repo.index
    if arg_file:
        # One file
        m = re.match(r'[0-9]{8}_[0-9]{8}.yaml', arg_file)
        if m is None:
            print 'Error: Filename is invalid.'
            sys.exit(0)

        # new_file and modify_file check
        if m.group(0) in repo.untracked_files or [diff for diff in repo.index.diff(None) if m.group(0) in str(diff)] != []:
            files = [m.group(0)]
            index.add(files)
            index.commit(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"))
        else:
            print 'Info: Nothing to commit.'
            sys.exit(0)
    else:
        # All files
        # new_files
        files = [f for f in repo.untracked_files if re.match(r'[0-9]{8}_[0-9]{8}.yaml', f) is not None]
        for diff in repo.index.diff(None):
            # modify_files
            m = re.search(r'[0-9]{8}_[0-9]{8}.yaml', str(diff))
            if m is None:
                print 'Info: Nothing to commit.'
                sys.exit(0)
            files.append(m.group(0))
        files = list(set(files))
        if files == []:
            print 'Info: Nothing to commit.'
            sys.exit(0)
        else:
            index.add(files)
            index.commit(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"))

    return files


def main():
    args = docopt(__doc__)
    if args['new_report']:
        new_report(args["--date"])

    elif args['deploy']:
        files = deploy(args["--file"])
        ar = AutoRegister(ID, PASS, files)
        ar.auto_register()

    elif args['--version']:
        version()
