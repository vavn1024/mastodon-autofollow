# coding = utf-8
import requests
import numpy as np
import telegram
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    "Authorization": "Bearer ***********************************",  # Bearer Token
}

wordList = [chr(i) for i in np.arange(97, 123)]
numList = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
following_count = 0
baseUrl = 'https://**********'  # mastodon实例地址
botName = '*****'  # telegram机器人用户名
openNotice = True  # 是否开启telegram通知
tgbot_token = '**********************'  # telegram机器人Token
tg_id = '***************'  # chat_id(在@getmyid_bot中获取)


def getUserInfo(key):
    url = baseUrl + "/api/v2/search"
    params = {"q": key, "resolve": True, "limit": 80}
    response = requests.get(url=url, params=params, headers=headers).json()
    return response


def followingRequest(id):
    url = f"{baseUrl}/api/v1/accounts/{id}/follow"
    response = requests.post(url=url, headers=headers)
    return response.headers.get("X-RateLimit-Remaining")


def getFollowingList(id):
    print("正在获取关注列表...")
    max_id = -1
    followingList = []
    while max_id != -2:
        url = f"{baseUrl}/api/v1/accounts/{id}/following"
        if max_id == -1:
            params = {}
        else:
            params = {"max_id": max_id}
        response = requests.get(url=url, params=params, headers=headers)
        response_json = response.json()
        try:
            link = response.headers.get("link")
            max_id = re.search("max_id=\d+", link).group(0)[7:]

        except:
            max_id = -2
        for j in response_json:
            if j["id"] not in followingList:
                followingList.append(j["id"])
    print(f"关注列表共有{len(followingList)}人")
    return followingList


def followingAll(ls, botId):
    followingList = getFollowingList(botId)
    for k in ls:
        for i in k:
            userInfo = getUserInfo(i)
            for j in userInfo["accounts"]:
                if j["id"] not in followingList and not j["locked"]:
                    remaining = int(followingRequest(j["id"]))
                    print("发送关注" + j["id"] + "请求成功")
                    if remaining < 50:
                        print("请求次数已达上限,请5分钟后再试！")
                        return
            print("keyword:" + i + ",complete!")


def telegram_notice(count):
    bot = telegram.Bot(token=tgbot_token)
    bot.send_message(chat_id=tg_id, text=f'定时任务执行完成\n成功关注{count - following_count}位用户',
                     parse_mode=telegram.ParseMode.HTML)
    print("发送TG通知成功")


def main():
    global following_count
    print("正在获取机器人id...")
    botInfo = getUserInfo(f"{botName}@{baseUrl[8:]}")["accounts"][0]
    bot_id = botInfo["id"]
    following_count = botInfo["following_count"]
    print(f"机器人id:{bot_id}")
    followingAll([wordList, numList], bot_id)
    if openNotice:
        following_count_now = len(getFollowingList(bot_id))
        telegram_notice(following_count_now)
    print("All Complete!")


if __name__ == '__main__':
    main()
