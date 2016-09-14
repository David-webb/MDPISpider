# -*- coding: utf-8 -*-
import os
import sys
import requests
# sys.path.append("..")
# sys.path.append("../..")
from MdpiPapers.MdpiDBop import *
from MdpiPapers.spiders.SubjectMenu import SubjectmenuSpider
from MdpiPapers.LetsDownload import goDownload


def testContinue():
    td = MdpiMysql("localhost", "root", "tw2016941017", "MDPIArticleInfo")
    return td.getControlInfo()
    pass


def Inspector():
    """监控函数: 负责停止后重启"""
    count = 0
    while(testContinue()):
        os.system('python LetsDownload.py')
        print '\n第' + `count` + '次启动...'
        count += 1


def GoUpdate(SourcePath, User, Password, databaseName):
    """ 用于重启爬虫更新数据库数据 """
    # 工具准备
    sp = SubjectmenuSpider()
    gd = goDownload(SourcePath, User, Password, databaseName)
    dbOp = daliyUpdateDbOps(SourcePath, User, Password, databaseName)
    murl = 'http://www.mdpi.com/'
    response = requests.get(murl)

    # 获取新的控制表的信息
    anslist = sp.multiUseOfParse(response)
    print anslist

    # 更新控制表中总页数, 已下载页数-1, 文章总数的数据
    if dbOp.UpdateMenu(anslist) == False:
        print '更新menu失败'
        return False

    # 启动爬虫,下载新数据
    gd.startDownload()
    pass


if __name__ == '__main__':
    # 测试脚本运行: 失败(import 的路径有问题) !!!!!!
    # if len(sys.argv) < 2:
    #     print "忘记输入参数了(goupdate/inspector),请重启!"
    # elif sys.argv[1].lower() == 'goupdate':
    #     GoUpdate()
    # elif sys.argv[1].lower() == 'inspector':
    #     Inspector()

    GoUpdate("localhost", "root", "tw2016941017", "MDPIArticleInfo")
    pass