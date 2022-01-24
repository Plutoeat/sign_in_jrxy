# !/usr/bin/python
# -*- coding:utf-8 -*-
# @author   : GaiusPluto
# @time     : 2022/1/23 8:58
# @version  : 1.0
import base64
import json
import os
import uuid
import oss2
import pyDes
import requests

from Config import logger
os.environ['NO_PROXY'] = 'campusphere.net'
with open('config/config.json', 'r', encoding='utf-8') as f:
    dc_form = json.load(f)['data']['form']
with open('config/config.json', 'r', encoding='utf-8') as f:
    address = json.load(f)['data']['login']['address']


class Login:
    def __init__(self, data):
        # 这key应该是逆向出来的
        logger.info('登录: 正在初始化网络会话')
        self.key = "b3L26XNL"
        self.session = requests.session()
        self.host = data['host']
        self.loginUrl = data['ampUrl']
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.37",
            "Pragma": "no-cache",
            "Accept": "application/json, text/plain, */*",
        })
        # 大佬的配置咱也不知到他是干哈的，也不敢乱改
        extension = {
            "deviceId": str(uuid.uuid4()),
            "systemName": "未来操作系统",
            "userId": "5201314",
            "appVersion": "9.0.16",
            "model": "红星一号量子计算机",
            "lon": 104.622818,
            "systemVersion": "初号机",
            "lat": 30.12702,
            "version": "first_v3",
            "calVersion": "firstv"
        }
        logger.info('加密: 开始加密')
        self.session.headers.update(
            {"Cpdaily-Extension": self.encrypt(json.dumps(extension))})
        logger.info('加密: 成功加密')
        logger.info('登录: 成功初始化网络会话')

    # 加密
    def encrypt(self, text):
        try:
            k = pyDes.des(self.key, pyDes.CBC, b"\x01\x02\x03\x04\x05\x06\x07\x08",
                          pad=None, padmode=pyDes.PAD_PKCS5)
            ret = k.encrypt(text)
            return base64.b64encode(ret).decode()
        except:
            # TODO send_email
            logger.debug('解密: 解密失败')
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
            # TODO send_email
            logger.debug('登录: 获取链接失败')
            exit(-1)

    # 登录
    def login(self, captcha=""):
        logger.info("登录: 正在获取用户配置信息")
        user = json.load(open('config/config.json', 'r', encoding='utf-8'))['data']['login']
        username = user['username']
        password = user['password']
        logger.info("登录: 成功获取用户配置信息")
        self.session.headers.update({"X-Requested-With": "XMLHttpRequest"})
        logger.info("登录: 正在获取参数")
        res1 = self.session.get(
            "https://{host}/iap/login?service=https://{host}/portal/login".format(host=self.host)).url
        lt = res1[res1.find("=") + 1:]
        logger.info("登录: 参数获取成功")
        logger.info("登录: 正在获取新的参数")
        res = self.request("https://{host}/iap/security/lt", "lt={lt}".format(lt=lt), True, False)
        lt = res["result"]["_lt"]
        logger.info("登录: 参数获取成功")
        data = {
            "username": username,
            "password": password,
            "lt": lt,
            "captcha": captcha,
            "rememberMe": "true",
            "dllt": "",
            "mobile": ""
        }
        logger.info("登录: 正在登录")
        res = self.request("https://{host}/iap/doLogin", data, True, False)
        if res["resultCode"] == "REDIRECT":
            self.session.get(res["url"])
            logger.info('登录成功')
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
                    logger.debug('第%d个默认配置不正确，请检查' % sort)
                    # TODO 发送邮件
                    exit(-1)
                # 文本直接赋值
                if formItem['fieldType'] == 1:
                    formItem['value'] = default['value']
                # 单选框需要删掉多余的选项
                if formItem['fieldType'] == 2:
                    # 填充默认值,现在不必填写默认值
                    # formItem['value'] = default['value']
                    fieldItems = formItem['fieldItems']
                    for i in range(0, len(fieldItems))[::-1]:
                        if fieldItems[i]['content'] == default['value']:
                            fieldItems[i]['isSelected'] = 1
                            if fieldItems[i]['content'] == '其他':
                                fieldItems[i]['contentExtend'] = default['ex_value']
                # 多选需要分割默认选项值，并且删掉无用的其他选项
                if formItem['fieldType'] == 3:
                    logger.INFO('作者没有遇见过第三种fieldType,支持可能并不友好')
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
                if formItem['fieldType'] == 4:
                    logger.INFO('作者没有遇见过第四种fieldType,支持可能并不友好')
                    fileName = self.uploadpicture(default['value'])
                    formItem['value'] = self.getpictureurl(fileName)
                logger.info('必填问题%d：' % sort + formItem['title'])
                logger.info('答案%d：' % sort + formItem['value'])
                sort += 1
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

    def submitform(self, formWid, collectWid, schoolTaskWid, form, address):
        data = {
            "formWid": formWid,
            "collectWid": collectWid,
            "form": form,
            "address": address,
            "schoolTaskWid": schoolTaskWid,
            "uaIsCpadaily": True,
            'latitude': 104.622818,
            'longitude': 36.12702
        }
        ret = self.request(
            "https://{host}/wec-counselor-collector-apps/stu/collector/submitForm", data)
        if ret["message"] == "SUCCESS":
            return True
        return False

    def autocomplete(self, address):
        logger.info('提交表单: 获取最新表单')
        collectList = self.getcollectorlist()
        collectWid = collectList[0]['wid']
        formWid = collectList[0]['formWid']
        instanceWid = collectList[0]['instanceWid']
        logger.info('提交表单: 获取学校Taskid')
        detailcollector = self.getdetailcollector(data={"collectorWid": collectWid, "instanceWid": instanceWid})
        schoolTaskWid = detailcollector['datas']['collector']['schoolTaskWid']
        logger.info('提交表单: 获取表单')
        form = self.queryform(
            data={"pageSize": "9999", "pageNumber": "1", "formWid": formWid, "collectorWid": collectWid, "instanceWid": instanceWid})
        logger.info('填写新表单')
        new_form = self.fillform(form)
        logger.info("提交表单: 提交表单")
        logger.debug("正在处理新版本今日校园")
        exit(-1)
        flag = self.submitform(formWid, collectWid, schoolTaskWid, new_form, address)
        if flag:
            # todo 告知签到成功
            logger.info('打卡成功')
        else:
            # todo 告知签到失败
            logger.debug('打卡失败,请重试')


def run():
    # 今日校园获取id的接口有连接限制，这里直接写上学校登录地址
    from sign_in.getSchoolLoginUrl import run02
    # data = run02()
    data = {'ampUrl': 'https://dlu.campusphere.net/wec-portal-mobile/client', 'host': 'dlu.campusphere.net'}
    app = Login(data)
    logger.info('登录: 开始准备登录')
    if not app.login():
        # TODO send_email
        logger.debug('登录:登录失败！！！')
        exit(-1)
    app.autocomplete(address)


if __name__ == '__main__':
    # 仅用于调试请勿调用
    run()
