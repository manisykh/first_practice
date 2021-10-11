import threading
import queue
import time
import datetime
import pyupbit
from collections import deque

class Consumer(threading.Thread):
    def __init__(self, q):
        super().__init__()
        self.q = q
        self.ticker = "KRW-BTT"

        self.ma15 = deque(maxlen=15)
        self.ma50 = deque(maxlen=50)
        self.ma120 = deque(maxlen=120)

        df = pyupbit.get_ohlcv(self.ticker, interval="minute1")
        self.ma15.extend(df['close'])
        self.ma50.extend(df['close'])
        self.ma120.extend(df['close'])

        # print(len(self.ma15), len(self.ma50),len(self.ma120))

    def run(self):
        price_curr = None
        hold_flag= False
        wait_flag = False

        with open("upbit.txt", "r") as f:
            key0 = f.readline().strip()
            key1 = f.readline().strip()

        upbit = pyupbit.Upbit(key0, key1)
        cash = upbit.get_balance()

        # A = open(r'C:\Users\Gil Bomin\python_class\Auto_trade_essential_files\upbit_ API Key_access.txt')
        # S = open(r'C:\Users\Gil Bomin\python_class\Auto_trade_essential_files\upbit_ API Key_secret.txt')
        # lines1 = A.readlines()
        # lines2 = S.readlines()
        # access = lines1[0]
        # secret = lines2[0]
        # A.close()
        # S.close()
        # upbit = pyupbit.Upbit('KvLKE7VAc2q8ka4WXk3LMAdwZTYnRZaDFLzcxtWP', 'a0BnhwpQE7BeMiYm5DB5bx4ifsiC8pawJ1Ok479e')
        # cash = upbit.get_balance()
        print("보유현금",  cash)


        while True:
            try:            
                if not self.q.empty():
                    if price_curr != None:
                        self.ma15.append(price_curr)
                        self.ma50.append(price_curr)
                        self.ma120.append(price_curr)

                    curr_ma15 = sum(self.ma15) / len(self.ma15)
                    curr_ma50 = sum(self.ma50) / len(self.ma50)
                    curr_ma120 = sum(self.ma120) / len(self.ma120)
                    

                    # 변경 사항: 매수하지 않았을때만 목표가 update!!
                    price_open = self.q.get()
                    if hold_flag ==False:
                        price_buy = price_open*1.01
                        price_sell = price_open*1.02
                    wait_flag = False
                
                price_curr = pyupbit.get_current_price(self.ticker)


                # 에러처리: 네트워크불안정등의 이유로 현재 가격이 반환되지 않으면 None이 출력되고, 그때는 continue로 while문의 처음으로 돌아간다.
                if price_curr == None:
                    continue
                #  매수 조건 실행 조건
                if hold_flag == False and wait_flag == False and price_curr >= price_buy and \
                    curr_ma15 >=curr_ma50 and curr_ma15 <= curr_ma50*1.03 and curr_ma120 <= curr_ma50:
                    ret = upbit.buy_market_order(self.ticker, cash*0.99)

                    #에러처리:시장가 주문을 실행한 결과 None 이라면 아직 주문 처리 되지 않았으니 Continue로 처음으로 돌아간다. 또한 처리되더라고 eorror를 반환하면 다시 돌아간다. 
                    if ret == None or "error" in ret:
                        continue
                    #get_order로 uuid를 조회하면 주문 정보 확인 가능, 주문정보가 None이 아니고 trades의 정보가 존재하면 (len()>0) 매수주문이 정상적으로 처리된것임.
                    # 주문이 정상적으로 조회가 되지 않는다면, 0.5초씩 쉬면서 재 조회 진행 후 정상 처리 되면 break하여 while문을 빠져 나옴.                        
                    while True:
                        order = upbit.get_order(ret['uuid'])
                        if order != None and len(order['trades']) >0:
                            print("매수주문 처리 완료", ret)
                            break
                        else:
                            print("매수 주문 대기 중")
                            time.sleep(0.5)

                    while True:    
                        volume = upbit.get_balance(self.ticker)
                        if volume != None:
                            break
                        time.sleep(0.5)

                    while True:
                        ret = upbit.sell_limit_order(self.ticker, price_sell, volume)
                        if ret != None and 'error' in ret:
                            print("매도 주문 에러")
                            time.sleep(0.5)
                        else:
                            print("매도주문", ret)
                            hold_flag = True
                            break

                    
                   
                # print(price_curr, curr_ma15, curr_ma50, curr_ma120)

                if hold_flag ==True:
                    uncomp = upbit.get_order(self.ticker)
                    if uncomp != None and len(uncomp) ==0:
                        cash = upbit.get_balance()
                        if cash == None:
                            continue
                        print("매도완료", cash)
                        hold_flag = False
                        wait_flag = True

                #3 minutes
                if i == (5*60*3):
                    print( f"[{datetime.datetime.now()}] 현재가 {price_curr}, 목표가{price_buy}, ma {curr_ma15:.2f} /{curr_ma50:.2f}/{curr_ma120:.2f} \
                        , {hold_flag}, {wait_flag}" )
                    i = 0
                i += 1

            except:
                print("error")
            time.sleep(0.2)
            
class Producer(threading.Thread):
    def __init__(self, q):
        super().__init__()
        self.q = q

    def run(self):
        while True:
            price = pyupbit.get_current_price("KRW-BTT")
            self.q.put(price)
            time.sleep(3)            
             
q = queue.Queue()
Producer(q).start()
Consumer(q).start()