import os
import requests

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')
    user_id = os.getenv('LINE_USER_ID')

    # 瑞穗鄉專用 API (花蓮縣鄉鎮預報)
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-071?Authorization={cwa_key}&locationName=瑞穗鄉"
    
    try:
        res = requests.get(url).json()
        # 修正這裡的抓取路徑，這是鄉鎮預報最容易噴錯的地方
        location_data = res['records']['locations'][0]['location'][0]
        elements = location_data['weatherElement']
        
        # 提取資料：天氣描述、降雨機率、溫度
        desc = ""
        pop = ""
        temp = ""
        
        for elm in elements:
            if elm['elementName'] == 'Wx': # 天氣現象
                desc = elm['time'][0]['elementValue'][0]['value']
            elif elm['elementName'] == 'PoP12h': # 12小時降雨機率
                pop = elm['time'][0]['elementValue'][0]['value']
            elif elm['elementName'] == 'T': # 平均溫度
                temp = elm['time'][0]['elementValue'][0]['value']

        msg = (
            f"🍊 花蓮【瑞穗鄉】詳細預報\n"
            f"-------------------\n"
            f"☁️ 天氣狀況：{desc}\n"
            f"☔ 降雨機率：{pop}%\n"
            f"🌡️ 平均氣溫：{temp}°C\n"
            f"-------------------\n"
            f"祝瑞穗的朋友今天愉快！"
        )
        
        # 發送推播
        line_url = 'https://api.line.me/v2/bot/message/push'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
        payload = {"to": user_id, "messages": [{"type": "text", "text": msg}]}
        
        r = requests.post(line_url, headers=headers, json=payload)
        print(f"發送結果: {r.status_code}")

    except Exception as e:
        print(f"解析失敗，原因：{e}")

if __name__ == "__main__":
    get_weather()