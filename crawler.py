#encoding:utf-8
# By Nroskill
# 爬自己leetcode上写过的题的答案

import requests
import json
import os
import sys
import re

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
    from config import loginInfo
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

def save(path, info, userName):
    from config import codeSetting
    if os.path.exists(path) == False:
        os.mkdir(path)
    from config import copyright
    if copyright != "":
        copyright += '\r\n'
    writeIntoFiles(
        '{0}/{1}.{2}{3}'.format(
            path, 
            info['id'], 
            info['title'], 
            codeSetting[info['lang']]['extensionname']
            ),
        '{0}\r\n'
        '{2}https://leetcode.com/problems/{1}/\r\n'
        '{2}By {3}\r\n'
        '{2}runtime {4}\r\n'
        '{2}language {5}\r\n'
        '{2}{6}'
        '{7}\r\n'
        '\r\n'
        '{8}'.format(
            codeSetting[info['lang']]['prefix'],
            info['title'],
            codeSetting[info['lang']]['middle'],
            userName, 
            info['runtime'], 
            info['lang'],
            copyright
            codeSetting[info['lang']]['suffix'],
            info['code']
            )
        )
    print 'finished writeIntoFiles {0}.{1}'.format(
            info['id'], 
            info['title']
        )

def init():
    from config import loginInfo
    #get csrf cookie
    result = handleRequests('https://leetcode.com/accounts/login/').text
    #init problemsType
    problemsType = re.findall(r'problemset/(.*)/">', result)
    #get csrf value
    loginInfo['csrfmiddlewaretoken'] = re.search(r"csrfmiddlewaretoken'\s*value='(.*)'", result).group(1)
    #handle main argv
    if len(sys.argv) > 1:
        loginInfo['login'] = sys.argv[1]
        loginInfo['password'] = sys.argv[2]
    return problemsType

if __name__=='__main__':

    with requests.Session() as session:
        session.keep_alive = False
        finished = []

        #init
        problemsType = init()      

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
            save(userName, finished[i], userName)
