import requests
import re
import sys
import time
import datetime

import hashlib

LOGIN_URL = 'http://harun.net/login'
clear = lambda : print("\033[H\033[J")

def isLoggedIn():
    getPage = requests.get(LOGIN_URL)
    return 'You are logged in' in getPage.text


def getPasswordSalt(htmlPage):
    for line in htmlPage.split('\n'):
        if "hexMD5" in line:
            m = re.findall('\((.+)\)', line)[0].split(' + ')
    
            # remove quote
            for i, mac in enumerate(m):
                m[i] = mac[1:-1]

            return [m[0], m[-1]]
    
    return []


def encodeStr(str):
    return str.encode('utf-8')

def getHtml(mockOn=False):
    if(mockOn):
        return open('harundotnet.html', 'r', encoding='utf-8').read()

    return requests.get(LOGIN_URL).text

def getParsedPassword(password):
    pageHtml = getHtml()

    [saltFirst, saltSecond] = getPasswordSalt(pageHtml)

    combineStr = eval('u\'' + "{}{}{}".format(saltFirst, password, saltSecond) + '\'')

    eCSTR = combineStr.encode('latin1')


    m = hashlib.new('md5')
    m.update(eCSTR)
    return m.hexdigest()

def postLogin(username, password):
    payload = {}
    payload['username'] = username
    payload['password'] = password
    response = requests.post(LOGIN_URL, data=payload)
    # print(response.text)
    return response

def appendLog(item, arr):
    new_arr = arr[1:5]
    new_arr.append(item)
    return new_arr

def main():
    # line = "document.sendin.password.value = hexMD5('\117' + document.login.password.value + '\151\167\120\133\215\266\351\041\263\072\272\256\235\033\235\024');"
    counter = 0
    log = []
    while True:
        clear()
        row = {}
        row["id"] = len(log) + 1
        row["time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("Checking status...")
        try:
            if(not isLoggedIn()):
                clear()
                print("[SIGNED OUT]")
                try:
                    print("[SIGNING IN] Parsing the password...")
                    parsePassword = sys.argv[2]
                    try:
                        # parse the password if required
                        parsePassword = getParsedPassword(sys.argv[2])
                    except Exception as e:
                        pass
                    print("[SIGNING IN] Submitting the account...")
                    postLogin(sys.argv[1], parsePassword)
                    print("[SIGNED IN] Success")
                    row["status"] = "SUCCESS"
                except Exception as err:
                    print("[ERROR] there is a problem parsing the password. Error: {}".format(err))
                    row["status"] = "FAILED [Invalid Password]"
                log = appendLog(row, log)
            else:
                if(counter % 2 == 0):
                    print("[SIGNED IN] Live")
                else:
                    print("[---------] Live")
        except Exception as err:
            row["status"] = "FAILED [Connection Error]"
            print("[ERROR] there is a problem with internet connection. Error: {}".format(err))
            log = appendLog(row, log)
        
        print("\n\n") 
        ## Print --------
        print("------------- [ LOG ] --------------")
        print("Time" + " "*25 + "|" + " "*4 + "Status")
        for index, row in enumerate(reversed(log)):
            if index == 0:
                print(row["time"] + " "*1 + "(Latest) |" + " "*4 + row["status"])
            else:
                print(row["time"] + " "*10 + "|" + " "*4 + row["status"])
            if index > 4:
                break
        
        if counter > 100:
            counter = 0
        else:
            counter += 1

        time.sleep(1)

if __name__ == "__main__":
    main()