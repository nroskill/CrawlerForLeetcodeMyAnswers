#encoding:utf-8
# By Nroskill
# 爬自己leetcode上写过的题的答案

import requests
import json
import os
import re

def configInit():
    if os.path.exists("config.py") == False:
        writeIntoFiles('config.py', 
            '#encoding:utf-8\r\n'
            'headers = {\r\n'
            '    "Host": "leetcode.com", \r\n'
            '    "Referer": "https://leetcode.com", \r\n'
            '    "Connection": "close", \r\n'
            '    "Accept": "application/json, text/javascript, */*; q=0.01", \r\n'
            '    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"\r\n'
            '}\r\n'
            'proxies = {\r\n'
            '#    "https": "http://127.0.0.1:1080"\r\n'
            '}\r\n'
            'loginInfo = {\r\n'
            '    "login": "", \r\n'
            '    "password": ""\r\n'
            '}\r\n'
            'copyright = ""'
            )
        print 'edit your config.py'
        exit(0)

def handleRequests(url, method = 'GET', data = None):
    from config import proxies
    from config import headers
    result = ''
    if method == 'GET':
        result = session.get(url, headers = headers, data = data, proxies = proxies)
    elif method == 'POST':
        result = session.post(url, headers = headers, data = data, proxies = proxies)
    else:
        return None
    return result

def writeIntoFiles(filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)

def login():
    #get csrf cookie
    from config import loginInfo
    result = handleRequests('https://leetcode.com/accounts/login/').text
    #get csrf value
    start = result.find('csrfmiddlewaretoken') + 28
    end = result.find('\'', start)
    loginInfo['csrfmiddlewaretoken'] = result[start:end]
    #login
    loginResult = handleRequests('https://leetcode.com/accounts/login/', 'POST', data = loginInfo).text
    if loginResult.find(r'form class="form-signin"') >= 0:
        return ''
    else:
        return re.search(r'<a href="#" class="dropdown-toggle" data-toggle="dropdown">\s*(\w*)\s*<span class="caret"></span>', loginResult).group(1)

def addToFinishedList(finished, apiRet):
    for pro in apiRet['stat_status_pairs']:
        if pro['status'] == 'ac':
            finished.append({'id': pro['stat']['question_id'], 'title': pro['stat']['question__title_slug']})

def getLatestAnswer(finished, index):
    apiRet = json.loads(handleRequests('https://leetcode.com/api/submissions/{0}/?format=json'.format(finished[index]['title'])).text)
    url = ''
    for i in apiRet['submissions_dump']:
        if i['status_display'] == 'Accepted':
            finished[index]['lang'] = i['lang']
            finished[index]['runtime'] = i['runtime']
            url = i['url']
            break
    htmlText = handleRequests('https://leetcode.com' + url).text
    finished[index]['code'] = re.search(r"submissionCode:\s*'(.*)',\s*editCodeUrl:\s*'", htmlText).group(1).decode('unicode-escape', errors='ignore')

def save(path, info):
    fileType = {
        'cpp': '.cpp', 
        'mysql': '.sql', 
        'java': '.java'
    }

    if os.path.exists(path) == False:
        os.mkdir(path)
    print info
    writeIntoFiles(
        '{0}/{1}.{2}{3}'.format(
            path, 
            info['id'], 
            info['title'], 
            fileType[info['lang']]
            ),
        info['code']
        )
    print 'finished writeIntoFiles {0}.{1}'.format(
            str(info['id']), 
            info['title']
        )

if __name__=='__main__':
    # default config
    configInit()

    with requests.Session() as session:
        session.keep_alive = False
        problemsType = [
            'algorithms', 
            'database', 
            'shell', 
            'draft', 
            'system-design'
        ]
        finished = []
        
        #login & get cookie
        userName = login()
        if userName != '':
            print userName + ' login success'
        else:
            print 'login failed'
            exit(0)

        #init problem list
        for i in range(len(problemsType)):
            apiRet = json.loads(handleRequests('https://leetcode.com/api/problems/{0}/'.format(problemsType[i])).text)
            addToFinishedList(finished, apiRet)
        print 'finished ' + str(len(finished)) + ' problem(s)'

        for i in range(len(finished)):
            getLatestAnswer(finished, i)
            save(userName, finished[i])
