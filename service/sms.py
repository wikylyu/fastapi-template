
# -*- coding: utf-8 -*-
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
# 导入对应产品模块的client models。
from tencentcloud.sms.v20210111 import sms_client, models

# 导入可选配置类
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile


from config.consul import read_config_by_key


_tencent_config = read_config_by_key('tencent')
_cred = credential.Credential(
    _tencent_config['secretid'], _tencent_config['secretkey'])

_sms_config = _tencent_config['sms']


def send_sms(phone: str, template: str, vars: list[str]):
    '''发送短信验证码'''
    try:
        client = sms_client.SmsClient(_cred, _tencent_config['region'])
        req = models.SendSmsRequest()
        req.SmsSdkAppId = _sms_config['appid']
        # 短信签名内容: 使用 UTF-8 编码，必须填写已审核通过的签名
        # 签名信息可前往 [国内短信](https://console.cloud.tencent.com/smsv2/csms-sign) 或 [国际/港澳台短信](https://console.cloud.tencent.com/smsv2/isms-sign) 的签名管理查看
        req.SignName = _sms_config['signname']
        # 模板 ID: 必须填写已审核通过的模板 ID
        # 模板 ID 可前往 [国内短信](https://console.cloud.tencent.com/smsv2/csms-template) 或 [国际/港澳台短信](https://console.cloud.tencent.com/smsv2/isms-template) 的正文模板管理查看
        req.TemplateId = _sms_config['templates'][template]
        # 模板参数: 模板参数的个数需要与 TemplateId 对应模板的变量个数保持一致，，若无模板参数，则设置为空
        req.TemplateParamSet = vars
        # 下发手机号码，采用 E.164 标准，+[国家或地区码][手机号]
        # 示例如：+8613711112222， 其中前面有一个+号 ，86为国家码，13711112222为手机号，最多不要超过200个手机号
        req.PhoneNumberSet = ["+86{}".format(phone)]

        resp = client.SendSms(req)
        return len(resp.SendStatusSet) > 0 and resp.SendStatusSet[0].Fee > 0
    except Exception as e:
        print(e)
    return False
