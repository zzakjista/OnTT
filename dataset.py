import pandas as pd
import numpy as np
from datetime import date, timedelta

class Dataset:
    def __init__(self):
        self.path = 'data/'
        self.dataset = dict()
    def load_datasets(self):
        self.dataset['con'] = con = pd.read_csv('data/consumer.csv') #소비자데이터
        self.dataset['movie_info'] =  pd.read_csv('data/movie_info_1971_2022_clean.csv') #영화정보데이터
        self.dataset['price'] = pd.read_csv('data/CGV_Ticket_price.csv') #티켓가격 추이
        self.dataset['theater'] = pd.read_csv('data/theater.csv',encoding='euc-kr') #전국 상설영화관 추이
        self.dataset['boxoffice'] = pd.read_csv('data/boxoffice.csv',encoding = 'mbcs')#박스오피스
        self.dataset['netflix'] = pd.read_csv("data/netflix.csv", encoding = 'mbcs')#넷플릭스
        self.dataset['seat_share'] = pd.read_csv("data/seat_share.csv") #좌석점유율
        return self.dataset
    