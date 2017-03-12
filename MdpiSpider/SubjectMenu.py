# -*- coding: utf-8 -*-
import scrapy
from MdpiDBop import MdpiMysql
import requests
from scrapy import Selector
import json
import time
# from MdpiPapers.items import subjectItem


'''
    功能： 用来创建“下载控制表”, 并从网页获取信息初始化控制表
'''
class SubjectmenuSpider(scrapy.Spider):
    name = "SubjectMenu"
    allowed_domains = ["mdpi.com"]
    start_urls = (
        'http://www.mdpi.com/',
    )

    def __init__(self, SourcePath, User, Password, databaseName):
        super(SubjectmenuSpider, self).__init__()
        self.dbop = MdpiMysql(SourcePath, User, Password, databaseName)

    def getTotalArticlesNum(self, text):
        response = Selector(text=text)
        try:
            return response.xpath('//div[@id="maincol"]/strong[1]/text()').extract()[0]
        except Exception as e:
            print "从网页获取文章总数失败...."
            return False
        pass

    def multiUseOfParse(self):
        """
            功能: 更新MDPI爬虫控制表，用于MDPI网站数据的更新
            更新时间: 2017年3月10日
            说明:
                1.MDPI网站的改变
                  首先主页改变了，subject列表信息不能再从网站主页获取了，需要点击动态加载；其次网站文章列表的代码结构有所改变，
                原先的提取文章信息提取规则不再适用
                2.应对措施
                (1) 控制信息: 在已有的控制表信息基础上,综合考虑最新的MDPI网站结构,只需要获取每个subject Type 对应的文章总数(totalArticlesNum)
                            然后计算出totalpageNum（每页200篇文章），　但是要注意文章列表获取时页码的使用需要计算（根据文章按照日期的
                            升序或降序来决定计算方式）
                (2) 文章提取规则：重新编写xpath即可
        """
        basicUrl = "http://www.mdpi.com/search?subjects=%s&year_from=1996&year_to=2017&page_count=200&sort=pubdate&view=abstract"
        mlist = self.dbop.getsubjectShortNameUrlList()
        anslist = []
        if mlist == False:
            print "更新控制列表：获取旧控制列表信息失败, 退出更新....."
            return False
        else:
            print "更新控制列表：获取旧控制列表信息成功..."

        for item in mlist:
            item = list(item)
            murl = basicUrl % item[1]
            res = requests.get(murl)
            totalArticlesnum = int(self.getTotalArticlesNum(res.text))
            totalPageNum = totalArticlesnum/200 + (1 if (totalArticlesnum % 200) > 0 else 0)
            item[5] = totalArticlesnum
            item[2] = totalPageNum
            anslist.append(item)
            print "提取%s主页信息成功......" % item[0]
            time.sleep(5)
        return anslist

    def multiUseOfParse_old(self, response):
        """  *****************************　失效 **************************************
            功能: 这里为了代码能够在后期更新的时候重用,故单独成函数
            说明: 这个是旧版本的更新爬虫控制表的程序，2017年3月10日之前，MDPI网站结构更新，这个程序不再适用
        """
        response = Selector(text=response.text)
        mlist = response.xpath('//div[@class="col-left"]/div[@class="box"][1]/nav[3]//li')
        basicUrl = 'http://www.mdpi.com/search?sort=pubdate&page_count=200&subjects='
        anslist = []
        count = 0
        for sel in mlist:
            print "更新菜单第" + str(count) + "项目......"
            count += 1
            tmpdict = {}
            tmpdict['subjectName'] = sel.xpath('a/text()')[0].extract()     # subjectName
            tmpdict['subjectShortNameUrl'] = sel.xpath('a/@href')[0].extract().split('/')[-1]
            tmpdict['firstPage'] = basicUrl + tmpdict['subjectShortNameUrl']
            print tmpdict['firstPage']
            r = requests.get(tmpdict['firstPage'])
            res = Selector(text=r.text)
            print '获得第一页'
            tmpstr = res.xpath('//div[@id="maincol"]/table/tr[1]//tr/td[1]/text()').extract()[1]
            totalArticlesnum = int(tmpstr.split('\n')[1].replace(' ', ''))
            totalPageNum = totalArticlesnum/200 + (1 if (totalArticlesnum % 200) > 0 else 0)
            anslist.append([tmpdict['subjectName'], tmpdict['subjectShortNameUrl'], totalPageNum, -1, 200, totalArticlesnum])
        return anslist

    def parse(self, response):
        anslist = self.multiUseOfParse(response)
        # print anslist
        with open('tmppage1.txt', 'w') as wr:
            wr.write(json.dumps(anslist))
        pass


if __name__ == "__main__":

    # *********************downloadControl表格数据的收集*********************
    # db = MdpiMysql("localhost", "root", "", "MDPIArticleInfo")
    # with open('../../tmppage.txt', 'r') as rd:
    #         db.InsertUrls(json.loads(rd.read()),'downloadControl')

    # *********************创建ArticlesInfo表格:存储具体的文章信息************
    # db = MdpiMysql("localhost", "root", "", "MDPIArticleInfo")
    # db.CreateTable('ArticlesInfo')

    # *********************下载控制信息获取测试*******************************
    # db = MdpiMysql("localhost", "root", "", "MDPIArticleInfo")
    # print db.getControlInfo()
    # 测试结果：
    #     每次得到的记录以元组形式呈现，例如：('Biology & Life Sciences', 'bio-life', 108L, -1L, 200L, 21590L)


    # *********************更新下载列表**************************************
    tmpobj = SubjectmenuSpider("localhost", "root", "", "MDPIArticleInfo")
    ## --------测试获取文章总数函-------------
    with open('tmppage1.txt', 'r') as rd:
        tmptext = rd.read()
    tmpobj.getTotalArticlesNum(tmptext)

    pass
