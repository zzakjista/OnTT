from dataset import Dataset

import pandas as pd
import numpy as np
from datetime import date, timedelta

class feature_engineering(Dataset):
    def __init__(self):
        super().__init__()

    def preprocessing(self):
        dataset = self.load_datasets()
        #소비자데이터
        con = dataset['con']
        movie_info = self.ppc_movie_info(dataset['movie_info'])
        theater = self.ppc_theater(dataset['theater'])
        boxoffice = self.ppc_boxoffice(dataset['boxoffice'])
        netflix = self.ppc_netflix(dataset['netflix'])
        price = self.ppc_price(dataset['price'])
        seat_share = self.ppc_seat_share(dataset['seat_share'])
        rehit_sort = self.make_rehit(boxoffice, movie_info)
        consumer = self.make_consumer(con)
        return con, movie_info, theater, boxoffice, netflix, price, seat_share, rehit_sort, consumer

    def ppc_movie_info(self,movie_info):
        #영화정보데이터 전처리
        movie_info['개봉일'] = pd.to_datetime(movie_info['개봉일'] , format = '%Y-%m-%d')
        movie_info.insert(19, '월', movie_info['개봉일'].dt.month) #월 feature 추가
        movie_info.insert(21, '전국 매출액(조 단위)', round(movie_info['전국 매출액(만 단위)']/10000000))
        return movie_info
    
    def ppc_theater(self,theater):
        theater.drop(columns='Unnamed: 0',inplace=True)
        theater['help'] = pd.to_datetime(theater['help'])
        return theater
    
    def ppc_boxoffice(self, boxoffice):
        boxoffice['개봉일'] = pd.to_datetime(boxoffice['개봉일'])
        return boxoffice
    
    def ppc_netflix(self, netflix):
        netflix['date_added'] = pd.to_datetime(netflix['date_added'] , format = '%Y-%m-%d')
        return netflix    
    
    def ppc_price(self, price):
        price['help'] = pd.to_datetime(price['help'])
        return price
    
    def ppc_seat_share(self, seat_share): 
        # 의미있는 영화에 대한 정보만 추출하기 위해 관객수 중앙값 이상의 영화만 추출
        seat_share = seat_share[seat_share['관객수']>seat_share['관객수'].median()]
        return seat_share
    
    def make_rehit(self, boxoffice, movie_info): #재개봉 영화 탐색을 위한 리스트 생성
        rehit= boxoffice[['영화명']].value_counts().reset_index()
        rehit.rename(columns={0:'개봉수'},inplace=True)
        rehit = rehit[rehit['개봉수']>1]
        rank = rehit.groupby('개봉수')['영화명'].count()
        rank=rank.reset_index()
        rank.rename(columns={'영화명':'영화수'},inplace=True)
        my_dict = {'관객수':'sum','매출액':'sum'}
        sales_merge = boxoffice.groupby(['영화명']).agg(my_dict) #영화별 매출액, 관객수
        rehit = rehit.merge(sales_merge,on='영화명',how='left')
        rehit_sort = rehit.sort_values('관객수',ascending=False)
        #rehit_sort[rehit_sort['관객수'] > rehit_sort['관객수'].mean()]
        rehit_sort=rehit_sort.merge(movie_info[['영화명','장르','등급','연도']],on='영화명',how='left').dropna()
        rehit_sort = rehit_sort.reset_index(drop=True)
        rehit_sort['연도'] = rehit_sort['연도'].astype('int')
        rehit_sort['관객수'] = rehit_sort['관객수'].astype('int')
        return rehit_sort
    
    def make_consumer(self, con):
        consumer = con.copy()
        Q15_list= {'1' : '영화 내용이 좋아서','2' : '영화 내용이 이해가 안 되어서','3' : '좋아하는 배우, 감독의 작품',
          '4' : '다른 사람과 다시 봐야 하는 상황','5' : '특별관(3D, IMAX 등)에서 다시 보고싶어서', ' ': '대답하지 않음','6' : '기타'}

        price_list = {1 : '15000원', 2 : '14500원', 3 : '14000원', 4 : '13500원', 5 : '13000원', 6 : '12500원', 7 : '12000원',
                    8 : '11500원', 9 : '11000원', 10 : '10500원', 11 : '10000원', 12 : '9500원', 13 : '9000원', 14 : '8500원',
                    15 : '8000원', 16 : '7500원', 17 : '7000원', 18 : '6500원', 19 : '6000원', 20 : '5500원', 21 : '5000원'}

        consumer['Q302']=consumer['Q302'].replace(price_list)
        consumer['Q312']=consumer['Q312'].replace(price_list)

        col = {'AGE' : '연령', 'Q14' : '재관람 경험여부', 'Q15' : '재관람 이유', 'Q302' : '극장 영화 티켓 1인 가격 인식 - 비싸다',
            'Q312' : '팝콘+음료세트 가격 인식 - 비싸다', 'Q1311' : '영화관 관람 호감도 평점', 'Q1321' : '영화관 관람 만족도 평점',
            'Q1331' : '추후 영화관 이용 의향', 'Q1314' : 'OTT 관람 호감도 평점', 'Q1324' : 'OTT 관람 만족도 평점', 'Q1334' : '추후 OTT 이용 의향'}
                
        consumer= consumer.rename(columns= col)          
        consumer['재관람 경험여부']=consumer['재관람 경험여부'].replace({2 : 0})
        consumer['재관람 이유']=consumer['재관람 이유'].replace(Q15_list)
        return consumer 

    def make_movie_kpi(self,movie_info):
        audi = movie_info.groupby('연도')[['전국 관객수']].sum()
        sales = movie_info.groupby('연도')[['전국 매출액','서울 매출액']].sum()
        audi = audi.merge(sales,on='연도',how='left').reset_index() #연도별 매출액, 관객수
        screen= movie_info.groupby('연도')['전국 스크린수'].sum().reset_index()
        audi = audi.merge(screen,on='연도',how='left') #극장산업 전년도 지표
        sales = audi[audi['연도']>=2016].copy() #2016년 이후 매출액, 관객수만 필터링(추후 분석을 위해)
        return audi, sales
    
    def make_theater_count(self,theater):
        theater_count=theater.groupby('년도')[['극장수']].sum()
        theater_count=theater_count.reset_index() #전국 극장수
        seoul_theater = theater[theater['지역']=='서울']
        seoul_theater = seoul_theater.reset_index(drop=True) #서울 극장수
        return theater_count, seoul_theater