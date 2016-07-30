# 爬虫：MDPI(Open Access Journals Platform)

## 爬虫技术：
> requests + Xpath + mysql + socket（监控脚本）

## 概要
> 这个项目是爬取MDPI这个期刊网站的所有文章信息，主要是要获取作者信息和文章的投稿发表时间，
> 用来研究作者发表文章的时间的规律（与节气、作者单位、地点的关系）

## 功能设计：
1. 控制表：实现对下载进程的控制（提供组装url必须的信息，各类型文章的下载进度信息）
    * 每次从控制表获取一条记录，用来组装url，该url就是当前需要下载的页面的url
	* 控制表的创建和初始化由SubjectMenu.py完成
2. 文章信息表，保存每篇文章的信息
	* 从当前页面中提取出文章信息，并存入数据库
	* 文章信息的提取保存由LetsDownload.py完成
3. 监控脚本：实现超时重启	
	* 在下载模块中使用socket.setdefaulttimeout(60.0) 设置全局超时，当爬虫主程序因请求超时（或者爬取异常）退出时，监控脚本将会重启该程序
	* 然而，网站文章信息全部爬取完也会导致程序退出，因此，需要增加对控制表的判断，看是否真的没有需要爬取的页面了，再决定是否重启
	* 监控脚本：Inspector.py
4. 数据库支持
	* mysql数据支持下载控制，数据保存
	* 数据库的相关操作由MdpiDBop.py完成，直接调用即可

## 结构设计
1. 存储
+ 控制表
结构如下表,其中,subjectShortNameUrl 是构建URL所需的参数

      +---------------------+--------------+------+-----+---------+-------+
      | Field               | Type         | Null | Key | Default | Extra |
      +---------------------+--------------+------+-----+---------+-------+
      | subjectName         | varchar(100) | NO   | PRI | NULL    |       |
      | subjectShortNameUrl | varchar(100) | NO   |     | NULL    |       |
      | totalPageNum        | int(11)      | NO   |     | NULL    |       |
      | downloadedPageNum   | int(11)      | YES  |     | NULL    |       |
      | perPageNum          | int(11)      | YES  |     | 200     |       |
      | totalArticlesNum    | int(11)      | NO   |     | NULL    |       |
      +---------------------+--------------+------+-----+---------+-------+

+ 文章信息表

      +---------------------+--------------+------+-----+---------+-------+
      | Field               | Type         | Null | Key | Default | Extra |
      +---------------------+--------------+------+-----+---------+-------+
      | subjectName         | varchar(100) | NO   | PRI | NULL    |       |
      | subjectShortNameUrl | varchar(100) | NO   |     | NULL    |       |
      | totalPageNum        | int(11)      | NO   |     | NULL    |       |
      | downloadedPageNum   | int(11)      | YES  |     | NULL    |       |
      | perPageNum          | int(11)      | YES  |     | 200     |       |
      | totalArticlesNum    | int(11)      | NO   |     | NULL    |       |
      +---------------------+--------------+------+-----+---------+-------+

## 程序流程
1. SubjectMenu.py 实现控制表的创建和初始化
2. LetsDownload.py 实现控制表控制下的文章信息爬取和存储
3. Inspector.py 处理异常退出的和超时，实现重启
4. MdpiDBop.py 实现数据库支持
