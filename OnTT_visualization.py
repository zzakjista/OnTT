from feature_engineering import feature_engineering

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style='whitegrid', font_scale=1.5)
sns.set_palette('Set2', n_colors=10)
plt.rc('font', family='malgun gothic')
plt.rc('axes', unicode_minus=False)
import streamlit as st
from datetime import date, timedelta

### importing data ###
con, movie_info, theater, boxoffice, netflix, price, seat_share, rehit_sort, consumer = feature_engineering().preprocessing()
######################


st.set_page_config(page_title='OnTT Data App', 
                   page_icon='🎬', layout='centered')
st.title("🎬OnTT Dashboard")

if st.button('새로고침'):
    st.experimental_rerun()

my_movie_info= movie_info.copy()
my_netflix = netflix.copy()
my_boxoffice = boxoffice.copy()

### sidebar ###
st.sidebar.title("조건 필터")
st.sidebar.header("날짜 조건")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("시작일시", date(2008, 1, 1),
                                       min_value=date(2008,1,1),
                                       max_value=date(2021,12,30))
with col2:
    end_date = st.date_input("종료일시", date(2021, 12, 31),
                                     min_value=date(2008,1,2),
                                     max_value=date(2021,12,31))
if end_date - start_date<=timedelta(days=1095):
    st.warning("⚠ 경고 : 3년 이내의 날짜 범위를 입력하면 자료가 깨질 수 있습니다")
################

### filtering ###    
my_movie_info = my_movie_info[my_movie_info['개봉일'].dt.date.between(start_date, end_date)]
my_netflix = my_netflix[my_netflix['date_added'].dt.date.between(start_date, end_date)]
my_boxoffice = my_boxoffice[my_boxoffice['개봉일'].dt.date.between(start_date, end_date)]
price = price[price['help'].dt.date.between(start_date, end_date)]
theater = theater[theater['help'].dt.date.between(start_date, end_date)]
rehit_sort = rehit_sort[rehit_sort['연도'] >= start_date.year]
#################

### adding features ###
audi= my_movie_info.groupby('연도')[['전국 관객수']].sum()
sales = my_movie_info.groupby('연도')[['전국 매출액','서울 매출액']].sum()
audi = audi.merge(sales,on='연도',how='left').reset_index()
sales = audi.copy()
screen= my_movie_info.groupby('연도')['전국 스크린수'].sum().reset_index()
audi = audi.merge(screen,on='연도',how='left')

theater_count=theater.groupby('년도')[['극장수']].sum()
theater_count=theater_count.reset_index() #전국 극장수
seoul_theater = theater[theater['지역']=='서울']
seoul_theater = seoul_theater.reset_index(drop=True) #서울 극장수
################################

# 1.Overview
st.header('1.Overview')

col1, col2, col3 = st.columns(3)
col1.metric(label = '영화 평균 매출액(단위:만원)', value = round(my_movie_info['전국 매출액(만 단위)'].mean(), 2),
           delta = round(my_movie_info['전국 매출액(만 단위)'].mean() - movie_info['전국 매출액(만 단위)'].mean(), 2))
col2.metric(label = '전국 대비 서울 관객 비율(%)', value = round(((my_movie_info['서울 관객수']/my_movie_info['전국 관객수']) * 100).mean(),2),
           delta = round(((my_movie_info['서울 관객수']/my_movie_info['전국 관객수']) * 100).mean() - ((movie_info['서울 관객수']/movie_info['전국 관객수']) * 100).mean(),2))
col3.metric(label = '개봉 영화 수', value = my_movie_info['순번'].nunique(),
           delta = my_movie_info['순번'].nunique() - movie_info['순번'].nunique())


#1)극장 매출액 vs 개봉영화수의 관계 
st.subheader('극장 매출액 vs 개봉 영화수')
time_frame = st.selectbox("월별/연도별",('월','연도'))
my_dict = {'전국 매출액(조 단위)' : 'sum',
           '영화명' : 'count'}
mmi = my_movie_info.groupby(time_frame).agg(my_dict)
st.area_chart(mmi, use_container_width=True)
#2)전국 vs 서울 매출비교
st.subheader('전국vs서울 매출')
chart_data = sales.set_index('연도')
chart_data = chart_data.drop(columns='전국 관객수')
st.area_chart(chart_data)

# 2.OTT vs 극장
st.header('2.OTT vs Theater')
# 1)넷플릭스 개봉영화 수 vs 극장 동시개봉 영화 수 
st.subheader('넷플릭스 동시개봉영화 수 vs 극장 개봉 영화 수')
df2 = my_netflix
i = df2[~df2['added_year'].between(2000,2020)].index
df2 = df2.drop(i)
c = df2[df2['added_year'] == df2['release_year']]
net_i = c.groupby(['added_year'])['show_id'].count() 
movie_i = my_boxoffice.groupby(['개봉년도'])['영화명'].count()
d_frame = st.selectbox('데이터선택',('my_boxoffice','my_netflix'))

if d_frame == 'my_netflix':
    st.line_chart(net_i,use_container_width=True)
else:
    st.line_chart(movie_i,use_container_width=True)

# 3.극장현황분석
st.header('3. 극장현황분석')
audi = audi[audi['연도']<=2021]
#1) 관람료 분석
st.subheader('관람료 분석')
kpi=st.selectbox('관객수/매출액',('전국 관객수','전국 매출액'))
plt.figure(figsize=(15,10))
fig, axe1 = plt.subplots()
axe2 = axe1.twinx()
c1 = sns.lineplot(ax = axe1, data = price,x='시기',y='주말',color='green',linewidth=2.5,legend=False,palette=sns.color_palette("hls",2))
c2 = sns.lineplot(ax = axe2, data = audi, x='연도',y=kpi,color='purple',linewidth=2.5,legend=False,palette=sns.color_palette("hls",2))
axe1.legend(['관람료'],bbox_to_anchor=(1.4, 1.1),prop={'size': 10})
axe2.legend([kpi],bbox_to_anchor=(1.4, 1.0),prop={'size': 10})
axe1.set_ylabel('관람료')
if kpi == '전국 관객수':
    axe2.set_ylabel(kpi+'(억)')
else:
    axe2.set_ylabel(kpi+'(10조)')
fig


#2) 관람료 분석
st.subheader('영화 수요와 공급')
col1, col2 = st.columns(2)
with col1:
    demand = st.selectbox('수요',('전국 매출액','전국 관객수'))
with col2:
    supply = st.selectbox('공급',('극장수','전국 스크린수'))

audi1 = audi[audi['연도']<=2021]
plt.figure(figsize=(15,10))
if demand == '전국 매출액':
    if supply == '전국 스크린수':
        plt.figure(figsize=(15,10))
        fig, axe1 = plt.subplots()
        axe2 = axe1.twinx()
        sns.lineplot(ax = axe1, data = audi1,x='연도',y=demand,color='green',linewidth=2.5)
        sns.lineplot(ax = axe2, data = audi1, x='연도',y=supply,color='red',linewidth=2.5)
        axe1.legend([demand],bbox_to_anchor=(1.4, 1.2),prop={'size': 10})
        axe2.legend([supply],bbox_to_anchor=(1.4, 1.1),prop={'size': 10})
        axe1.set_ylabel('전국 매출액(10억)')
        fig
    else:
        plt.figure(figsize=(15,10))
        fig, axe1 = plt.subplots()
        axe2 = axe1.twinx()
        sns.lineplot(ax = axe1, data = audi1,x='연도',y=demand,color='green',linewidth=2.5)
        sns.lineplot(ax = axe2, data = theater_count, x='년도',y=supply,color='red',linewidth=2.5)
        axe1.set_ylabel('전국 매출액(10억)')
        axe1.legend([demand],bbox_to_anchor=(1.4, 1.2),prop={'size': 10})
        axe2.legend([supply],bbox_to_anchor=(1.4, 1.1),prop={'size': 10})
        fig
else:
    if supply == '전국 스크린수':
        plt.figure(figsize=(15,10))
        fig, axe1 = plt.subplots()
        axe2 = axe1.twinx()
        sns.lineplot(ax = axe1, data = audi1,x='연도',y=demand,color='green',linewidth=2.5)
        sns.lineplot(ax = axe2, data = audi1, x='연도',y=supply,color='red',linewidth=2.5)
        axe1.legend([demand],bbox_to_anchor=(1.4, 1.2),prop={'size': 10})
        axe2.legend([supply],bbox_to_anchor=(1.4, 1.1),prop={'size': 10})
        axe1.set_ylabel('전국 관객수(억)')
        fig
    else:
        plt.figure(figsize=(15,10))
        fig, axe1 = plt.subplots()
        axe2 = axe1.twinx()
        sns.lineplot(ax = axe1, data = audi1,x='연도',y=demand,color='green',linewidth=2.5)
        sns.lineplot(ax = axe2, data = theater_count, x='년도',y=supply,color='red',linewidth=2.5)
        axe1.legend([demand],bbox_to_anchor=(1.4, 1.2),prop={'size': 10})
        axe2.legend([supply],bbox_to_anchor=(1.4, 1.1),prop={'size': 10})
        axe1.set_ylabel('전국 관객수(억)')
        fig

#3) 좌석판매율
st.subheader('좌석판매율')
my_seat_share = seat_share.copy()
seat_sales=my_seat_share.groupby('년도')['좌석판매율'].mean()
st.area_chart(seat_sales,use_container_width=True)


# 4.타겟 분석
st.header('4.소비자 데이터')
st.subheader('소비자 데이터')
age_frame = st.selectbox("질문을 선택하세요", ("연령", '재관람 경험여부', '재관람 이유', '극장 영화 티켓 1인 가격 인식 - 비싸다','팝콘+음료세트 가격 인식 - 비싸다','영화관 관람 호감도 평점','영화관 관람 만족도 평점','OTT 관람 호감도 평점','OTT 관람 만족도 평점','추후 영화관 이용 의향','추후 OTT 이용 의향'))
ax = sns.displot(x=age_frame, data=consumer, height=7, rug=True,palette=sns.color_palette("magma", as_cmap=True))
fig = ax.figure
plt.xticks(rotation=90)
st.pyplot(fig)

# 5.솔루션 - REHIT
# 1) 재개봉 영화 분석
st.header('5.SOLUTION')
st.subheader('REHIT')
st.write('REHIT 상품을 골라보세요')
my_rehit=rehit_sort.copy()
my_rehit = my_rehit[my_rehit['연도']>=start_date.year] #개봉일까지 시간나면 맞추기
my_rehit['관객수'] = round(my_rehit['관객수']/10000,0)
my_rehit['매출액'] = round(my_rehit['매출액']/10000,0)
top = st.selectbox('TOP/5/10/ALL',('TOP5','TOP10','ALL'))
if top == 'TOP5':
    st.dataframe(rehit_sort.head(5),width=10000)
elif top == 'TOP10':
    st.dataframe(rehit_sort.head(10),width=10000)
else:
    st.dataframe(rehit_sort,width=10000)

# 2) 특수영화관 수요 분석
st.subheader('특수영화관')
ss=con[['Q37','Q38']]
ss['Q37_nom'] = ss['Q37'].value_counts(normalize=True)
ss['Q38_nom'] = ss['Q38'].value_counts(normalize=True)
col_name = {1:'없음',2:'1~2회',3:'3~4회',4:'5회 이상'}
row_name = {'Q37_nom':'특별관 관람경험','Q38_nom':'프리미엄관 관람경험'}
special = ss[['Q37_nom','Q38_nom']].dropna().T
special = special.rename(index=row_name,columns=col_name)

plt.figure(figsize=(15,10))
ax= special.plot(kind='barh',stacked=True)
fig = ax.figure #차트가 안나올 때, fig = g.figure
plt.legend(bbox_to_anchor=(1.0, 1.0),prop={'size': 10})
st.pyplot(fig)


# 6.번외 19금 영화를 즐겨보는 당신
ott_19 = df2.copy()
ott_19 = ott_19[ott_19['added_year']<=2021]
ott_19['rating'] = ott_19['rating'].str.replace('0','전체')

st.header('번외.19금 영화를 즐겨보는 당신')

col1, col2 = st.columns(2)
with col1:
    st.write('OTT 19금 콘텐츠')
    plt.figure(figsize=(15,10))
    a1=sns.countplot(data=ott_19, x='added_year', hue = 'rating',palette=sns.color_palette("hls",4))
    plt.xlabel('OTT 19금 콘텐츠')
    fig = a1.figure
    plt.legend(loc=2)
    st.pyplot(fig)
with col2:
    st.write('극장 19금 영화')
    plt.figure(figsize=(15,10))
    a2=sns.countplot(data=my_movie_info,x='연도',hue='등급',palette=sns.color_palette("hls",4))
    plt.legend(loc=2)
    plt.xlabel('극장 19금 영화')
    fig = a2.figure
    st.pyplot(fig)