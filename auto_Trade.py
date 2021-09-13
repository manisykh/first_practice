import pyupbit
import time  # 시간을 표현하는 라이브러리
import datetime  # 현재 시간을 알려주는 라이브러리

# Target Cost 를 지정 전략 별로 K value를 조정할 수 있다

def cal_target(ticker):
    df1 = pyupbit.get_ohlcv(ticker, interval = 'day1', count=200)
    yesterday = df1.iloc[-2]
    today = df1.iloc[-1]
    yesterday_range = yesterday['high'] - yesterday['low']
    target = today['open'] +yesterday_range*0.5
    return(target)

# 객체 생성(로그인)

A = open(r"C:\Users\Gil Bomin\python_class\Auto_trade_essential_files\upbit_ API Key_access.txt")
S = open(r"C:\Users\Gil Bomin\python_class\Auto_trade_essential_files\upbit_ API Key_secret.txt")
lines1 = A.readlines()
lines2 = S.readlines()
access = lines1[0]
secret = lines2[0]
A.close()
S.close()
upbit = pyupbit.Upbit(access, secret)


# 변수 설정

target = cal_target("KRW-BTT")
# print(target)
op_mode = False  # 현재 시간에는 operation 되지 않게 
hold =False  

while True:   # 항상이란 의미
    now = datetime.datetime.now()
 
    # 매도 시도

    if now.hour ==8 and now.minute == 59 and 50<= no.second <= 59:
        if op_mode is True and hold is True:
            BTT_balance = upbit.get_balance('KRW-BTT')
            upbit.sell_market_order("KRW-BTT", BTT_balance)
            hold = False
        
        op_mode = False
        time.sleep(10)
    
    
    # 목표가와 현재가 비교
    
    if now.hour ==9 and now.minute == 0 and 20<= now.second <= 30:
        target = cal_target("KRW-BTT")
        op_mode = True  # 위에서 정의한 오전 9시 20~30초 사이에 operation 되도록 구현
    
    price = pyupbit.get_current_price("KRW-BTT")


    # 매수 시도 조건에 맞게 매수 후 보유->True    
    
    if op_mode is True and hold is False and price>= target:
        krw_balance = upbit.get_balance('KRW')
        upbit.buy_market_order("KRW-BTT", krw_balance)
        hold = True 
        
        
    print(f'현재시간:{now} 목표가:{target} 현재가:{price} 보유상태:{hold} 동작상태: {op_mode}')
    time.sleep(1)
