import json

import coloredlogs

import requests

from file.file_util import read_file

req_url = 'https://business.huanengleasing.cn/modules/wfl_screen/PRJ_PROJECT/hn_prj_atm_before_db.lsc?document_id={' \
          'project_id}&document_table=PRJ_PROJECT '

wechat_server_url = 'http://sctapi.ftqq.com/{sendKey}.send'
Sora_send_key = '''SCT79558TBhJsgrVByfymoolYzF6ydp9Q'''


def get_request(url):
    response = requests.get(url, verify=False)
    return response.text


def send_wechat_msg(send_key, data):
    response = requests.post(wechat_server_url.format(sendKey=send_key), data)
    return response.text


if __name__ == '__main__':
    coloredlogs.install(level='WARNING')
    requests.packages.urllib3.disable_warnings()
    print(send_wechat_msg(Sora_send_key, {"title": "bilibili自动签到 登录失败"}))
