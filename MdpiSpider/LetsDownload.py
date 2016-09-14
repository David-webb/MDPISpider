# -*- coding: utf-8 -*-
from MdpiPapers.MdpiDBop import MdpiMysql
from scrapy import Selector
import requests
import traceback
import socket
import json

class goDownload():
    def __init__(self, SourcePath, User, Password, databaseName, updateFlag=False):
        self.dboperator = MdpiMysql(SourcePath, User, Password, databaseName)
        self.updateFlag = updateFlag

    # 根据提供的控制信息（页码）组装URL
    def getUrl(self, subjectShortUrlName, pageNum):
        basicUrl = "http://www.mdpi.com/search?subjects=" + subjectShortUrlName + "&year_from=1996&year_to=2016&page_no=" + str(pageNum) + "&page_count=200&sort=pubdate&view=abstract"
        return basicUrl
        pass

    # 根据request返回的网页源码提取items,并插入数据库
    def getItem(self, durl, conInfo, pageNum):
        print "开始下载" + conInfo[0] + "项目的第" + str(pageNum) + "页......"
        socket.setdefaulttimeout(60.0)     # 数值是浮点型
        try:
            r = requests.get(durl)
            # with open('tmppage.txt', 'r')as rd:
            #     slect = Selector(text=rd.read())
            slect = Selector(text=r.text)
            articleItemLists = slect.xpath('//table[@class="articleItem"]')
            totalArtInfoLists = []
            for sel in articleItemLists:
                ArtInfo = {}
                JandDList = self.parseJournalAndDoi(sel)
                ArtInfo['Dio'] = JandDList[1]
                ArtInfo['mType'] = conInfo[0]
                try:
                    ArtInfo['title'] = sel.xpath('descendant::div[@class="title"]/a/text()')[0].extract()
                except:
                    # print sel.xpath('descendant::div[@class="title"]/a/text()').extract()
                    ArtInfo['title'] = '"the title is Not Given!"'
                ArtInfo['Journal'] = JandDList[0]
                timeList = self.parseTime(sel)
                ArtInfo['Received'] = timeList[0]
                ArtInfo['Revised'] = timeList[1]
                ArtInfo['Accepted'] = timeList[2]
                ArtInfo['Published'] = timeList[3]
                ArtInfo['Author_Addr_Institution'] = self.parseAffiliatioln(sel)
                totalArtInfoLists.append([ArtInfo['Dio'], ArtInfo['mType'], ArtInfo['title'], ArtInfo['Journal'], ArtInfo['Received'],
                                          ArtInfo['Revised'], ArtInfo['Accepted'], ArtInfo['Published'], ArtInfo['Author_Addr_Institution']])
                # print ArtInfo
                # break
            print len(totalArtInfoLists)
            # import pprint
            # pprint.pprint(totalArtInfoLists[0])
            self.dboperator.InsertUrls(totalArtInfoLists, 'ArticlesInfo')
            self.dboperator.UpdatedownloadRcd(conInfo[0], pageNum)
            return True
        except Exception as e:
            print e
            print traceback.format_exc()
            print "下载失败，即将重启！"
            return False
            pass
        pass

    def judgeNumStr(self, Jstr):        # 判断字符是否是数字字符
        try:
            num = int(Jstr)
            return num
        except:
            return False


    def AffiliationHasSup(self, sel):
        suplist = sel.xpath('descendant::div[@class="affiliations"]/sup/text()').extract()
        if suplist:     # 存在<sup>标签
            tmplist = [int(i) for i in suplist if self.judgeNumStr(i)]
            return len(tmplist)     # 列表不空返回长度（真），反之，返回False
        else:           # 不存在<sup>标签
            return False

    def parseAffiliatioln(self, sel):
        AuthorList = sel.xpath('descendant::div[@class="authors"]/span[@class="inlineblock"]')      # 存放作者信息的List(上标和姓名)
        strlist = sel.xpath('descendant::div[@class="affiliations"]/text()').extract()
        affiliationlist = [i.strip() for i in strlist if i.strip()]     # 保存所有地址字符串（可能有部分说明字符串）
        # print affiliationlist
        if affiliationlist:
            AuthorToAffiliationDict = {}
            lenth = self.AffiliationHasSup(sel)
            if lenth:
                for i in affiliationlist[:lenth]:
                    AuthorToAffiliationDict[i] = []
                for i in AuthorList:
                    name = i.xpath('a/text()').extract()
                    if name==[]:        # 醉了，有些文献连作者这一栏都是空的
                        print name
                        continue
                    supNum = i.xpath('sup/text()').extract()
                    if supNum:
                        supNum = supNum[0]
                        for j in [int(t) for t in supNum.strip().split(',') if self.judgeNumStr(t)]:
                            try:
                                AuthorToAffiliationDict[affiliationlist[j-1]].append(name)
                            except:
                                # print 'index: ', j, 'affiliation[0]:',affiliationlist[0]
                                # AuthorToAffiliationDict[affiliationlist[j-2]].append(name)  # 有些论文格式不规范：上标的数字最大值超过实际的单位个数
                                continue          # 这里由于上标没有对应的单位，所以就不加了,宁缺毋滥

                    else:
                        AuthorToAffiliationDict[affiliationlist[0]].append(name)
                        pass
            else:
                AuthorToAffiliationDict[affiliationlist[0]] = []
                for i in AuthorList:
                    name = i.xpath('a/text()').extract()[0]
                    AuthorToAffiliationDict[affiliationlist[0]].append(name)

            AnswerDict = json.dumps(AuthorToAffiliationDict)
            # print AnswerDict
            # print AnswerDict.decode('utf-8')
            return AnswerDict
        else:
            return 'affiliations Info Not Given!'
        pass


    def parseJournalAndDoi(self, sel):
        childList = sel.xpath('descendant::div[@class="idnt"]/child::node()')
        strtmp = ''
        count = 0
        for i in childList:
            if count % 2:
                strtmp += i.extract()
            else:
                strtmp += i.xpath('text()').extract()[0]
            count += 1
        # tmplist = [i.xpath('text()').extract()[0] for i in childList[::2]]
        # tmplist2 = [j.extract() for j in childList[1::2]]
        # for i, j in tmplist, tmplist2:
        #     strtmp += i
        #     strtmp += j
        return [i.strip() for i in strtmp.split(';')]
        pass

    def parseTime(self, sel):
        timeList = []
        tmpstr = sel.xpath('descendant::div[@class="pubdates"]/text()').extract()
        strList = tmpstr[0].split('/')
        mdict = {'Received': 'Not recorded', 'Revised': 'Not recorded', 'Accepted': 'Not recorded', 'Published': 'Not recorded'}
        for i in strList:
            j = i.split(':')
            j[0] = j[0].strip()
            if j[0] in mdict.keys():
                mdict[j[0]] = j[1]
        timeList.append(mdict['Received'].strip())
        timeList.append(mdict['Revised'].strip())
        timeList.append(mdict['Accepted'].strip())
        timeList.append(mdict['Published'].strip())
        return timeList
        pass

    # 下载过程的控制函数
    def startDownload(self):
        # (subjectName, subjectShortUrlName, totalPageNum, downloadedPageNum, perPageNum, totalArticlesNum)
        while(self.dboperator.getControlInfo()):
            conInfo = self.dboperator.getControlInfo()
            pageNum = 1
            if conInfo[3] > 0:      # downloadedPageNum 初始化是-1
                pageNum = conInfo[3] + 1
            # print 'pageNum', `pageNum`, str(pageNum)
            # 说明:由于MDPI网站的时间排序是将最新的文章放在最前面,所以,在构造url的时候,每次下载的页码要计算一下
            if self.updateFlag == True:
                dUrl = self.getUrl(conInfo[1], conInfo[2]-conInfo[3])
            else:
                dUrl = self.getUrl(conInfo[1], pageNum)
            if(self.getItem(dUrl, conInfo, pageNum)==False):
                break
        pass


if __name__ == '__main__':
    tmp = goDownload("localhost", "root", "", "MDPIArticleInfo")
    tmp.startDownload()
