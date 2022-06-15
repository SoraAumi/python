import json
import os
import time

from file.file_util import FileUtil

import coloredlogs
import tqdm
import requests
import urllib3

req_url = 'https://business.huanengleasing.cn/modules/wfl_screen/PRJ_PROJECT/hn_prj_atm_before_db.lsc?document_id={' \
          'project_id}&document_table=PRJ_PROJECT '

wechat_server_url = 'http://sctapi.ftqq.com/{sendKey}.send'
Sora_send_key = '''SCT79558TBhJsgrVByfymoolYzF6ydp9Q'''


def get_request(url):
    response = requests.get(url, verify=False)
    return json.loads(response.text)


def send_wechat_msg(send_key, data):
    response = requests.post(wechat_server_url.format(sendKey=send_key), data)
    return response.text


def hn_project_req():
    try:
        tqdm.tqdm.write("开始检索")
        for item in tqdm.tqdm(FileUtil('./letters.txt').read_file('utf-8', 'list')):
            res = get_request(req_url.format(project_id=item))
            if res['message'] != '':
                tqdm.tqdm.write(f"项目:{item} 返回信息为:{res}")
    except Exception as e:
        print(e)
    finally:
        x = input("Press Enter to exit")


if __name__ == '__main__':
    coloredlogs.install(level='INFO')
    urllib3.disable_warnings()
    hn_project_req()
