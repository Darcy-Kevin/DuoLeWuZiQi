import requests,json

url = "http://120.53.247.249:8012/mails/send"

payload = {
    "passwd": "sscvrbbt532dfdgnmjyukukueghkkuhegnklethjk7gcs",
    "mailInfo": {
        "userlist": [461684],
        "addresser": "多乐五子棋团队",
        "title": "测试一下这个标题最长能展示多少个字",
        "content": "ssssssssssssssssssssssssss",
        "days": 1,
        "type": 0,
        "props": [
            {
                "proptype": 0,
                "propid": 0,
                "delta": 9999
            },
            {
                "proptype": 0,
                "propid": 1,
                "delta": 99999999
            },
            {
                "proptype": 0,
                "propid": 2,
                "delta": 9999
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

response = requests.post(url, data=payload)

print(response.text)