import json
import os
import time
from functools import lru_cache

import dotenv
import requests

dotenv.load_dotenv()

PATH = os.getenv("API_URL")

campaigns = json.load(open("campaigns.json"))
clients = [c['client_id'] for c in json.load(open("clients.json"))]
scores = json.load(open("scores.json"))

def set_day(date: int):
    requests.post(PATH + "/time/advance", json={"current_date": date})

@lru_cache
def get_score(client_id: str, advertiser_id: str):
    for score in scores:
        if score['client_id'] == client_id and score['advertiser_id'] == advertiser_id:
            return score['score']
    return 0

requests.delete(PATH + "/views")

revenue = 0
resp_times = []
total_scores = []
cnt_404 = 0
for day in range(1, 13):
    set_day(day)
    print(f"Day {day}")
    for client in clients:
        for _ in range(15):
            start = time.perf_counter()
            res = requests.get(PATH + "/ads", params={"client_id": client})
            resp_times.append(time.perf_counter() - start)
            if res.status_code == 404:
                print(404)
                cnt_404 += 1
                break
            ad = res.json()
            revenue += campaigns[ad['ad_id']]['cost_per_impression']
            total_scores.append(get_score(client, ad['advertiser_id']))

print("Revenue:", revenue)
print("AVG Score:", sum(total_scores) / len(total_scores))
print("AVG Response Time:", sum(resp_times) * 1000 / len(resp_times))
print("404 Count:", cnt_404)