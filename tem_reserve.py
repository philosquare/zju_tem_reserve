# encoding:utf-8
import json
import urllib
import urllib2
import cookielib

INSTRUMENT_OLD_F20 = '28ad18ae3ebb4f91b1d52553019ca381'
INSTRUMENT_NEW_F20 = '563e690aae7b41dfb6da1880f291e65b'
id2instrument = {'28ad18ae3ebb4f91b1d52553019ca381': '老F20',
                 '563e690aae7b41dfb6da1880f291e65b': '新F20'}


class ReserveTem(object):
    def __init__(self):
        self.login_url = 'http://cem.ylab.cn/doLogin.action'  # GET or POST
        self.reserve_url = 'http://cem.ylab.cn/user/doReserve.action'  # POST
        self.add_comment_url = 'http://cem.ylab.cn/user/addReserveComment.action'  # POST
        self.delete_reserve_url = 'http://cem.ylab.cn/user/deleteReserve.action'  # GET or POST

        self.cookie = cookielib.CookieJar()
        self.handler = urllib2.HTTPCookieProcessor(self.cookie)
        self.opener = urllib2.build_opener(self.handler)

    def login(self, email, password):
        login_data = urllib.urlencode(dict(
            origUrl='',
            origType='',
            rememberMe='false',
            username=email,
            password=password
        ))
        login_result = self.opener.open(self.login_url, login_data)

        if login_result.geturl() != self.login_url:
            # 重定向则登录成功
            print '登录成功！'
            return True
        else:
            print '登录失败……'
            return False

    def reserve(self, reserveDate, reserveStartTime, reserveEndTime, instrumentId):
        reserve_data = urllib.urlencode({
            'reserveDate': reserveDate,
            'instrumentId': instrumentId,
            'reserveStartTime': reserveStartTime,
            'reserveEndTime': reserveEndTime
        })
        reserve_result = self.opener.open(self.reserve_url, reserve_data)

        result = json.loads(reserve_result.read())

        if 'success' in result["errorType"] and result["reserveRecordId"]:
            # 预约成功
            print id2instrument[instrumentId] + ' 预约成功! 预约时间：' + reserveDate + ' ' + \
                reserveStartTime + '-' + reserveEndTime
            return result["reserveRecordId"]
        else:
            print id2instrument[instrumentId] + ' 预约失败…… ' + result['errorCode'].encode('utf-8')
            return None

    def add_comment(self, instrumentId, reserveRecordId, msg):
        add_comment_data = urllib.urlencode({
            'instrumentId': instrumentId,
            'hideRest': '1',
            'reserveRecordId': reserveRecordId,
            'commentMandatory': 'true',
            'comment': msg
        })
        self.opener.open(self.add_comment_url, add_comment_data)

    def delete_reserve(self, reserveRecordId):
        delete_data = urllib.urlencode(dict(
            hideRest='1',
            reserveRecordId=reserveRecordId))
        result = self.opener.open(self.delete_reserve_url, delete_data)
        if '操作失败' in result.read():
            # 失败
            print '无此记录，删除失败'
        else:
            print '删除成功！'


if __name__ == '__main__':
    # 以下需填写
    # --------------------------------------
    email = ''
    password = ''
    reserve_info = [
        dict(
            reserveDate='2017年05月13日',  # '2017年05月14日'
            reserveStartTime='12:00',  # '12:00'
            reserveEndTime='13:00',  # '13:00'
            instrumentId=INSTRUMENT_NEW_F20  # INSTRUMENT_OLD_F20
        )
    ]

    # --------------------------------------

    rsv = ReserveTem()

    # 登录
    rsv.login(email, password)

    # 预定
    for info in reserve_info:
        id = rsv.reserve(reserveDate=info['reserveDate'],
                         reserveStartTime=info['reserveStartTime'],
                         reserveEndTime=info['reserveEndTime'],
                         instrumentId=info['instrumentId'])
        # 填写预订信息
        if id:
            rsv.add_comment(instrumentId=info['instrumentId'], reserveRecordId=id, msg='f20')
