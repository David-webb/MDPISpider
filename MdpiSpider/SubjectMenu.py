# -*- coding: utf-8 -*-
import scrapy
from MdpiPapers.MdpiDBop import MdpiMysql
import requests
from scrapy import Selector
import json
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

    def multiUseOfParse(self, response):
        """ 这里为了代码能够在后期更新的时候重用,故单独成函数 """
        response = Selector(text=response.text)
        mlist = response.xpath('//div[@class="col-left"]/div[@class="box"][1]/nav[3]//li')
        basicUrl = 'http://www.mdpi.com/search?sort=pubdate&page_count=200&subjects='
        anslist = []
        count = 0
        for sel in mlist:
            print count
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
        print anslist
        with open('tmppage.txt', 'w') as wr:
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
    pass
