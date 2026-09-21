import os, json, requests
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
TOKEN=os.getenv("TELEGRAM_BOT_TOKEN","")
CHAT_ID=os.getenv("TELEGRAM_CHAT_ID","")
sold_words=["품절","일시품절","판매종료","구매불가","재고없음","sold out","out of stock"]
available_words=["구매하기","바로구매","장바구니","주문하기","buy now","add to cart","in stock"]

def telegram(text):
    if TOKEN and CHAT_ID:
        r=requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                        data={"chat_id":CHAT_ID,"text":text},timeout=20)
        r.raise_for_status()

def status(html):
    text=BeautifulSoup(html,"html.parser").get_text(" ",strip=True).lower()
    sold=any(x.lower() in text for x in sold_words)
    available=any(x.lower() in text for x in available_words)
    if sold and not available: return "sold_out"
    if available and not sold: return "available"
    return "unknown"

products=json.loads(Path("products.json").read_text(encoding="utf-8"))
state_path=Path("state.json")
states=json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

for p in products:
    try:
        r=requests.get(p["url"],headers={"User-Agent":"Mozilla/5.0"},timeout=30)
        current=status(r.text)
        previous=states.get(p["url"],"unknown")
        print(p["name"],previous,"->",current)
        if previous=="sold_out" and current=="available":
            telegram(f"🚨 재입고 감지!\n{p['name']}\n{p['url']}")
        states[p["url"]]=current
    except Exception as e:
        print("오류:",p["name"],e)

state_path.write_text(json.dumps(states,ensure_ascii=False,indent=2),encoding="utf-8")
