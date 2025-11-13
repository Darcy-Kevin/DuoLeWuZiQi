#!/bin/bash

for i in {1}; do
  echo "执行第 $i 次请求..."
  curl --request POST \
    --url http://120.53.247.249:8012/mails/send \
    --header 'Accept: */*' \
    --header 'Accept-Encoding: gzip, deflate, br' \
    --header 'Connection: keep-alive' \
    --header 'User-Agent: PostmanRuntime-ApipostRuntime/1.1.0' \
    --data passwd=sscvrbbt532dfdgnmjyukukueghkkuhegnklethjk7gcs \
    --data 'mailInfo={
  "userlist": [
        461684
  ],
  "addresser": "多乐五子棋团队",
  "title": "滕王阁序",
  "content": "豫章故郡",
  "days": 1,
  "type": 0,
  "props": [
      {
          "proptype": 0,
          "propid": 0, 
          "delta": 400000
      },
      {
          "proptype": 0,
          "propid": 2, 
          "delta": 4
      },
      {
          "proptype": 0,
          "propid": 2, 
          "delta": 4
      },
      {
          "proptype": 0,
          "propid": 2, 
          "delta": 4
      },
      {
          "proptype": 0,
          "propid": 2, 
          "delta": 4
      },
      {
          "proptype": 0,
          "propid": 2, 
          "delta": 4
      },
      {
          "proptype": 0,
          "propid": 2, 
          "delta": 4
      },
      {
          "proptype": 0,
          "propid": 2, 
          "delta": 4
      },
      {
          "proptype": 0,
          "propid": 2, 
          "delta": 4
      },
      {
          "proptype": 0,
          "propid": 2, 
          "delta": 4
      },
      {
          "proptype": 0,
          "propid": 2, 
          "delta": 4
      },
      {
          "proptype": 0,
          "propid": 2, 
          "delta": 4
      },
      {
          "proptype": 0,
          "propid": 2, 
          "delta": 4
      },
      {
          "proptype": 0,
          "propid": 2, 
          "delta": 4
      }
  ],
  "from": 3,
  "extraInfo": {
      "type": 1,
      "extra": ""
  }
}'
done

echo "完成！已执行 $i 次请求。"