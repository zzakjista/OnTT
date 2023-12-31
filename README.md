# 🎬 OnTT
코로나 이후 붕괴하는 극장 산업 회복을 위한 데이터 분석 프로젝트입니다.
전례없는 전염병으로 인해 오프라인 산업과 소비자의 단절이 극심해져 
의식주 뿐만이 아닌 여가와 문화 산업 등 극심한 타격을 입었습니다.

해당 프로젝트는 '엔데믹 이후 오프라인 극장 산업'의 방향성에 대한 통찰을 담고 있습니다.
극장가의 주변 환경에 대한 분석부터, 경쟁적 관계에 대한 분석, 본 산업에 대한 분석까지
다양한 데이터를 활용하여 다양한 관점에서 '오프라인 극장 산업의 부활'을 위한 방법을 제시합니다.

# 📑 Dev description

## data
사용한 데이터의 출처는 다음과 같습니다.
- 영화진흥위원회 API
- 넷플릭스
- 웹(티켓 가격 추이 분석을 위해)

1. 역대 개봉 영화(1971~2022) 
   - 5000여 건의 역대 개봉 영화
   - movie_info_1971_2022_clean.csv
2. 연도별 박스오피스(2004~2022)
   - 2000여 건의 박스오피스 등재 영화
   - boxoffice.csv
3. 지역별 극장 현황(2016~2022)
   - 연도별 각 지역의 극장 수
   - theater.csv
4. 연도별 좌석점유율(2016~2022)
   - 각 영화의 좌석점유율 및 매출액 등의 지표
   - seat_share.csv
5. 넷플릭스 콘텐츠 현황(2008~2021)
   - OTT 서비스에서 배포된 영화
   - netflix.csv
6. 영화 소비자 분석(2018)
   - 2018년 영화 소비자 행태 조사
   - consumer.csv
7. CGV 티겟가격 추이(2001~2021)
   - CGV_Ticket_price.csv
  
※ 위 데이터들은 모두 1차적으로 전처리가 되어있는 상태이며
본 레포지토리에는 분석에 필수적으로 필요한 전처리만 포함되어있습니다.

## feature engineering
분석할 데이터들에 대해 전처리를 수행하고 새로운 feature를 만드는 베이스 코드를 포함합니다

## OnTT_visualization
Streamlit을 통해 localhost에서 시각화 자료를 볼 수 있습니다.
- 주요 콘텐츠
  - Overview
  - OTT vs Theater
  - 극장현황분석
  - 소비자 데이터
  - SOLUTION
  - 번외

```python
pip install streamlit
```

```
streamlit run OnTT_visualization.py
```

# contents
시각화 자료를 분석하고 문제점을 발견해 솔루션을 제시하는 과정이 포함되어있습니다.
