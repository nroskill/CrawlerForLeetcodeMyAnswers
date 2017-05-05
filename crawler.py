#encoding:utf-8
# By Nroskill
# 爬自己leetcode上写过的题的答案

import json
import multiprocessing
import os
import re
import requests
import sys

def handleRequests(session, url, method = 'GET', data = None):
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

def login(session):
    from config import loginInfo
    #login
    loginResult = handleRequests(session, 'https://leetcode.com/accounts/login/', 'POST', data = loginInfo).text
    if loginResult.find(r'form class="form-signin"') >= 0:
        return ''
    else:
        return re.search(r'<a href="#" class="dropdown-toggle" data-toggle="dropdown">\s*(\w*)\s*<span class="caret"></span>', loginResult).group(1)

def addToFinishedList(finished, apiRet):
    for pro in apiRet['stat_status_pairs']:
        if pro['status'] == 'ac':
            finished.append({'id': pro['stat']['question_id'], 'title': pro['stat']['question__title_slug'].encode('utf-8')})

def getLatestAnswer(info, session, searcher):
    apiRet = json.loads(handleRequests(session, 'https://leetcode.com/api/submissions/{0}/?format=json'.format(info['title'])).text)
    url = ''
    ret = {}
    for i in apiRet['submissions_dump']:
        if i['status_display'] == 'Accepted':
            ret['lang'] = i['lang'].encode('utf-8')
            ret['runtime'] = i['runtime'].encode('utf-8')
            url = i['url']
            break
    htmlText = handleRequests(session, 'https://leetcode.com' + url).text
    ret['code'] = searcher.search(htmlText).group(1).decode('unicode-escape', errors='ignore').encode('utf-8')
    return ret

def save(path, info, userName):
    from config import codeSetting
    if os.path.exists(path) == False:
        os.mkdir(path)
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
        '{6}\r\n'
        '\r\n'
        '{7}'.format(
            codeSetting[info['lang']]['prefix'],
            info['title'],
            codeSetting[info['lang']]['middle'],
            userName, 
            info['runtime'], 
            info['lang'], 
            codeSetting[info['lang']]['suffix'],
            info['code']
            )
        )

def init(session):
    from config import loginInfo
    #get csrf cookie
    result = handleRequests(session, 'https://leetcode.com/accounts/login/').text
    #init problemsType
    problemsType = re.findall(r'problemset/(.*)/">', result)
    #get csrf value
    loginInfo['csrfmiddlewaretoken'] = re.search(r"csrfmiddlewaretoken'\s*value='(.*)'", result).group(1)
    #handle main argv
    if len(sys.argv) > 1:
        loginInfo['login'] = sys.argv[1]
        loginInfo['password'] = sys.argv[2]
    return problemsType

def worker(userName, finished, cur, lock, session, processId, searcher):
    index = -1
    while True:
        with lock:
            if index != -1:
                print 'Problem ' + str(finished[index]['id']) + ' done! '
            if cur.value >= len(finished):
                break
            else:
                index = cur.value
                cur.value += 1
                print 'Process ' + str(processId) + ' fetch Problem ' + str(finished[index]['id'])
        finished[index].update(getLatestAnswer(finished[index], session, searcher))
        save(userName, finished[index], userName)

if __name__=='__main__':
    import datetime
    begin = datetime.datetime.now()

    with requests.Session() as session:
        session.keep_alive = False
        finished = []
        searcher = re.compile(r"submissionCode:\s*'(.*)',\s*editCodeUrl:\s*'")
        #init
        problemsType = init(session)      

        #login & get cookie
        userName = login(session)
        if userName != '':
            print userName + ' login success! '
        else:
            print 'Login failed! '
            exit(0)

        #init problem list
        for i in range(len(problemsType)):
            apiRet = json.loads(handleRequests(session, 'https://leetcode.com/api/problems/{0}/'.format(problemsType[i])).text)
            addToFinishedList(finished, apiRet)
        print 'Total ' + str(len(finished)) + ' problem(s). '

        if len(sys.argv) == 4:
            for index in range(len(finished)):
                if finished[index]['id'] == int(sys.argv[3]):
                    print 'Process 0 fetch Problem ' + str(finished[index]['id'])
                    finished[index].update(getLatestAnswer(finished[index], session, searcher))
                    save(userName, finished[index], userName)
                    print 'Problem ' + str(finished[index]['id']) + ' done! '
                    exit(0)

        from config import ConcurrencyCountLimit
        manager = multiprocessing.Manager()
        cur = manager.Value('i', 0)
        lock = manager.Lock()
        processId = 0
        pool = multiprocessing.Pool(processes = ConcurrencyCountLimit)
        for processId in range(ConcurrencyCountLimit):
            pool.apply_async(worker, (userName, finished, cur, lock, session, processId, searcher, ))
        pool.close()
        pool.join()
        
        print 'Job Done. '
        print 'Time ' + str(datetime.datetime.now() - begin)