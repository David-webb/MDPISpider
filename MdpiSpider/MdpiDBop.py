# -*- coding: utf-8 -*-
import MySQLdb
import traceback
import json
import datetime


class MdpiMysql():
    def __init__(self, SourcePath, User, Password, databaseName):
        self.db = MySQLdb.connect(SourcePath, User, Password, databaseName, charset='utf8')
        self.cursor = self.db.cursor()
        pass

    def CreateTable(self, TableName):
        # url_table
        sql = ''
        if TableName == 'ArticlesInfo':
            sql = """CREATE TABLE ArticlesInfo(
                Dio VARCHAR(200) PRIMARY KEY,
                mType VARCHAR(50) NOT NULL,
                Title VARCHAR(500) NOT NULL,
                Journal VARCHAR(100) NOT NULL,
                Received VARCHAR(50),
                Revised VARCHAR(50),
                Accepted VARCHAR(50),
                Published VARCHAR(50),
                Author_Addr_Institution  VARCHAR(20000)
            )default charset=utf8;
            """
            try:
                self.cursor.execute("DROP TABLE IF EXISTS " + TableName)
                self.cursor.execute(sql)
                self.db.commit()
            except:
                print '创建表格' + TableName + '失败！\n'
                self.db.rollback()


        # settings_table

        pass
    def InsertUrls(self, urlList, TableName):
        sql = ''
        if TableName == 'downloadControl':
            sql = "INSERT IGNORE INTO " + TableName + " value(%s, %s, %s, %s, %s, %s)"         # 占位符用%s没有问题, IGNORE根据ID查重
        elif TableName == 'ArticlesInfo':
            sql = "INSERT IGNORE INTO " + TableName + " value(%s, %s, %s, %s, %s, %s, %s, %s, %s)"         # 占位符用%s没有问题, IGNORE根据ID查重
            pass
        try:
            self.cursor.executemany(sql, urlList)
            self.db.commit()
        except Exception as e:
            print e
            print traceback.format_exc()
            print '插入失败！\n'
            self.db.rollback()
        pass


    def getControlInfo(self):
        sql = "select * from  downloadControl where downloadedPageNum < totalPageNum limit 1 FOR UPDATE"
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        except:
            print '获取失败，可能没有未下载数据了...'
            self.db.rollback()
            return False
        pass

    def UpdatedownloadRcd(self, subjectName, pageNum):
        try:
            sql = 'Update downloadControl set downloadedPageNum=' + str(pageNum) + ' where subjectName="' + subjectName + '"'
            # print 'update sql:',sql
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print e
            print traceback.format_exc()
            print '更新下载记录失败！停止下载，进行检查！'
            self.db.rollback()
        pass


    def __del__(self):
        self.cursor.close()
        self.db.commit()
        self.db.close()
        pass


class daliyUpdateDbOps():
    def __init__(self, SourcePath, User, Password, databaseName):
        self.db = MySQLdb.connect(SourcePath, User, Password, databaseName, charset='utf8')
        self.cursor = self.db.cursor()
        pass

    def UpdateMenu(self, menuInfoList):

            try:
                for i in menuInfoList:
                    sql = 'Update downloadControl set totalPageNum=' + str(i[2]) + ' ' \
                          + 'subjectShortNameUrl=' + i[1] + ' ' \
                          + 'downloadedPageNum = downloadedPageNum-1' + ' '\
                          + 'totalArticlesNum =' + str(i[5]) + ' ' \
                          + 'where subjectName="' + i[0] + '"'
                    # print 'update sql:',sql
                    self.cursor.execute(sql)
                    self.db.commit()
                return True
            except Exception as e:
                print e
                print traceback.format_exc()
                print '更新下载记录失败！停止下载，进行检查！'
                self.db.rollback()
                return False

if __name__ == '__main__':
    td = MdpiMysql("localhost", "root", "", "MDPIArticleInfo")
    td.CreateTable('ArticlesInfo')

    pass