import os
import requests

def get_weather():
    cwa_key = os.getenv('CWA_TOKEN')
    line_key = os.getenv('LINE_TOKEN')

    # 花蓮縣各鄉鎮預報 (這個編號最穩)
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-071?Authorization={cwa_key}"
    
    try:
        res = requests.get(url).json()
        
        # 抓取地點列表
        locations = res['records']['locations'][0]['location']
        
        # 尋找瑞穗鄉 (嘗試完全比對)
        target = None
        for loc in locations:
            if '瑞穗' in loc['locationName']:
                target = loc
                break
        
        if target:
            elements = target['weatherElement']
            # 解析數據
            desc = next(e for e in elements if e['elementName'] == 'Wx')['time'][0]['elementValue'][0]['value']
            pop = next(e for e in elements if e['elementName'] == 'PoP12h')['time'][0]['elementValue'][0]['value']
            temp = next(e for e in elements if e['elementName'] == 'T')['time'][0]['elementValue'][0]['value']

            msg = (
                f"🍊 花蓮【{target['locationName']}】預報\n"
                f"-------------------\n"
                f"☁️ 天氣：{desc}\n"
                f"☔ 降雨：{pop}%\n"
                f"🌡️ 氣溫：{temp}°C\n"
                f"-------------------\n"
                f"{'📢 瑞穗的朋友出門要帶傘！' if int(pop) >= 30 else '☀️ 今天天氣不錯喔！'}"
            )
            
            line_url = 'https://api.line.me/v2/bot/message/broadcast'
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {line_key}'}
            payload = {"messages": [{"type": "text", "text": msg}]}
            
            r = requests.post(line_url, headers=headers, json=payload)
            print(f"發送成功！狀態碼: {r.status_code}")
        else:
            # 如果還是找不到，把所有地名印出來 Debug
            all_names = [l['locationName'] for l in locations]
            print(f"API 裡的地點有：{all_names}")
            print("找不到瑞穗鄉，請檢查 API 授權碼是否正確或有權限抓取鄉鎮預報")

    except Exception as e:
        print(f"解析失敗: {e}")

if __name__ == "__main__":
    get_weather()