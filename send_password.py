import os, datetime, time, hmac, hashlib, base64, urllib.parse, requests

WEBHOOK = os.environ["DINGTALK_WEBHOOK"]
SECRET = os.environ["DINGTALK_SECRET"]

def get_today_password():
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    print(f"正在查找的日期：{today_str}")

    try:
        with open("1_厂商密码表out.txt", "r", encoding="gbk") as f:
            lines = f.readlines()
        print(f"文件共 {len(lines)} 行")
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None

    for line in lines:
        parts = line.strip().split("\t")
        # 至少要有年、月、年月、日期、密码这5列
        if len(parts) < 5:
            continue

        # 第4列（索引3）是日期列，检查它是否等于今天
        if parts[3].strip() == today_str:
            print(f"找到匹配行，共 {len(parts)} 列")
            return parts[4].strip()

    print("未找到今日日期对应的行")
    return None

def send_to_dingtalk(content):
    timestamp = str(round(time.time() * 1000))
    secret_enc = SECRET.encode("utf-8")
    string_to_sign = f"{timestamp}\n{SECRET}"
    string_to_sign_enc = string_to_sign.encode("utf-8")
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    full_url = f"{WEBHOOK}&timestamp={timestamp}&sign={sign}"

    message = {
        "msgtype": "markdown",
        "markdown": {
            "title": "今日密码",
            "text": f"### 今日厂商密码提醒  \n\n日期：{datetime.date.today()}  \n密码：**{content}**"
        }
    }
    resp = requests.post(full_url, json=message, timeout=10)
    resp.raise_for_status()
    print("发送成功", resp.json())

if __name__ == "__main__":
    pwd = get_today_password()
    if pwd is None:
        print("未找到密码，不发送")
    else:
        send_to_dingtalk(pwd)
