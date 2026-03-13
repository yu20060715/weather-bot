import os
import requests

def get_weather():
    # 中央氣象署 API URL (以台北市為例)
    token = os.getenv('CWA_TOKEN')
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={token}&locationName=臺北市&elementName=PoP,MaxT,MinT"
    
    res = requests.get(url).json()
    data = res['records']['location'][0]['weatherElement']
    
    # 提取降雨機率 (PoP)、最高溫 (MaxT)、最低溫 (MinT)
    pop = data[0]['time'][0]['parameter']['parameterName']
    min_t = data[1]['time'][0]['parameter']['parameterName']
    max_t = data[2]['time'][0]['parameter']['parameterName']
    
    return f"今日台北天氣：\n🌡️ 氣溫：{min_t}°C - {max_t}°C\n☔ 降雨機率：{pop}%"

def send_line(msg):
    line_token = os.getenv('LINE_TOKEN')
    user_id = os.getenv('LINE_USER_ID')
    
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {line_token}'
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": msg}]
    }
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    content = get_weather()
    send_line(content)