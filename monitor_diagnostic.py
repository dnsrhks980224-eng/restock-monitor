import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
}

def compact(text, limit=220):
    return " ".join(text.split())[:limit]

products = json.loads(Path("products.json").read_text(encoding="utf-8"))

print("=== 재고 감지 진단 시작 ===")

for p in products:
    print("\n" + "=" * 60)
    print("상품:", p["name"])
    print("요청 URL:", p["url"])
    try:
        r = requests.get(
            p["url"],
            headers=HEADERS,
            timeout=30,
            allow_redirects=True,
        )

        print("HTTP:", r.status_code)
        print("최종 URL:", r.url)
        print("리다이렉트:", len(r.history))
        print("Content-Type:", r.headers.get("content-type", ""))
        print("응답 bytes:", len(r.content))

        # requests의 추정 인코딩이 없거나 부정확할 때 보조
        if not r.encoding:
            r.encoding = r.apparent_encoding

        html = r.text
        text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)

        probes = [
            "품절", "일시품절", "판매종료", "구매불가", "재고없음",
            "구매하기", "바로구매", "장바구니", "주문하기",
            "sold out", "out of stock", "buy now", "add to cart",
            "sellStatCd", "saleStatus", "stockQuantity", "soldout",
        ]

        found = [x for x in probes if x.lower() in html.lower()]
        print("발견 키워드:", ", ".join(found) if found else "(없음)")
        print("페이지 텍스트 앞부분:", compact(text))

    except Exception as e:
        print("요청 오류:", type(e).__name__, str(e))

print("\n=== 진단 끝 ===")
