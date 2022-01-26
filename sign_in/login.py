# !/usr/bin/python
# -*- coding:utf-8 -*-
# @author   : GaiusPluto
# @time     : 2022/1/23 8:58
# @version  : 1.0
import base64
import hashlib
import json
import os
from urllib import parse
import uuid
import oss2
import pyDes
import requests
from Crypto.Cipher import AES
from send_msg.send_wechat import send

# from Config import logger
os.environ['NO_PROXY'] = 'campusphere.net'
with open('config/config.json', 'r', encoding='utf-8') as f:
    dc_form = json.load(f)['data']['form']
with open('config/config.json', 'r', encoding='utf-8') as f:
    address = json.load(f)['data']['login']['address']
user = json.load(open('config/config.json', 'r', encoding='utf-8'))['data']['login']
username = user['username']
password = user['password']
lon = user['lon']
lat = user['lat']


class Login:
    def __init__(self, data, charset='utf-8'):
        # 这key应该是逆向出来的
        # logger.info('登录: 正在初始化网络会话')
        self.key = "XCE927=="
        self.bodyString_key = b"SASEoK4Pa5d4SssO"
        self.sign_key="SASEoK4Pa5d4SssO"
        self.charset = charset
        self.session = requests.session()
        self.host = data['host']
        self.loginUrl = data['ampUrl']
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.37",
            "Pragma": "no-cache",
            "Accept": "application/json, text/plain, */*",
        })
        # 哈哈哈
        extension = {
            "deviceId": str(uuid.uuid4()),
            "systemName": "未来操作系统",
            "userId": "5201314",
            "appVersion": "9.0.16",
            "model": "红星一号量子计算机",
            "lon": lon,
            "systemVersion": "初号机",
            "lat": lat,
        }
        # logger.info('加密: 开始加密')
        self.session.headers.update(
            {"Cpdaily-Extension": self.encrypt(json.dumps(extension))})
        # logger.info('加密: 成功加密')
        # logger.info('登录: 成功初始化网络会话')

    # 加密
    def encrypt(self, text):
        try:
            k = pyDes.des(self.key, pyDes.CBC, b"\x01\x02\x03\x04\x05\x06\x07\x08",
                          pad=None, padmode=pyDes.PAD_PKCS5)
            ret = k.encrypt(text)
            return base64.b64encode(ret).decode()
        except:
            # send_email
            send('提交表单失败','报错: 加密失败')
            # logger.debug('加密: 加密失败')
            exit(-1)

    # 重写requests方法
    def request(self, url: str, data=None, parseJson=True, JsonBody=True, Referer=None):
        try:
            url = url.format(host=self.host)
            if Referer != None:
                self.session.headers.update({"Referer": Referer})
            if data == None:
                res = self.session.get(url)
            else:
                self.session.headers.update(
                    {"Content-Type": ("application/json" if JsonBody else "application/x-www-form-urlencoded")})
                res = self.session.post(url, data=(
                    json.dumps(data) if JsonBody else data))
            if parseJson:
                return json.loads(res.text)
            else:
                return res
        except:
            # send_email
            send('提交表单失败','报错: 登陆时获取链接失败')
            # logger.debug('登录: 获取链接失败')
            exit(-1)

    # 登录
    def login(self, captcha=""):
        # logger.info("登录: 正在获取用户配置信息")
        # logger.info("登录: 成功获取用户配置信息")
        self.session.headers.update({"X-Requested-With": "XMLHttpRequest"})
        # logger.info("登录: 正在获取参数")
        res1 = self.session.get(
            "https://{host}/iap/login?service=https://{host}/portal/login".format(host=self.host)).url
        lt = res1[res1.find("=") + 1:]
        # logger.info("登录: 参数获取成功")
        # logger.info("登录: 正在获取新的参数")
        res = self.request("https://{host}/iap/security/lt", "lt={lt}".format(lt=lt), True, False)
        lt = res["result"]["_lt"]
        # logger.info("登录: 参数获取成功")
        data = {
            "username": username,
            "password": password,
            "lt": lt,
            "captcha": captcha,
            "rememberMe": "true",
            "dllt": "",
            "mobile": ""
        }
        # logger.info("登录: 正在登录")
        res = self.request("https://{host}/iap/doLogin", data, True, False)
        if res["resultCode"] == "REDIRECT":
            self.session.get(res["url"])
            # logger.info('登录成功')
            return True
        else:
            return False

    # 获取收集列表
    def getcollectorlist(self):
        data = {
            "pageSize": "6",
            "pageNumber": "1"
        }
        res = self.request(
            "https://{host}/wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList", data)
        return res["datas"]["rows"]

    # 获取schoolTaskWid
    def getdetailcollector(self, data):
        res = self.request("https://{host}/wec-counselor-collector-apps/stu/collector/detailCollector", data)
        return res

    # 查询form
    def queryform(self, data):
        res = self.request("https://{host}/wec-counselor-collector-apps/stu/collector/getFormFields", data)
        return res['datas']['rows']

    # 填写form
    def fillform(self, form):
        sort = 1
        for formItem in form:
            # 只处理必填项
            if formItem['isRequired'] == 1:
                default = dc_form['defaults'][sort - 1]['default']
                if formItem['title'] != default['title']:
                    # logger.debug('第%d个默认配置不正确，请检查' % sort)
                    # 发送邮件
                    send('提交表单失败','报错: 你的默认配置有误')
                    exit(-1)
                # 文本直接赋值
                if formItem['fieldType'] == '1':
                    formItem['value'] = default['value']
                # 单选框需要删掉多余的选项
                if formItem['fieldType'] == '2':
                    # 填充默认值,现在不必填写默认值
                    # formItem['value'] = default['value']
                    fieldItems = formItem['fieldItems']
                    for i in range(0, len(fieldItems))[::-1]:
                        if fieldItems[i]['content'] == default['value']:
                            fieldItems[i]['isSelected'] = 1
                            if fieldItems[i]['content'] == '其他':
                                fieldItems[i]['contentExtend'] = default['ex_value']
                        else:
                            formItem['fieldItems'].remove(fieldItems[i])
                # 多选需要分割默认选项值，并且删掉无用的其他选项
                if formItem['fieldType'] == '3':
                    # logger.INFO('作者没有遇见过第三种fieldType,支持可能并不友好')
                    fieldItems = formItem['fieldItems']
                    defaultValues = default['value'].split(',')
                    for i in range(0, len(fieldItems))[::-1]:
                        flag = True
                        for j in range(0, len(defaultValues))[::-1]:
                            if fieldItems[i]['content'] == defaultValues[j]:
                                # 填充默认值
                                formItem['value'] += defaultValues[j] + ' '
                                flag = False
                        if flag:
                            del fieldItems[i]
                # 图片需要上传到阿里云oss
                if formItem['fieldType'] == '4':
                    # logger.INFO('作者没有遇见过第四种fieldType,支持可能并不友好')
                    fileName = self.uploadpicture(default['value'])
                    formItem['value'] = self.getpictureurl(fileName)
                # logger.info('必填问题%d：' % sort + formItem['title'])
                # logger.info('答案%d：' % sort + formItem['value'])
                sort += 1
            else:
                if formItem['fieldType'] == '2':
                    # 填充默认值,现在不必填写默认值
                    # formItem['value'] = default['value']
                    fieldItems = formItem['fieldItems']
                    for i in range(0, len(fieldItems))[::-1]:
                        formItem['fieldItems'].remove(fieldItems[i])
        return form

    # 上传图片到阿里云oss
    def uploadpicture(self, image):
        url = 'https://{host}/wec-counselor-collector-apps/stu/collector/getStsAccess'.format(host=self.host)
        res = self.request(url=url, data=json.dumps({}))
        datas = res.json().get('datas')
        fileName = datas.get('fileName')
        accessKeyId = datas.get('accessKeyId')
        accessSecret = datas.get('accessKeySecret')
        securityToken = datas.get('securityToken')
        endPoint = datas.get('endPoint')
        bucket = datas.get('bucket')
        bucket = oss2.Bucket(oss2.Auth(access_key_id=accessKeyId, access_key_secret=accessSecret), endPoint, bucket)
        with open(image, "rb") as f:
            data = f.read()
        bucket.put_object(key=fileName, headers={'x-oss-security-token': securityToken}, data=data)
        bucket.sign_url('PUT', fileName, 60)
        return fileName

    # 获取图片上传位置
    def getpictureurl(self, fileName):
        url = 'https://{host}/wec-counselor-collector-apps/stu/collector/previewAttachment'.format(host=self.host)
        data = {
            'ossKey': fileName
        }
        res = self.request(url=url, data=data)
        photoUrl = res.json().get('datas')
        return photoUrl

    def pkcs7padding(self, text: str):
        """明文使用PKCS7填充"""
        remainder = 16 - len(text.encode(self.charset)) % 16
        return str(text + chr(remainder) * remainder)

    def encrypt_BodyString(self, text):
        """BodyString加密"""
        iv = b'\x01\x02\x03\x04\x05\x06\x07\x08\t\x01\x02\x03\x04\x05\x06\x07'
        cipher = AES.new(self.bodyString_key, AES.MODE_CBC, iv)

        text = self. pkcs7padding(text)  # 填充
        text = text.encode(self.charset)  # 编码
        text = cipher.encrypt(text)  # 加密
        text = base64.b64encode(text).decode(self.charset)  # Base64编码
        return text

    def geneHashObj(self, hash_type):
        if hash_type == 1:
            return hashlib.sha1()
        elif hash_type == 224:
            return hashlib.sha224()
        elif hash_type == 256:
            return hashlib.sha256()
        elif hash_type == 384:
            return hashlib.sha384()
        elif hash_type == 512:
            return hashlib.sha512()
        elif hash_type == 5:
            return hashlib.md5()
        elif hash_type == 3.224:
            return hashlib.sha3_224()
        elif hash_type == 3.256:
            return hashlib.sha3_256()
        elif hash_type == 3.384:
            return hashlib.sha3_384()
        elif hash_type == 3.512:
            return hashlib.sha3_512()
        else:
            raise Exception('类型错误, 初始化失败')

    def strHash(self, str_: str, hash_type):
        """计算字符串哈希
        :param str_: 字符串
        :param hash_type: 哈希算法类型
        :param charset: 字符编码类型
            1       sha-1
            224     sha-224
            256      sha-256
            384     sha-384
            512     sha-512
            5       md5
            3.256   sha3-256
            3.384   sha3-384
            3.512   sha3-512
        """
        hashObj = self.geneHashObj(hash_type)
        bstr = str_.encode(self.charset)
        hashObj.update(bstr)
        return hashObj.hexdigest()

    def signAbstract(self, submitData: dict):
        '''表单中sign项目生成'''
        abstractKey = ["appVersion", "bodyString", "deviceId", "lat",
                       "lon", "model", "systemName", "systemVersion", "userId"]
        abstractSubmitData = {k: submitData[k] for k in abstractKey}
        abstract = parse.urlencode(abstractSubmitData) + '&' + self.sign_key
        abstract_md5 = self.strHash(abstract, 5)
        return abstract_md5

    def submitform(self, formWid, collectWid, schoolTaskWid, form, instanceWid, address):
        rel_form = {
            "formWid": formWid,
            "collectWid": collectWid,
            "form": form,
            "address": address,
            "schoolTaskWid": schoolTaskWid,
            "uaIsCpadaily": True,
            'latitude': lat,
            'longitude': lon,
            'instanceWid': instanceWid
        }
        data = {
            "lon": "104.622818",
            "version": "first_v3",
            "calVersion": "firstv",
            "deviceId": str(uuid.uuid4()),
            "userId": username,
            "systemName": "iPadOS",
            "bodyString": self.encrypt_BodyString(json.dumps(rel_form)),
            "lat": "36.12702",
            "systemVersion": "15.2.1",
            "appVersion": "9.0.16",
            "model": "iPad13,4",
        }
        data['sign'] = self.signAbstract(data)
        res = self.request(
            "https://{host}/wec-counselor-collector-apps/stu/collector/submitForm", data)
        if res["message"] == "SUCCESS":
            return True
        return False

    def autocomplete(self, address):
        # logger.info('提交表单: 获取最新表单')
        collectList = self.getcollectorlist()
        collectWid = collectList[0]['wid']
        formWid = collectList[0]['formWid']
        instanceWid = collectList[0]['instanceWid']
        # logger.info('提交表单: 获取学校Taskid')
        detailcollector = self.getdetailcollector(data={"collectorWid": collectWid, "instanceWid": instanceWid})
        schoolTaskWid = detailcollector['datas']['collector']['schoolTaskWid']
        # logger.info('提交表单: 获取表单')
        form = self.queryform(
            data={"pageSize": "9999", "pageNumber": "1", "formWid": formWid, "collectorWid": collectWid, "instanceWid": instanceWid})
        # logger.info('填写新表单')
        new_form = self.fillform(form)
        # logger.info("提交表单: 提交表单")
        flag = self.submitform(formWid, collectWid, schoolTaskWid, new_form, instanceWid, address)
        if flag:
            # 告知签到成功
            send('提交表单成功', '你的今日校园表单已提交')
            # logger.info('success')
            print('success')
        else:
            # 告知签到失败
            # logger.debug('failure')
            send('提交表单失败','报错: 表单加密失败')
            print('failure')
            pass


def run():
    # 今日校园获取id的接口有连接限制，这里直接写上学校登录地址
    from sign_in.getSchoolLoginUrl import run02
    data = run02()
    # data = {'ampUrl': 'https://dlu.campusphere.net/wec-portal-mobile/client', 'host': 'dlu.campusphere.net'}
    app = Login(data)
    # logger.info('登录: 开始准备登录')
    if not app.login():
        # send_email
        send('提交表单失败','报错: 您未能成功登录')
        # logger.debug('登录:登录失败！！！')
        exit(-1)
    app.autocomplete(address)


if __name__ == '__main__':
    # 仅用于调试请勿调用
    run()
