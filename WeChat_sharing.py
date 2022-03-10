# -*- coding:utf-8 -*-
# author：LJ

# http://127.0.0.1:8080/latest_data/星球名/微信roomid/艾特名字
# http://127.0.0.1:8080/latest_data/爬虫技术分享/27917620291@chatroom/白寸  # 将数据发送
# http://127.0.0.1:8080/select_planet                                    # 查询星球
# http://127.0.0.1:8080/select_WeChat                                    # 查询微信群
# 27917620291@chatroom

import uvicorn
from fastapi import FastAPI
import websocket
import time
import json
from monitor import monitor, select_planet, get_group

SERVER = 'ws://127.0.0.1:5555'
AT_MSG = 550
USER_LIST = 5000

headers = {
    'authority': 'api.zsxq.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    'x-version': '2.18.0',
    'x-signature': 'c302d5753dafe8a84aac2df2fb7c6944f5c36248',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'accept': 'application/json, text/plain, */*',
    'x-timestamp': '1646207273',
    'x-request-id': '2ce1058a0-05cd-0e9d-0b9d-c6f11cfce9d',
    'sec-ch-ua-platform': '"Windows"',
    'origin': 'https://wx.zsxq.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://wx.zsxq.com/',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cookie': 'zsxq_access_token=0DE35B07-A866-8401-8A25-94CBAF1FB4A0_D3EA69AE3F149971',
}


def getid():
    id = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    return id


def send_at_msg(roomid, content, nickname):
    # 艾特群成员  以下都是必要参数
    j = {
        'id': getid(),
        'type': AT_MSG,
        'roomid': roomid,
        'wxid': 'your wxid',
        'content': content,
        'nickname': nickname,
        'ext': 'null'
    }
    s = json.dumps(j)
    return s

def send_wxuser_list():
    # 获取微信通讯录用户名字和wxid
    qs = {
        'id': getid(),
        'type': USER_LIST,
        'content': 'user list',
        'wxid': 'null',
    }
    s = json.dumps(qs)
    return s


app = FastAPI()


# 查询星球
@app.get("/select_planet")
async def root():
    result = select_planet(headers)
    if result == -1:
        return {'message': '可能网络抖动请重试；重试无效，可能cookie失效，请重新填入zsxq_access_token ----> ^_^!'}
    else:
        return {'message': result}


# 查询微信roomid
@app.get("/select_WeChat")
async def root():
    ws = websocket.create_connection(SERVER)
    ws.send(send_wxuser_list())
    result = json.loads(ws.recv())
    ws.close()
    content = result['content']
    groups = []
    for item in content:
        id = item['wxid']
        m = id.find('@')
        if m != -1:
            groups.append(f'微信群：---->roomid：{id}----name：{item["name"]}')

    return groups


# 将数据用微信发出
@app.get("/latest_data/{planet}/{roomid}/{nickname}")
async def root(planet,roomid,nickname):
    # 获取星球7天最新数据
    result = get_group(headers)
    if result == -1:
        return {'message': '可能网络抖动请重试；重试无效，可能cookie失效，请重新填入zsxq_access_token ----> ^_^!'}
    else:
        contents = monitor(planet, headers)
        for i in contents:
            content = json.dumps(i,sort_keys=True,indent=4,ensure_ascii=False)
            # 将数据用微信发出
            ws = websocket.create_connection(SERVER)
            ws.send(send_at_msg(roomid, str(content), nickname))
            ws.close()
        return {'message': contents}


if __name__ == '__main__':
    uvicorn.run(app='WeChat_sharing:app', host="127.0.0.1", port=8080, reload=True, debug=True)

