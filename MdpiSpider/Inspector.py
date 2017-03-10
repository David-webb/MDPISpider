# -*- coding: utf-8 -*-
import os
import sys
import requests
import getpass
# sys.path.append("..")
# sys.path.append("../..")
from MdpiDBop import *
from SubjectMenu import SubjectmenuSpider
from LetsDownload import goDownload


def testContinue(SourcePath, User, Password, databaseName):
    td = MdpiMysql(SourcePath, User, Password, databaseName)
    return td.getControlInfo()
    pass


def Inspector(SourcePath, User, Password, databaseName):
    """监控函数: 负责停止后重启"""
    count = 0
    while(testContinue()):
        os.system('python LetsDownload.py')
        print '\n第' + `count` + '次启动...'
        count += 1


def GoUpdate(SourcePath, User, Password, databaseName, operations=[1, 2]):
    """ 用于重启爬虫更新数据库数据 """
    # 工具准备
    sp = SubjectmenuSpider()
    gd = goDownload(SourcePath, User, Password, databaseName, updateFlag=True)
    dbOp = daliyUpdateDbOps(SourcePath, User, Password, databaseName)
    murl = 'http://www.mdpi.com/'
    response = requests.get(murl)

    # 更新控制表
    if 1 in operations:
        # 获取新的控制表的信息
        anslist = sp.multiUseOfParse(response)
        print anslist

        # 更新控制表中总页数, 已下载页数-1, 文章总数的数据
        if dbOp.UpdateMenu(anslist) == False:
            print '更新menu失败'
            return False

    # 启动爬虫,下载新数据
    if 2 in operations:
        print "启动！"
        gd.startDownload()
    pass


if __name__ == '__main__':
    # SourcePath = "localhost"
    # databaseName = "MDPIArticleInfo"
    userName = 'root'
    psw = 'tw2016941017'
    # userName = raw_input("数据库用户名:")
    # psw = getpass.getpass("密码:")
    # 测试脚本运行: 失败(import 的路径有问题) !!!!!!
    # if len(sys.argv) < 2:
    #     print "忘记输入参数了(goupdate/inspector),请重启!"
    # elif sys.argv[1].lower() == 'goupdate':
    #     GoUpdate(SourcePath, User, Password, databaseName)
    # elif sys.argv[1].lower() == 'inspector':
    #     Inspector(SourcePath, User, Password, databaseName)

    GoUpdate("localhost", userName, psw, "MDPIArticleInfo", [1, 2])
    pass
