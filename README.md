# CrawlerForLeetcodeMyAnswers

支持的、经过测试的Python版本：
* 2.7.12
* 3.6.1

使用方法：

```
python crawler.py [username password][problem_id]
```

其中`problem_id`为指定题号，如果不指定则默认爬取所有AC过的题，但不会爬取本地已经爬到过的题

**注：如果多次AC，只会爬取最新的答案，如需更新，请删除之前的版本，或使用problem_id参数强制爬取**

可以根据自己情况修改config.py, 包括

* 代理
* 登陆信息
* 并发数上限（多进程）
* header（一般不用改）
* 语言相关设置（一般不用改）

**注：会优先使用参数中的用户名和密码**

例如 只爬取题目id为100的题（需要修改config.json中的login和password）

```
python crawler.py 100
```

例如 在参数中使用用户名和密码爬取

```
python crawler.py nroskill 123456
```

也可以同时使用

```
python crawler.py nroskill 123456 100
```