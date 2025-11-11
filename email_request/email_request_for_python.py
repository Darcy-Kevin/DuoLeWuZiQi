import json
import requests


def get_send_count(default: int = 1) -> int:
    """获取发送次数，支持自定义输入"""
    try:
        raw = input(f"请输入邮件发送次数（默认 {default} 次）: ").strip()
        if not raw:
            return default
        count = int(raw)
        if count < 1:
            raise ValueError("发送次数必须大于 0")
        return count
    except ValueError as exc:
        print(f"输入无效：{exc}，将按默认值 {default} 次发送。")
        return default


url = "http://120.53.247.249:8012/mails/send"

payload = {
    "passwd": "sscvrbbt532dfdgnmjyukukueghkkuhegnklethjk7gcs",
    "mailInfo": {
        "userlist": [461684],
        "addresser": "多乐五子棋团队",
        "title": "测试红点退场逻辑",
        "content": "亲爱的玩家：\n        感谢您的举报，经过多轮人工审核，查询您举报的牌局证明该玩家作弊，我们将对其进行封禁处理。给您的游戏豆补偿为您与违规用户所有对局的净输豆，若未对您造成损失，我们则不会进行补偿，请知悉。\n        多乐跑得快致力于打击各种类型的作弊行为，维护公平的游戏环境，给您和其他正直的玩家带来良好的游戏体验，再次感谢您对反作弊工作的支持。",
        "days": 1,
        "type": 0,
        "props": [
            {
                "proptype": 0,
                "propid": 0,
                "delta": 1
            }
        ],
        "from": 3,
        "extraInfo": {
            "type": 1,
            "extra": ""
        }
    }
}
payload["mailInfo"] = json.dumps(payload["mailInfo"])

send_count = get_send_count()

for index in range(1, send_count + 1):
    print(f"开始发送第 {index}/{send_count} 封邮件...")
    response = requests.post(url, data=payload)
    print(f"第 {index} 次发送结果：{response.status_code} -> {response.text}")
