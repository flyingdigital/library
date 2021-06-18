from appium import webdriver
import requests
import time
import re
'''
    通过 appium 控制手机登录微信  跳转至座位预约页面 获取其cookie
        会把 cookie存起来  如果cookie可以用就从文件拿取
                         不可用就控制手机登录座位页面  拿到cookie 存一份  返回一份
    使用条件：
        1. 微信用户要先关注 长江大学图书馆 公众号  (没有做判断)
        2. 手机微信 内置的浏览器 ChromeDriver版本 为 77.0.3865
'''
def getCookie():
    # appiumt 需要的参数
    desired_caps = {
        'platformName': 'Android',  # 被测手机是安卓
        'platformVersion': '10',  # 手机安卓版本
        'deviceName': 'xxx',  # 设备名，安卓手机可以随意填写
        'appPackage': 'com.tencent.mm',  # 启动APP Package名称
        'appActivity': '.ui.LauncherUI',  # 启动Activity名称
        'unicodeKeyboard': True,  # 使用自带输入法，输入中文时填True
        'resetKeyboard': True,  # 执行完程序恢复原来输入法
        'noReset': True,  # 不要重置App
        'newCommandTimeout': 6000,
        'automationName': 'UiAutomator2',
        'recreateChromeDriverSessions': True,
        'chromedriverExecutable': 'C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe',
        # 'chromeOptions':{'androidProcess': 'WEBVIEW_com.tencent.mm:toolsmp'}
    }

    # 连接Appium Server，初始化自动化环境
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

    # 设置缺省等待时间
    driver.implicitly_wait(20)

    # 点击搜索按钮
    driver.find_element_by_id("he6").click()

    # 根据id定位搜索输入框并点击  输入长江大学图书馆搜索公众号
    sbox = driver.find_element_by_id('bxz')
    sbox.send_keys('长江大学图书馆')

    # 进入公众号
    driver.find_element_by_xpath(
        '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.ListView/android.widget.RelativeLayout[2]/android.widget.LinearLayout').click()

    # 点击定制服务 座位预约
    time.sleep(1)
    driver.find_elements_by_id('fdd')[-1].click()
    time.sleep(1)
    driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout').click()

    time.sleep(5)

    # 打印所有 上下文
    print(driver.contexts)
    # 切换上下文
    driver.switch_to.context('WEBVIEW_com.tencent.mm:toolsmp')
    # print(driver.current_url)
    print(driver.window_handles)
    # 不同的handle对应的url
    # for i  in driver.window_handles:
    #     driver.switch_to.window(i)
    #     print(driver.current_url)

    # 跳转到指定句柄
    for i in driver.window_handles:
        driver.switch_to.window(i)
        if driver.current_url=="http://seat.yangtzeu.edu.cn/libseat-ibeacon/nowActivity":
            break
    # driver.switch_to.window(driver.window_handles[-1])
    # print(driver.current_url)
    # print(driver.get_cookies())
    # print(driver.current_url)
    # 拿到想要的东西 cookie
    cookie = ''
    for item in driver.get_cookies():
        cookie += item['name']+"="+item['value']+";"

    print('成功获取cookie')

    driver.quit()
    with open('cookie.txt','w') as f:
        f.write(cookie)
    return cookie

'''
    所有阅览室信息 get
        http://seat.yangtzeu.edu.cn/libseat-ibeacon/loadRooms?buildId=1&selectDate=2021-06-05
    单个阅览室所有座位信息 get
        http://seat.yangtzeu.edu.cn/libseat-ibeacon/seats?roomId=1&date=2021-06-05&linkSign=activitySeat&endTime=
    单个座位可以选择的开始时间段 (结束可选时间段也会传回来) get
        http://seat.yangtzeu.edu.cn/libseat-ibeacon/loadStartTime?seatId=5868&date=2021-06-05
    单个座位选择开始时间后 会请求可以选择的结束时间  get
        http://seat.yangtzeu.edu.cn/libseat-ibeacon/loadEndTimeByStart?seatId=5868&date=2021-06-05&start=1290
    提交预约  get
        http://seat.yangtzeu.edu.cn/libseat-ibeacon/saveBook?seatId=5868&date=2021-06-05&start=1290&end=1320&type=1
'''


'''
    获取当前时间的阅览室信息概览 并打印
    return 阅览室 信息概况data
'''
def getRoomInfos():
    # 所有阅览室座位信息总览
    roomInfoUrl = 'http://seat.yangtzeu.edu.cn/libseat-ibeacon/loadRooms?buildId=1&selectDate='+nowDate

    try:
        roomInfos = requests.get(roomInfoUrl,headers=headers).json()['params']
    except Exception as e:
        cookie = getCookie()
        headers['Cookie'] = cookie
        roomInfos = requests.get(roomInfoUrl, headers=headers).json()['params']

    # 获取并打印当前所有阅览室信息
    print('当前阅览室信息: '+' '*30 +'当前时间: '+str(time.ctime()))
    print('-'*50)
    for roomInfo in roomInfos['rooms']:
        print(str(roomInfo['floor'])+"F  "+roomInfo['room'])
        print('共有座位: '+str(roomInfo['totalSeats'])+"     "
              + '剩余座位: '+str(roomInfo['free'])+"     "
              + '正在使用座位: '+str(roomInfo['inUse'])
              )
        print('-' * 50)

    return roomInfos['rooms']


'''
    获取单个阅览室所有座位信息

    获取规则:
            1. 阅览室排序  二楼大厅 永远最后一个考虑  因为二楼会上下楼梯的人会非常多  非常之吵
                        其余阅览室优先获取空余座位最多的阅览室
                        另一种匹配规则是优先考虑楼层最高的阅览室
            2. 若阅览室是自然社科或大厅  优先考虑空余的靠窗座位(靠近一教)和沙发坐
            3. 优先考虑座位大于两个小时的时间段  若只有半个小时或以下  不考虑该座位
'''

'''
    通过楼层排序
        相同楼层根据空余座位进行排序
        二楼大厅会被排到最后
'''
def checkRoomByFloor():
    print("通过楼层排序...")
    rooms = getRoomInfos()
    roomRank = sorted(rooms,key=lambda x:(-x['floor'],-x['free']))

    # 把二楼大厅排到最后
    for i in range(len(roomRank)):
        if roomRank[i]['roomId']==4:
            room = roomRank.pop(i)
            roomRank.append(room)
    print(roomRank)
    return roomRank

'''
    通过剩余座位数最多的阅览室进行排序
'''
def checkRoomByFree():
    print("通过剩余座位数排序...")
    rooms = getRoomInfos()
    roomRank = sorted(rooms, key=lambda x: -x['free'])

    # 把二楼大厅排到最后
    for i in range(len(roomRank)):
        if roomRank[i]['roomId'] == 4:
            room = roomRank.pop(i)
            roomRank.append(room)
    # print(roomRank)
    return roomRank

'''
    获取某个阅览室的所有座位信息  并选择
    :param roomId 阅览室 id
    选择座位
        以下阅览室优先考虑靠窗 沙发坐(空余座位里有)
            一楼社科  49号及之后座位
            二楼大厅、三楼大厅  33号及之后座位
            二楼社科、三楼自科、四楼自科  53号及之后的座位
            四楼大厅  33-44的座位
'''
def checkSeat(roomId):
    print('获取座位信息并选择座位...')
    time.sleep(5)

    seatUrl = 'http://seat.yangtzeu.edu.cn/libseat-ibeacon/seats'
    params = {
        'roomId': roomId,
        'linkSign': 'activitySeat',
        'date': nowDate,
        'endTime': ''
    }
    response = requests.get(seatUrl,headers=headers,params=params).json()['params']['seats']
    # print(response)

    # 可用座位
    availableSeats = []
    for item in response:
        if item['type']=='seat' and item['status'] == 'FREE':
            availableSeats.append(item)
    print(availableSeats)

    # 优先获取
    for seat in availableSeats:
        seatName = int(seat['name'])
        seatId = None
        # 根据上边规则优先选择座位
        if roomId == 1:
            if seatName >= 49:
                seatId = seat['id']
        if roomId == 4 or roomId == 8:
            if seatName >= 33:
                seatId = seat['id']
        if roomId == 3 or roomId == 7 or roomId == 10:
            if seatName >= 53:
                seatId = seat['id']
        if roomId == 11:
            if seatName>=33 and seatName <=44:
                seatId = seat['id']
        if seatId!=None:
            timeList = checkTimePeriod(seat['id'])
            if checkTimePeriod(seatId)!=[]:
                bookingUrl = 'http://seat.yangtzeu.edu.cn/libseat-ibeacon/saveBook'
                bookingParams = {
                    'seatId': seat['id'],
                    'date': nowDate,
                    'type': 1,
                    'start': timeList[0],
                    'end': timeList[1]
                }
                bookingResponse = requests.get(bookingUrl, headers=headers, params=bookingParams).text
                print(bookingResponse)

                return True

    # 如果没有优先选择的座位  就开始一个个遍历
    for seat in availableSeats:
        timeList = checkTimePeriod(seat['id'])
        if timeList!=[]:
            bookingUrl = 'http://seat.yangtzeu.edu.cn/libseat-ibeacon/saveBook'
            bookingParams = {
                'seatId':seat['id'],
                'date': nowDate,
                'type': 1,
                'start': timeList[0],
                'end': timeList[1]
            }
            bookingResponse = requests.get(bookingUrl,headers=headers,params=bookingParams).text
            print(bookingResponse)

            return True
    return False


def checkTimePeriod(seatId):
    print('确定时间....')
    url = 'http://seat.yangtzeu.edu.cn/libseat-ibeacon/loadStartTime'
    params = {
        'seatId': seatId,
        'date': nowDate
    }
    response = requests.get(url,headers=headers,params=params)
    # print(response.text.replace(r"\"",""))

    period = re.findall('id.*?:(\d+),', response.text.replace(r"\"",""), re.S)


    # 只要能在其中找到跨度为120的 直接return
    periodId = []
    # print(period)
    for item in period:
        if str((int(item) + learningTime)) in period:
            # print(item)
            # print(str(int(item) + 60))
            periodId.append(item)
            periodId.append(str(int(item) + learningTime))
            break
    return periodId


# 需要学习的时间  分钟
learningTime = 180

# 当前年月日
year = str(time.localtime().tm_year)
month = time.localtime().tm_mon
day = time.localtime().tm_mday
if month < 10:
    month = '0' + str(month)
else:
    month = str(month)
if day < 10:
    day = '0' + str(day)
else:
    day = str(day)

nowDate = year + '-' + month + '-' + day

cookie = ''
# 尝试从文件获取 cookie  获取不到则通过手机获取
try:
    with open('cookie.txt', 'r') as f:
        cookie = f.read()
except Exception as e:
    cookie = getCookie()

if cookie == '':
    cookie = getCookie()

print(cookie)
# 请求头
headers = {
    "Cookie": cookie,  # getCookie()
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; EML-AL00 Build/HUAWEIEML-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045617 Mobile Safari/537.36 MMWEBID/3345 MicroMessenger/8.0.3.1880(0x2800033D) Process/toolsmp WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64",
}


roomRank = checkRoomByFree()
for room in roomRank:
    print(room['room'])
    if checkSeat(room['roomId']):
        break





