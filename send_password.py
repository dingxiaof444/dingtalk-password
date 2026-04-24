import os
import datetime
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests

# ========== 以下两个值后面会设到 GitHub Secrets 中 ==========
WEBHOOK_URL = os.environ["DINGTALK_WEBHOOK"]
SECRET = os.environ["DINGTALK_SECRET"]

def get_today_password():
    """从同目录下的密码文件中读取今日密码"""
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    with open("1_厂商密码表out.txt", "r", encoding="utf-8") as f:
        for line in f:
            # 你的文件格式是 年 月 年月 日期 密码，由 tab 分隔
            if line.startswith(today_str):
                parts = line.strip().split("\t")
                if len(parts) >= 5:
                    return parts[4]   # 密码是第 5 列（从 0 开始数）
    return None

def send_to_dingtalk(content):
    """发送 Markdown 消息到钉钉机器人"""
    timestamp = str(round(time.time() * 1000))
    secret_enc = SECRET.encode("utf-8")
    string_to_sign = f"{timestamp}\n{SECRET}"
    string_to_sign_enc = string_to_sign.encode("utf-8")
    hmac_code = hmac.new(
        secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    full_url = f"{WEBHOOK_URL}&timestamp={timestamp}&sign={sign}"

    message = {
        "msgtype": "markdown",
        "markdown": {
            "title": "今日密码",
            "text": f"### 今日厂商密码提醒  \n\n日期：{datetime.date.today()}  \n密码：**{content}**  \n"
        }
    }

    resp = requests.post(full_url, json=message)
    resp.raise_for_status()
    print("消息发送成功", resp.json())

if __name__ == "__main__":
    pwd = get_today_password()
    if pwd is None:
        print("今日密码未找到，不发送消息。")
    else:
        send_to_dingtalk(pwd)
