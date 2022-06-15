# -*- coding: utf8 -*-
import json
import random
import time
import requests as r


def live_sign(sessdata):
    print("开始进行直播间签到")
    sign = r.get("https://api.live.bilibili.com/sign/doSign", cookies={"SESSDATA": sessdata})
    sign_info = json.loads(sign.text)

    if sign_info["code"] == 0:
        print("今日收获: " + sign_info["data"]["text"])
        print(sign_info["data"]["specialText"])
    else:
        print("签到失败：" + sign_info["message"])


def charge_self(sessdata, user_id, jct):
    print("今天是当月第一天，开始进行充电")

    # 领取B币券
    get_charge_url = "https://api.bilibili.com/x/vip/privilege/receive?type=1&csrf={}".format(jct)
    get_charge_res = r.post(get_charge_url, cookies={"SESSDATA": sessdata})
    get_charge_res_info = json.loads(get_charge_res.text)
    print(get_charge_res_info["message"])

    time.sleep(3)
    # 为自己充电
    charge_url = "https://api.bilibili.com/x/ugcpay/web/v2/trade/elec/pay/quick?bp_num=5&is_bp_remains_prior=true" \
                 "&up_mid={}&otype=up&oid={}&csrf={}".format(user_id, user_id, jct)
    charge_res = r.post(charge_url, cookies={"SESSDATA": sessdata})
    charge_res_info = json.loads(charge_res.text)
    if charge_res_info["data"]["status"] == -4:
        print("B 币余额不足")
    elif charge_res_info["data"]["status"] == 4:
        print("充值成功")


def video_sign(sessdata, jct):
    print("开始进行视频播放和分享")
    time.sleep(3)
    charge_res_info = {"data": [], "code": "-400"}
    while charge_res_info["code"] != 0:
        rids = [1, 3, 4, 5, 160, 22, 119]
        days = [1, 3, 7]
        top_url = "https://api.bilibili.com/x/web-interface/ranking/region?rid={}&day={}".format(random.choice(rids),
                                                                                                 random.choice(days))
        top_res = r.get(top_url, cookies={"SESSDATA": sessdata})
        charge_res_info = json.loads(top_res.text)
    random_video = random.choice(charge_res_info["data"])
    print("随机到的视频是{}，BV号是{}，就决定是你了！".format(random_video["title"], random_video["bvid"]))
    play_time = random.choice(range(90))

    watch_url = "https://api.bilibili.com/x/click-interface/web/heartbeat?aid={}&playtime={}".format(
        random_video["aid"], play_time)
    watch_res = r.post(watch_url, cookies={"SESSDATA": sessdata})
    watch_res_info = json.loads(watch_res.text)
    if watch_res_info["code"] == 0:
        print("已观看该视频到第{}秒".format(play_time))
    else:
        print(watch_res_info["message"])
    # time.sleep(2)

    # share_url = "https://api.bilibili.com/x/web-interface/share/add?bvid={}&csrf={}".format(random_video["bvid"], jct)
    # share_res = r.post(share_url, cookies={"SESSDATA": sessdata})
    # share_res_info = json.loads(share_res.text)
    # if share_res_info["code"] == 0:
    #     print("该视频分享成功")
    # else:
    #     print(share_res_info["message"])


def send_wechat_msg(send_key, data):
    wechat_server_url = 'http://sctapi.ftqq.com/{sendKey}.send'
    r.post(wechat_server_url.format(sendKey=send_key), data)


def bili_main(event, context):
    time.sleep(random.randint(0, 300))
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    sessdata = "b13d0555%2C1658313042%2Cf2289*11"
    jct = "2e00ce5affc7b4d596a59ee19782d368"
    user_id = "5985053"
    my_send_key = '''SCT79558TBhJsgrVByfymoolYzF6ydp9Q'''

    userinfo = json.loads(r.get("https://api.bilibili.com/x/web-interface/nav", cookies={"SESSDATA": sessdata}).text)
    if not userinfo["data"]["isLogin"]:
        print("登录失败")
        send_wechat_msg(my_send_key, {"title": "bilibili自动签到 登录失败"})
        return "Login Failed"
    data = userinfo["data"]
    print("用户名：" + data["uname"])
    print("UID：" + str(data["mid"]))
    print("当前等级为LV{}，经验值为{}".format(data["level_info"]["current_level"], data["level_info"]["current_exp"]))
    print("硬币还剩{}个".format(data["money"]))
    time.sleep(3)

    video_sign(sessdata, jct)
    time.sleep(2)

    live_sign(sessdata)
    time.sleep(2)


    charge_self(sessdata=sessdata, user_id=user_id, jct=jct)
    return "Finish"

