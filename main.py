import os
import requests

def get_weather():
    # 1. 從環境變數讀取鑰匙
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')
    user_id = os.getenv('LINE_USER_ID')

    # 2. 抓取雲林縣天氣預報 (斗六就在雲林縣)
    # F-C0032-001 是 36 小時預報
    weather_url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={cwa_key}&locationName=雲林縣"
    
    try:
        res = requests.get(weather_url).json()
        location_data = res['records']['location'][0]
        
        # 取得天氣現象 (如：晴時多雲)
        desc = location_data['weatherElement'][0]['time'][0]['parameter']['parameterName']
        # 取得降雨機率
        pop = location_data['weatherElement'][1]['time'][0]['parameter']['parameterName']
        # 取得氣溫
        min_t = location_data['weatherElement'][2]['time'][0]['parameter']['parameterName']
        max_t = location_data['weatherElement'][4]['time'][0]['parameter']['parameterName']

        msg = f"📍 雲林斗六今日預報：\n☁️ 天氣狀態：{desc}\n☔ 降雨機率：{pop}%\n🌡️ 氣溫：{min_t}°C - {max_t}°C"
        
        # 3. 發送 LINE 訊息
        line_url = 'https://api.line.me/v2/bot/message/push'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {line_key}'
        }
        payload = {
            "to": user_id,
            "messages": [{"type": "text", "text": msg}]
        }
        
        response = requests.post(line_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("訊息發送成功！")
        else:
            print(f"LINE 發送失敗: {response.text}")

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    get_weather()