![header](https://capsule-render.vercel.app/api?type=waving&color=gradient&height=260&section=header&text=%ED%8C%8C%EC%9D%B4%EC%8D%AC%20%ED%95%9C%EA%B5%AD%ED%88%AC%EC%9E%90%EC%A6%9D%EA%B6%8C%20API%20WIKI&fontSize=50&animation=fadeIn&fontAlignY=38&desc=KIS%20Open%20Trading%20API%20Client&descAlignY=51&descAlign=62&customColorList=24)

## 1. PyKis 인증 관리

### 1.1. 시크릿 키 관리

시크릿 키를 관리하는 방법은 크게 2가지가 있습니다.

 1. 시크릿 키를 파일로 관리하는 방법
    ```python
    # 먼저 시크릿 키를 파일로 저장합니다.
    from pykis import KisAuth

    auth = KisAuth(
        # HTS 로그인 ID  예) soju06
        id="YOUR_HTS_ID",
        # 앱 키  예) Pa0knAM6JLAjIa93Miajz7ykJIXXXXXXXXXX
        appkey="YOUR_APP_KEY",
        # 앱 시크릿 키  예) V9J3YGPE5q2ZRG5EgqnLHn7XqbJjzwXcNpvY . . .
        secretkey="YOUR_APP_SECRET",
        # 앱 키와 연결된 계좌번호  예) 00000000-01
        account="00000000-01",
        # 모의투자 여부
        virtual=False,
    )

    # 안전한 경로에 시크릿 키를 파일로 저장합니다.
    auth.save("secret.json")
    ```

    그 후, 저장된 시크릿 키를 사용하여 PyKis 객체를 생성합니다.

    ```python
    from pykis import PyKis, KisAuth

    # 실전투자용 PyKis 객체를 생성합니다.
    kis = PyKis("secret.json", keep_token=True)
    kis = PyKis(KisAuth.load("secret.json"), keep_token=True)

    # 모의투자용 PyKis 객체를 생성합니다.
    kis = PyKis("secret.json", "virtual_secret.json", keep_token=True)
    kis = PyKis(KisAuth.load("secret.json"), KisAuth.load("virtual_secret.json"), keep_token=True)
    ```

1. 직접 시크릿 키를 입력하는 방법
   ```python
   from pykis import PyKis

    # 실전투자용 한국투자증권 API를 생성합니다.
    kis = PyKis(
        id="soju06",  # HTS 로그인 ID
        account="00000000-01",  # 계좌번호
        appkey="PSED321z...",  # AppKey 36자리
        secretkey="RR0sFMVB...",  # SecretKey 180자리
        keep_token=True,  # API 접속 토큰 자동 저장
    )

    # 모의투자용 한국투자증권 API를 생성합니다.
    kis = PyKis(
        id="soju06",  # HTS 로그인 ID
        account="00000000-01",  # 모의투자 계좌번호
        appkey="PSED321z...",  # 실전투자 AppKey 36자리
        secretkey="RR0sFMVB...",  # 실전투자 SecretKey 180자리
        virtual_id="soju06",  # 모의투자 HTS 로그인 ID
        virtual_appkey="PSED321z...",  # 모의투자 AppKey 36자리
        virtual_secretkey="RR0sFMVB...",  # 모의투자 SecretKey 180자리
        keep_token=True,  # API 접속 토큰 자동 저장
    )
    ```
    
### 1.2. 엑세스 토큰 관리

한국투자증권 개인 고객의 경우, 엑세스 토큰의 만료 기간은 1일이며, 엑세스 토큰을 발급받으면, 계좌와 연결된 카카오톡으로 알림이 전송됩니다.

PyKis는 엑세스 토큰을 자동으로 관리하기 때문에 일반적인 환경에서는 발급이나 만료를 직접 관리할 필요가 없습니다.

하지만 만약, PyKis 객체를 1일 이상 유지하기 어려운 환경이라면, 엑세스 토큰을 파일로 저장하여 기간이 남은 토큰을 재사용할 수 있습니다.

1. 토큰 자동 관리 활성화 방법
    ```python
    from pykis import PyKis

    # keep_token=True를 사용하여 토큰을 자동으로 저장합니다.
    # 기본 저장 경로는 ~/.pykis/ 입니다. 신뢰할 수 없는 환경에서 사용하지 마세요.
    kis = PyKis("secret.json", keep_token=True)
    ```
    
2. 토큰을 수동으로 관리하는 방법
    ```python
    from pykis.kis import PyKis, KisAccessToken

    # 저장된 토큰을 사용하려면 아래와 같이 PyKis 객체를 생성합니다.
    kis = PyKis("secret.json", token="token.json")
    kis = PyKis("secret.json", token=KisAccessToken.load("token.json"))
    # 또는 아래와 같이 PyKis 객체를 생성한 후 토큰을 설정합니다.
    kis = PyKis("secret.json")
    kis.token = KisAccessToken.load("token.json")

    # 아래 프로퍼티를 호출하면 만료기간이 보장된 토큰을 발급받을 수 있습니다.
    token = kis.token
    # 토큰의 정보를 확인합니다.
    print(repr(token), str(token))

    # 안전한 경로에 해당 토큰을 파일로 저장합니다.
    token.save("token.json")

    # 파일로 저장된 토큰이 만료되더라도 PyKis 객체에서 자동으로 갱신합니다.
    print(f"남은 유효기간: {kis.token.remaining}")
    ```
## 2. 종목 시세 및 차트 조회

기본적으로 어떠한 종목이든 시세를 조회하려면 `kis.stock('AAPL')` 처럼 종목의 개체를 받아와야 합니다.

국내주식, 해외주식에 상관 없이 모두 동일한 방법으로 조회할 수 있습니다.

```python
from pykis import KisStock

# 국내 주식
hynix: KisStock = kis.stock("000660")  # SK하이닉스 (코스피)
ecopro: KisStock = kis.stock("247540")  # 에코프로비엠 (코스닥)

# 해외 주식 (미국)
nvida: KisStock = kis.stock("NVDA")  # 엔비디아 (나스닥)
coupang: KisStock = kis.stock("CPNG")  # 쿠팡 (뉴욕)
```

API의 한계로 종목이 발견될 때까지 모든 시장을 순회하며 조회하므로 시장 정보를 함께 입력하면 더 빠르게 조회할 수 있습니다.

기본값은 한국 -> 미국 -> 일본 -> 홍콩 -> 중국 -> 베트남 순으로 조회합니다.

```python
tokyo_electric: KisStock = kis.stock("9501", market="TYO")  # 도쿄 전력 (도쿄)
# 또는 국가코드를 사용할 수 있습니다.
tokyo_electric: KisStock = kis.stock("9501", market="JP")  # 도쿄 전력 (도쿄)
```

PyKis의 stock함수로 얻은 종목 스코프(`KisStock`)는 기본적인 종목 정보를 담고 있습니다.

```python
print(
    f"""
종목코드: {hynix.symbol}
종목명: {hynix.name}
종목시장: {hynix.market}
"""
)

# 또한 info 프로퍼티를 통해 상세 정보를 얻을 수 있습니다.
print(
    f"""
종목코드: {hynix.info.symbol}
종목표준코드: {hynix.info.std_code}
종목명: {hynix.info.name}
종목영문명: {hynix.info.name_eng}
종목시장: {hynix.info.market}
종목시장한글명: {hynix.info.market_name}
"""
)
```

이렇게 얻은 종목 스코프를 이용해 시세, 주문가능 수량 조회, 매매 주문을 할 수 있습니다.

### 2.1. 시세 조회

`stock.quote()` 함수를 이용하여 국내주식 및 해외주식의 시세를 조회할 수 있습니다.

```python
from pykis import KisQuote

quote: KisQuote = kis.stock("CPNG").quote()

print(
    f"""
종목코드: {quote.symbol}
종목명: {quote.name}
종목시장: {quote.market}

업종명: {quote.sector_name}

현재가: {quote.price}
거래량: {quote.volume}
거래대금: {quote.amount}
시가총액: {quote.market_cap}
대비부호: {quote.sign}
위험도: {quote.risk}
거래정지: {quote.halt}
단기과열구분: {quote.overbought}

전일종가: {quote.prev_price}
전일거래량: {quote.prev_volume}
전일대비: {quote.change}

상한가: {quote.high_limit}
하한가: {quote.low_limit}
거래단위: {quote.unit}
호가단위: {quote.tick}
소수점 자리수: {quote.decimal_places}

통화코드: {quote.currency}
당일환율: {quote.exchange_rate}

당일시가: {quote.open}
당일고가: {quote.high}
당일저가: {quote.low}

등락율: {quote.rate}
대비부호명: {quote.sign_name}

==== 종목 지표 ====

EPS (주당순이익): {quote.indicator.eps}
BPS (주당순자산): {quote.indicator.bps}
PER (주가수익비율): {quote.indicator.per}
PBR (주가순자산비율): {quote.indicator.pbr}

52주 최고가: {quote.indicator.week52_high}
52주 최저가: {quote.indicator.week52_low}
52주 최고가 날짜: {quote.indicator.week52_high_date.strftime("%Y-%m-%d")}
52주 최저가 날짜: {quote.indicator.week52_low_date.strftime("%Y-%m-%d")}
"""
)
```

### 2.2. 차트 조회

 국내주식 및 해외주식의 당일 분봉과 기간 봉 차트를 조회합니다.

총 3가지의 함수(`chart`, `daily_chart`, `day_chart`) 가 있지만, `chart` 함수를 이용하여 모두 조회할 수 있습니다.

```python
from datetime import date, time
from pykis import KisChart

chart: KisChart = coupang.chart()  # 기본값은 상장 이래의 일봉입니다.
# 최근 기간 조회는 아래와 같이 시간 표현식을 사용할 수 있습니다.
# 1m: 1분
# 1h: 1시간
# 1d: 1일
# 1w: 1주
# 1M: 1개월 (개월 단위는 대문자 M)
# 1y: 1년
# 1y6M: 1년 6개월
chart: KisChart = coupang.chart("3d")  # 최근 3일 일봉입니다.
chart: KisChart = coupang.chart("1y", period="month")  # 최근 1년간의 월봉입니다.
chart: KisChart = coupang.chart(period="year")  # 상장 이래의 연간 일봉입니다.
chart: KisChart = coupang.chart(start=date(2023, 1, 1))  # 2023년 1월 1일부터 현재까지의 일봉입니다.
chart: KisChart = coupang.chart(
    start=date(2023, 1, 1),
    end=date(2024, 1, 1),
) # 2023년 1월 1일부터 2023년 12월 31일까지의 일봉입니다.

chart: KisChart = coupang.chart("1h", period=1)  # 최근 1시간의 1분봉입니다.
chart: KisChart = coupang.chart(period=5)  # 당일 5분봉입니다.
chart: KisChart = coupang.chart(period=1, end=time(12, 30))  # 당일 12시 30분까지의 1분봉입니다.
```

PyKis의 모든 객체는 repr를 통해 객체의 주요 내용을 확인할 수 있습니다.

```python
print(repr(hynix.chart("7d"))) # SK하이닉스의 최근 7일 일봉 차트
```
```python
KisDomesticDailyChart(
    market='KRX',
    symbol='000660',
    bars=[
        KisDomesticDailyChartBar(time='2024-07-19T00:00:00+09:00', open=208500, close=209500, high=214000, low=207000, volume=4519170, amount=949039126250, change=-3000),
        KisDomesticDailyChartBar(time='2024-07-22T00:00:00+09:00', open=209000, close=205000, high=209500, low=200500, volume=6662441, amount=1363039398518, change=-4500),
        KisDomesticDailyChartBar(time='2024-07-23T00:00:00+09:00', open=208500, close=205000, high=209500, low=200500, volume=5976519, amount=1224619868908, change=0),
        KisDomesticDailyChartBar(time='2024-07-24T00:00:00+09:00', open=202000, close=208500, high=212500, low=200000, volume=4838734, amount=1003813878000, change=3500),
        KisDomesticDailyChartBar(time='2024-07-25T00:00:00+09:00', open=196200, close=190000, high=198800, low=189000, volume=12503762, amount=2411730871900, change=-18500),
        KisDomesticDailyChartBar(time='2024-07-26T00:00:00+09:00', open=190800, close=191800, high=194500, low=186100, volume=8769107, amount=1670363205934, change=1800)
    ]
)
```

아래는 차트의 간단한 시각화 예시입니다.

먼저 필요한 라이브러리를 설치합니다.

```sh
pip install pandas lightweight-charts
```

```python
from datetime import datetime, timedelta
from lightweight_charts import JupyterChart

chart_view = JupyterChart(width=1280, height=720)
chart = nvida.chart("1y")

chart_view.set(chart.df()) # pykis의 차트 객체는 df함수를 이용하여 pandas DataFrame으로 변환할 수 있습니다.
chart_view.set_visible_range(datetime.now() - timedelta(days=365), datetime.now())

chart_view.load()
```

![image](https://github.com/user-attachments/assets/05d54e06-37dd-48a3-bb49-09b58b561716)


### 2.3. 호가 조회

`stock.orderbook()` 함수를 이용하여 국내주식 및 해외주식의 호가를 조회할 수 있습니다.

```python
from pykis import KisOrderbook

orderbook: KisOrderbook = hynix.orderbook()

print("매도1호가:", orderbook.ask_price, orderbook.ask_volumn)
print("매수1호가:", orderbook.bid_price, orderbook.bid_volumn)

print(repr(orderbook)) # repr을 통해 객체의 주요 내용을 확인할 수 있습니다.
```

```python
매도1호가: 192500 127
매수1호가: 192400 1384
KisDomesticOrderbook(
    market='KRX',
    symbol='000660',
    asks=[
        KisDomesticOrderbookItem(price=192500, volume=127),
        KisDomesticOrderbookItem(price=192600, volume=3630),
        KisDomesticOrderbookItem(price=192700, volume=559),
        KisDomesticOrderbookItem(price=192800, volume=693),
        KisDomesticOrderbookItem(price=192900, volume=461),
        KisDomesticOrderbookItem(price=193000, volume=2634),
        KisDomesticOrderbookItem(price=193100, volume=1151),
        KisDomesticOrderbookItem(price=193200, volume=379),
        KisDomesticOrderbookItem(price=193300, volume=842),
        KisDomesticOrderbookItem(price=193400, volume=1159)
    ],
    bids=[
        KisDomesticOrderbookItem(price=192400, volume=1384),
        KisDomesticOrderbookItem(price=192300, volume=2598),
        KisDomesticOrderbookItem(price=192200, volume=7793),
        KisDomesticOrderbookItem(price=192100, volume=12525),
        KisDomesticOrderbookItem(price=192000, volume=13471),
        KisDomesticOrderbookItem(price=191900, volume=10903),
        KisDomesticOrderbookItem(price=191800, volume=31044),
        KisDomesticOrderbookItem(price=191700, volume=930),
        KisDomesticOrderbookItem(price=191600, volume=1280),
        KisDomesticOrderbookItem(price=191500, volume=1921)
    ]
)
```

### 2.4. 장운영 시간 조회

`kis.trading_hours()` 함수를 이용하여 국내 및 해외 장운영 시간을 조회할 수 있습니다.

```python
from pykis import KisTradingHours

trading_hours: KisTradingHours = kis.trading_hours("US")

print(repr(trading_hours)) # repr을 통해 객체의 주요 내용을 확인할 수 있습니다.
```

```python
KisForeignTradingHours(
    market='NASDAQ',
    open='09:30:00',
    open_kst='22:30:00',
    close='16:00:00',
    close_kst='05:00:00'
)
```

## 3. 주문 및 잔고 조회

계좌의 잔고를 조회하려면 `kis.account()` 함수를 이용하여 잔고 스코프 개체를 받아와야 합니다.

```python
from pykis import KisAccount

account: KisAccount = kis.account() 
```

### 3.1. 예수금 및 보유 종목 조회

`account.balance()` 함수를 이용하여 예수금 및 보유 종목을 조회할 수 있습니다.

```python
from pykis import KisBalance

balance: KisBalance = account.balance()

print(repr(balance)) # repr을 통해 객체의 주요 내용을 확인할 수 있습니다.
```

```python
KisIntegrationBalance(
    account_number=KisAccountNumber('50113500-01'),
    deposits={
        'KRW': KisDomesticDeposit(account_number=KisAccountNumber('50113500-01'), currency='KRW', amount=2447692, exchange_rate=1),
        'USD': KisForeignPresentDeposit(account_number=KisAccountNumber('50113500-01'), currency='USD', amount=0, exchange_rate=1384.6),
    },
    stocks=[
        KisDomesticBalanceStock(account_number=KisAccountNumber('50113500-01'), market='KRX', symbol='000660', qty=14, price=192600, amount=2696400, profit=22900, profit_rate=0.856555077613615111277351786),
        KisDomesticBalanceStock(account_number=KisAccountNumber('50113500-01'), market='KRX', symbol='039200', qty=118, price=39600, amount=4672800, profit=-199500, profit_rate=-4.094575457176282248630010467)
    ],
    purchase_amount=7545800,
    current_amount=7369200,
    profit=-176600,
    profit_rate=-2.340374778022211031302181346
)
```

### 3.2. 기간 손익 조회

`account.profits()` 함수를 이용하여 기간 손익을 조회할 수 있습니다. (모의투자에서는 조회가 불가능합니다.)

```python
from datetime import date
from pykis import KisOrderProfits

profits: KisOrderProfits =account.profits(start=date(2023, 8, 1))

print(repr(profits)) # repr을 통해 객체의 주요 내용을 확인할 수 있습니다.
```

```python
KisIntegrationOrderProfits(
    account_number=KisAccountNumber('00000000-01'),
    buy_amount=8456747.364,
    sell_amount=8458122.90431,
    profit=1375.54031,
    orders=[
        KisDomesticOrderProfit(time_kst='2024-07-11T00:00:00+09:00', market='KRX', symbol='462870', name='시프트업', buy_price=60000, sell_price=85000, qty=1, profit=25000, profit_rate=41.66666666666666666666666667),
        KisForeignOrderProfit(time_kst='2024-06-18T00:00:00+09:00', market='NASDAQ', symbol='ARM', name='에이알엠 홀딩스(ADR)', buy_price=135.39, sell_price=161.14, qty=7, profit=180.25, profit_rate=19.01912992096905236723539405),
        KisForeignOrderProfit(time_kst='2024-05-23T00:00:00+09:00', market='NYSE', symbol='CPNG', name='쿠팡', buy_price=17.55, sell_price=22.3601, qty=1, profit=4.8101, profit_rate=27.40797720797720797720797721),
        KisDomesticOrderProfit(time_kst='2024-04-01T00:00:00+09:00', market='KRX', symbol='005930', name='삼성전자', buy_price=81700, sell_price=83200, qty=7, profit=10500, profit_rate=1.835985312117503059975520196),
        KisForeignOrderProfit(time_kst='2024-02-29T00:00:00+09:00', market='NASDAQ', symbol='MARA', name='매러선 디지털 홀딩스', buy_price=32.8718, sell_price=29.41, qty=37, profit=-128.09, profit_rate=-10.53146531169322348839886209),
        KisForeignOrderProfit(time_kst='2024-02-28T00:00:00+09:00', market='NASDAQ', symbol='NVDA', name='엔비디아', buy_price=738, sell_price=787.2, qty=1, profit=49.2, profit_rate=6.666666666666666666666666667),
        KisForeignOrderProfit(time_kst='2024-02-28T00:00:00+09:00', market='NASDAQ', symbol='SOUN', name='사운드하운드 AI', buy_price=7.028, sell_price=6.72, qty=45, profit=-13.86, profit_rate=-4.382470119521912350597609562),
        KisForeignOrderProfit(time_kst='2024-02-16T00:00:00+09:00', market='NASDAQ', symbol='AAPL', name='애플', buy_price=194, sell_price=184.46, qty=11, profit=-104.94, profit_rate=-4.917525773195876288659793814),
        KisForeignOrderProfit(time_kst='2024-02-16T00:00:00+09:00', market='NYSE', symbol='CPNG', name='쿠팡', buy_price=17.71, sell_price=15.76, qty=8, profit=-15.6, profit_rate=-11.01072840203274985883681536),
        KisForeignOrderProfit(time_kst='2023-12-13T00:00:00+09:00', market='NYSE', symbol='WMT', name='월마트', buy_price=159.09, sell_price=151.36, qty=1, profit=-7.73, profit_rate=-4.858884907913759507197183984),
        KisDomesticOrderProfit(time_kst='2023-09-04T00:00:00+09:00', market='KRX', symbol='389500', name='에스비비테크', buy_price=55400, sell_price=59200, qty=1, profit=3800, profit_rate=6.859205776173285198555956679),
        KisDomesticOrderProfit(time_kst='2023-08-09T00:00:00+09:00', market='KRX', symbol='228760', name='지노믹트리', buy_price=22200, sell_price=22250, qty=4, profit=200, profit_rate=0.2252252252252252252252252252),
        KisDomesticOrderProfit(time_kst='2023-08-09T00:00:00+09:00', market='KRX', symbol='008930', name='한미사이언스', buy_price=39600, sell_price=40200, qty=2, profit=1200, profit_rate=1.515151515151515151515151515)
    ]
)
```

### 3.3. 일별 체결 내역 조회

`account.daily_orders()` 함수를 이용하여 일별 체결 내역을 조회할 수 있습니다.

```python
from datetime import date
from pykis import KisDailyOrders

daily_orders: KisDailyOrders = account.daily_orders(start=date(2024, 4, 2), end=date(2024, 6, 1))

print(repr(daily_orders)) # repr을 통해 객체의 주요 내용을 확인할 수 있습니다.
```

```python
KisIntegrationDailyOrders(
    account_number=KisAccountNumber('00000000-01'),
    orders=[
        KisForeignDailyOrder(
            order_number=KisOrderBase(
                kis=kis,
                account_number=KisAccountNumber('00000000-01'),
                code='CPNG',
                market='NYSE',
                branch='01790',
                number='0030677379'
            ),
            type='sell',
            price=22.3601,
            qty=1,
            executed_qty=1
        ),
        KisForeignDailyOrder(
            order_number=KisOrderBase(
                kis=kis,
                account_number=KisAccountNumber('00000000-01'),
                code='NVDA',
                market='NASDAQ',
                branch='01790',
                number='0000018511'
            ),
            type='buy',
            price=0,
            qty=1,
            executed_qty=0
        ),
        KisForeignDailyOrder(
            order_number=KisOrderBase(
                kis=kis,
                account_number=KisAccountNumber('00000000-01'),
                code='NVDA',
                market='NASDAQ',
                branch='01790',
                number='0000011574'
            ),
            type='buy',
            price=0,
            qty=1,
            executed_qty=0
        )
    ]
)
```

### 3.4. 매수 가능 금액/수량 조회

`account.orderable_amount()` 또는 `stock.orderable_amount()` 함수를 이용하여 매수 가능 금액/수량을 조회할 수 있습니다.

```python
from pykis import KisOrderableAmount

# 엔비디아 주간거래 시장가 매수 가능 금액 조회
orderable_amount: KisOrderableAmount = account.orderable_amount(
    market="NASDAQ",
    symbol="NVDA",
    condition="extended"
)

print(repr(orderable_amount)) # repr을 통해 객체의 주요 내용을 확인할 수 있습니다.

# 오스코텍 단가 40,950원 매수 가능 금액 조회
orderable_amount: KisOrderableAmount = oscotec.orderable_amount(price=40950)

print(repr(orderable_amount)) # repr을 통해 객체의 주요 내용을 확인할 수 있습니다.
```

```python
KisForeignOrderableAmount(
    account_number=KisAccountNumber('50113500-01'),
    symbol='NVDA',
    market='NASDAQ',
    unit_price=109.18,
    qty=906,
    amount=100000,
    condition='extended',
    execution=None
)
KisDomesticOrderableAmount(
    account_number=KisAccountNumber('50113500-01'),
    symbol='039200',
    market='KRX',
    unit_price=40950,
    qty=59,
    amount=2435453,
    condition=None,
    execution=None
)
```

### 3.5. 매도 가능 수량 조회

매도 가능 수량은 `account.balance()`의 `KisBalanceStock` 객체 또는 `KisStock`의 단축 프로퍼티를 이용하여 조회할 수 있습니다.

1. 잔고 스코프의 `KisBalanceStock` 객체를 이용하여 조회하는 방법
    ```python
    from pykis import KisBalanceStock

    # 오스코텍 매도 가능 수량 조회
    balance_stock: KisBalanceStock = account.balance().stocks[1]
    balance_stock: KisBalanceStock | None = account.balance().stock("039200")

    print(balance_stock.orderable) # 매도 가능 수량
    ```

    ```python
    Decimal('118')
    ```
2. 종목 스코프의 단축 프로퍼티를 이용하여 조회하는 방법
    ```python
    oscotec = kis.stock("039200")

    # 오스코텍 매도 가능 수량 조회
    print(oscotec.orderable) # 매도 가능 수량
    ```

    ```python
    Decimal('118')
    ```

### 3.6. 미체결 주문 조회

`account.pending_orders()` 또는 `stock.pending_orders()` 함수를 이용하여 미체결 주문을 조회할 수 있습니다. (국내 모의투자는 조회가 불가능합니다.)

```python
from pykis import KisPendingOrders

# 계좌의 미체결 주문 조회
pending_orders: KisPendingOrders = account.pending_orders()
# 특정 종목의 미체결 주문 조회
pending_orders: KisPendingOrders = oscotec.pending_orders()

print(repr(pending_orders)) # repr을 통해 객체의 주요 내용을 확인할 수 있습니다.
```

```python
KisSimplePendingOrders(
    account_number=KisAccountNumber('00000000-01'),
    orders=[
        KisDomesticPendingOrder(
            order_number=KisOrderBase(
                kis=kis,
                account_number=KisAccountNumber('00000000-01'),
                code='039200',
                market='KRX',
                branch='91253',
                number='0000157444'
            ),
            type='buy',
            price=41300,
            qty=2,
            executed_qty=0,
            condition=None,
            execution=None
        )
    ]
)
```

### 3.7. 매도/매수 주문 및 정정/취소

`stock.order()`, `stock.buy()`, `stock.sell()`, `stock.modify()`, `stock.cancel()` 함수를 이용하여 매수/매도 주문 및 정정/취소를 할 수 있습니다.

#### 3.7.1. 매수/매도 주문

```python
from pykis import KisOrder

# SK하이닉스 1주 시장가 매수 주문
order: KisOrder = hynix.buy(qty=1)
# SK하이닉스 1주 지정가 매수 주문
order: KisOrder = hynix.buy(price=194700, qty=1)
# SK하이닉스 전량 시장가 매도 주문
order: KisOrder = hynix.sell()
# SK하이닉스 전량 지정가 매도 주문
order: KisOrder = hynix.sell(price=194700)

stock.buy(price=100, condition=None, execution=None) # 전체 지정가 매수
stock.buy(price=None, condition=None, execution=None) # 전체 시장가 매수
stock.buy(price=100, condition=None, execution=None) # 지정가 매수
stock.buy(price=None, condition=None, execution=None) # 시장가 매수
stock.buy(price=100, condition='condition', execution=None) # 조건부지정가 매수
stock.buy(price=100, condition='best', execution=None) # 최유리지정가 매수
stock.buy(price=100, condition='priority', execution=None) # 최우선지정가 매수
stock.buy(price=100, condition='extended', execution=None) # 시간외단일가 매수 (모의투자 미지원)
stock.buy(price=None, condition='before', execution=None) # 장전시간외 매수 (모의투자 미지원)
stock.buy(price=None, condition='after', execution=None) # 장후시간외 매수 (모의투자 미지원)
stock.buy(price=100, condition=None, execution='IOC') # IOC지정가 매수 (모의투자 미지원)
stock.buy(price=100, condition=None, execution='FOK') # FOK지정가 매수 (모의투자 미지원)
stock.buy(price=None, condition=None, execution='IOC') # IOC시장가 매수 (모의투자 미지원)
stock.buy(price=None, condition=None, execution='FOK') # FOK시장가 매수 (모의투자 미지원)
stock.buy(price=100, condition='best', execution='IOC') # IOC최유리 매수 (모의투자 미지원)
stock.buy(price=100, condition='best', execution='FOK') # FOK최유리 매수 (모의투자 미지원)
stock.buy(price=100, condition='LOO', execution=None) # 나스닥, 뉴욕, 아멕스 장개시지정가 매수 (모의투자 미지원)
stock.buy(price=100, condition='LOC', execution=None) # 나스닥, 뉴욕, 아멕스 장마감지정가 매수 (모의투자 미지원)
stock.buy(price=None, condition='MOO', execution=None) # 나스닥, 뉴욕, 아멕스 장개시시장가 매수 (모의투자 미지원)
stock.buy(price=None, condition='MOC', execution=None) # 나스닥, 뉴욕, 아멕스 장마감시장가 매수 (모의투자 미지원)
stock.buy(price=None, condition='extended', execution=None) # 나스닥, 뉴욕, 아멕스 주간거래 시장가 매수 (모의투자 미지원)
stock.buy(price=100, condition='extended', execution=None) # 나스닥, 뉴욕, 아멕스 주간거래 지정가 매수 (모의투자 미지원)

stock.sell(price=100, condition=None, execution=None) # 전체 지정가 매도
stock.sell(price=None, condition=None, execution=None) # 전체 시장가 매도
stock.sell(price=100, condition=None, execution=None) # 지정가 매도
stock.sell(price=None, condition=None, execution=None) # 시장가 매도
stock.sell(price=100, condition='condition', execution=None) # 조건부지정가 매도
stock.sell(price=100, condition='best', execution=None) # 최유리지정가 매도
stock.sell(price=100, condition='priority', execution=None) # 최우선지정가 매도
stock.sell(price=100, condition='extended', execution=None) # 시간외단일가 매도 (모의투자 미지원)
stock.sell(price=None, condition='before', execution=None) # 장전시간외 매도 (모의투자 미지원)
stock.sell(price=None, condition='after', execution=None) # 장후시간외 매도
stock.sell(price=100, condition=None, execution='IOC') # IOC지정가 매도 (모의투자 미지원)
stock.sell(price=100, condition=None, execution='FOK') # FOK지정가 매도 (모의투자 미지원)
stock.sell(price=None, condition=None, execution='IOC') # IOC시장가 매도 (모의투자 미지원)
stock.sell(price=None, condition=None, execution='FOK') # FOK시장가 매도 (모의투자 미지원)
stock.sell(price=100, condition='best', execution='IOC') # IOC최유리 매도 (모의투자 미지원)
stock.sell(price=100, condition='best', execution='FOK') # FOK최유리 매도 (모의투자 미지원)
stock.sell(price=100, condition='LOO', execution=None) # 나스닥, 뉴욕, 아멕스 장개시지정가 매도 (모의투자 미지원)
stock.sell(price=100, condition='LOC', execution=None) # 나스닥, 뉴욕, 아멕스 장마감지정가 매도 (모의투자 미지원)
stock.sell(price=None, condition='MOO', execution=None) # 나스닥, 뉴욕, 아멕스 장개시시장가 매도 (모의투자 미지원)
stock.sell(price=None, condition='MOC', execution=None) # 나스닥, 뉴욕, 아멕스 장마감시장가 매도 (모의투자 미지원)
stock.sell(price=None, condition='extended', execution=None) # 나스닥, 뉴욕, 아멕스 주간거래 시장가 매도 (모의투자 미지원)
stock.sell(price=100, condition='extended', execution=None) # 나스닥, 뉴욕, 아멕스 주간거래 지정가 매도 (모의투자 미지원)
```

#### 3.7.2. 주문 정정

```python
from pykis import KisOrder

order: KisOrder = hynix.buy(price=194700, qty=1) # 매수 주문

print(order.pending) # 미체결 주문인지 여부
print(order.pending_order.pending_qty) # 미체결 수량

order: KisOrder = order.modify(price=195000) # 단가 정정
order: KisOrder = order.modify(qty=10) # 수량 정정

order.cancel() # 주문 취소

# 미체결 주문 전체 취소
for order in account.pending_orders():
    order.cancel()
```

## 4. 실시간 이벤트 수신

PyKis의 웹소켓 연결과 구독 관리는 모두 자동으로 이루어집니다. 라이브러리 활용시 이벤트 리스닝시 발급되는 티켓만 관리하면 됩니다.

티켓은 Python GC에 의해 소멸되기 전까지 웹소켓 구독을 유지합니다. 동일 이벤트를 다중 수신하더라도 래퍼런스 카운터에 의해 안전하게 관리됩니다.

### 4.1. 이벤트 수신을 했는데, 바로 취소됩니다.

이벤트 수신을 했는데, 바로 취소되는 경우가 있습니다. 이는 이벤트 수신을 위한 티켓이 GC에 의해 소멸되었기 때문입니다.

아래와 같은 코드에서 티켓이 소멸될 수 있습니다.

```python
from pykis import PyKis, KisWebsocketClient, KisSubscriptionEventArgs, KisRealtimePrice

kis = PyKis("secret.json", keep_token=True)

def on_price(sender: KisWebsocketClient, e: KisSubscriptionEventArgs[KisRealtimePrice]):
    print(e.response)

def add_event():
    # 이벤트 리스닝 함수는 모두 KisEventTicket을 반환합니다.
    # 해당 티켓을 관리하지 않으면 GC에 의해 소멸됩니다.
    kis.stock("000660").on("price", on_price)
    kis.stock("005930").on("price", on_price)
    kis.stock("039200").on("price", on_price)

add_event()

print(kis.websocket.subscriptions) # 현재 구독중인 이벤트 목록

input("Press Enter to exit...")
```

```python
[07/31 16:51:27] INFO: RTC Connected to real server
[07/31 16:51:27] INFO: RTC Subscribed to H0STCNT0.005930
[07/31 16:51:27] INFO: RTC Unsubscribed from H0STCNT0.005930
[07/31 16:51:27] INFO: RTC Subscribed to H0STCNT0.039200
set() # 구독중인 이벤트 목록이 비어있습니다.
Press Enter to exit...
[07/31 16:51:27] INFO: RTC Unsubscribed from H0STCNT0.039200
```

해당 문제를 해결하기 위해 2가지 방법이 있습니다.

1. 티켓을 전역 변수로 유지하여 GC에 의해 소멸되지 않도록 합니다.
   ```python
   tickets = []

    def add_event():
         tickets.append(kis.stock("000660").on("price", on_price))
         tickets.append(kis.stock("005930").on("price", on_price))
         tickets.append(kis.stock("039200").on("price", on_price))

    add_event()

    print(kis.websocket.subscriptions) # 현재 구독중인 이벤트 목록

    input("Press Enter to exit...")

    for ticket in tickets:
        ticket.unsubscribe()
    ```
2. `with` 구문을 이용하여 범위 내에서만 티켓을 유지합니다.
   ```python
    def add_event():
        with kis.stock("000660").on("price", on_price) as ticket:
            input("Press Enter to exit...")

    add_event()
    ```
3. 티켓이 GC에 의해 구독 취소되지 않도록 플래그를 지정합니다.
   ```python
    def add_event():
        kis.stock("000660").on("price", on_price).suppress()
        kis.stock("005930").on("price", on_price).suppress()
        kis.stock("039200").on("price", on_price).suppress()

    add_event()

    print(kis.websocket.subscriptions) # 현재 구독중인 이벤트 목록

    input("Press Enter to exit...")
    ```

### 4.2. 실시간 체결가 조회

국내주식 및 해외주식의 실시간 체결가 조회는 `stock.on("price", callback)` 함수를 이용하여 수신할 수 있습니다.

```python
from pykis import KisRealtimePrice, KisSubscriptionEventArgs, KisWebsocketClient, PyKis

def on_price(sender: KisWebsocketClient, e: KisSubscriptionEventArgs[KisRealtimePrice]):
    print(e.response)

ticket = hynix.on("price", on_price)

print(kis.websocket.subscriptions) # 현재 구독중인 이벤트 목록

input("Press Enter to exit...")

ticket.unsubscribe()
```

```python
{KisWebsocketTR(id='H0STCNT0', key='000660')}
Press Enter to exit...
[08/02 13:50:42] INFO: RTC Connected to real server
[08/02 13:50:42] INFO: RTC Restoring subscriptions... H0STCNT0.000660
[08/02 13:50:42] INFO: RTC Subscribed to H0STCNT0.000660
KisDomesticRealtimePrice(market='KRX', symbol='000660', time='2024-08-02T13:50:44+09:00', price=174900, change=-18400, volume=8919304, amount=1587870362300)
KisDomesticRealtimePrice(market='KRX', symbol='000660', time='2024-08-02T13:50:44+09:00', price=174800, change=-18500, volume=8919354, amount=1587879102300)
KisDomesticRealtimePrice(market='KRX', symbol='000660', time='2024-08-02T13:50:45+09:00', price=174800, change=-18500, volume=8919358, amount=1587879801500)
KisDomesticRealtimePrice(market='KRX', symbol='000660', time='2024-08-02T13:50:45+09:00', price=174900, change=-18400, volume=8920313, amount=1588046831000)
KisDomesticRealtimePrice(market='KRX', symbol='000660', time='2024-08-02T13:50:45+09:00', price=174800, change=-18500, volume=8920319, amount=1588047879800)

[08/02 13:50:48] INFO: RTC Unsubscribed from H0STCNT0.000660
```

### 4.3. 실시간 호가 조회

국내주식 및 해외주식의 실시간 호가 조회는 `stock.on("orderbook", callback)` 함수를 이용하여 수신할 수 있습니다.

```python
from pykis import KisRealtimeOrderbook, KisSubscriptionEventArgs, KisWebsocketClient, PyKis

def on_orderbook(sender: KisWebsocketClient, e: KisSubscriptionEventArgs[KisRealtimeOrderbook]):
    print(e.response)

ticket = hynix.on("orderbook", on_orderbook)

print(kis.websocket.subscriptions) # 현재 구독중인 이벤트 목록

input("Press Enter to exit...")

ticket.unsubscribe()
```

```python
{KisWebsocketTR(id='H0STASP0', key='000660')}
Press Enter to exit...
[08/02 14:22:52] INFO: RTC Connected to real server
[08/02 14:22:52] INFO: RTC Restoring subscriptions... H0STASP0.000660
[08/02 14:22:52] INFO: RTC Subscribed to H0STASP0.000660
KisDomesticRealtimeOrderbook(
    market='KRX',
    symbol='000660',
    asks=[
        KisDomesticRealtimeOrderbookItem(price=174000, volume=10689),
        KisDomesticRealtimeOrderbookItem(price=174100, volume=7197),
        KisDomesticRealtimeOrderbookItem(price=174200, volume=3430),
        KisDomesticRealtimeOrderbookItem(price=174300, volume=3120),
        KisDomesticRealtimeOrderbookItem(price=174400, volume=4865),
        KisDomesticRealtimeOrderbookItem(price=174500, volume=477),
        KisDomesticRealtimeOrderbookItem(price=174600, volume=1818),
        KisDomesticRealtimeOrderbookItem(price=174700, volume=3344),
        KisDomesticRealtimeOrderbookItem(price=174800, volume=2184),
        KisDomesticRealtimeOrderbookItem(price=174900, volume=2266)
    ],
    bids=[
        KisDomesticRealtimeOrderbookItem(price=173900, volume=12054),
        KisDomesticRealtimeOrderbookItem(price=173800, volume=15792),
        KisDomesticRealtimeOrderbookItem(price=173700, volume=12568),
        KisDomesticRealtimeOrderbookItem(price=173600, volume=19204),
        KisDomesticRealtimeOrderbookItem(price=173500, volume=71514),
        KisDomesticRealtimeOrderbookItem(price=173400, volume=6470),
        KisDomesticRealtimeOrderbookItem(price=173300, volume=9029),
        KisDomesticRealtimeOrderbookItem(price=173200, volume=8204),
        KisDomesticRealtimeOrderbookItem(price=173100, volume=15445),
        KisDomesticRealtimeOrderbookItem(price=173000, volume=36000)
    ]
)

[08/02 14:22:56] INFO: RTC Unsubscribed from H0STASP0.000660
```

### 4.4. 실시간 체결내역 조회

국내주식 및 해외주식의 실시간 체결내역 조회는 `account.on("execution", callback)` 함수를 이용하여 수신할 수 있습니다.

```python
from pykis import KisRealtimeExecution, KisSubscriptionEventArgs, KisWebsocketClient

account = kis.account()

def on_execution(sender: KisWebsocketClient, e: KisSubscriptionEventArgs[KisRealtimeExecution]):
    print(e.response)


ticket = account.on("execution", on_execution)

print(kis.websocket.subscriptions)  # 현재 구독중인 이벤트 목록

input("Press Enter to exit...")

ticket.unsubscribe()
```

```python
{KisWebsocketTR(id='H0GSCNI9', key='soju06'), KisWebsocketTR(id='H0STCNI9', key='soju06')}
Press Enter to exit...
[08/02 14:27:24] INFO: RTC Connected to real server
[08/02 14:27:24] INFO: RTC Connected to virtual server
[08/02 14:27:24] INFO: RTC Restoring subscriptions... H0GSCNI9.soju06
[08/02 14:27:24] INFO: RTC Restoring subscriptions... H0STCNI9.soju06
[08/02 14:27:24] INFO: RTC Subscribed to H0STCNI9.soju06
[08/02 14:27:24] INFO: RTC Subscribed to H0GSCNI9.soju06
KisDomesticRealtimeOrderExecution(account_number=KisAccountNumber('50113500-01'), market='KRX', symbol='000660', time='2024-08-02T14:28:25+09:00', type='buy', price=173600, executed_qty=0)
KisDomesticRealtimeOrderExecution(account_number=KisAccountNumber('50113500-01'), market='KRX', symbol='000660', time='2024-08-02T14:28:25+09:00', type='buy', price=173600, executed_qty=10)
KisDomesticRealtimeOrderExecution(account_number=KisAccountNumber('50113500-01'), market='KRX', symbol='000660', time='2024-08-02T14:28:25+09:00', type='buy', price=173600, executed_qty=10)
```
