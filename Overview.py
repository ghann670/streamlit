import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Overview", page_icon="🏢", layout="wide")

# Page title
st.title("🏢 Organization Overview")
st.header("Trial Organizations")

# 1. users.xlsx의 'date' 시트만 불러오기
excel_file = "users.xlsx"
df = pd.read_excel(excel_file, sheet_name="date")

# 2. status가 'trial'인 기업만 필터
trial_df = df[df['status'].str.strip().str.lower() == 'trial'].copy()

# 3. 날짜 컬럼 변환
trial_df['trial_start_date'] = pd.to_datetime(trial_df['trial_start_date']).dt.strftime('%Y-%m-%d')
trial_df['trial_end_date'] = pd.to_datetime(trial_df['trial_end_date'])

# 4. trial end date 표시 설정
trial_df['trial_end_date_display'] = trial_df['trial_end_date'].dt.strftime('%Y-%m-%d')
trial_df.loc[pd.isnull(trial_df['trial_end_date']), 'trial_end_date_display'] = 'Ongoing'

# 5. 정렬: trial end date 오름차순, null은 마지막
trial_df['trial_end_date_sort'] = trial_df['trial_end_date'].fillna(pd.Timestamp.max)
trial_df = trial_df.sort_values('trial_end_date_sort')

# 6. Trial Duration 설정 (상태 이모지 포함)
def get_status_emoji(end_date):
    if pd.isna(end_date):
        return '🟢'  # 초록색 (Ongoing)
    
    today = pd.Timestamp.now()
    days_remaining = (end_date - today).days
    
    if days_remaining < 0:
        return '🔴'  # 빨간색 (종료됨)
    elif days_remaining <= 7:
        return '🟡'  # 노란색 (7일 이내)
    else:
        return '🟢'  # 초록색 (7일 이상)

trial_df['Status'] = trial_df['trial_end_date'].apply(get_status_emoji)
trial_df['Trial Duration'] = trial_df['Status'] + ' ' + trial_df['trial_start_date'] + ' ~ ' + trial_df['trial_end_date_display']

# 표에 표시할 컬럼만 추출 (기업명, 기간)
show_df = trial_df[['organization', 'Trial Duration']].rename(columns={'organization': 'Organization'})

# 각 기업명을 클릭 가능한 링크로 만들기
def make_clickable(org_name):
    return f'<a href="Usage_Summary?selected_org={org_name}" target="_self">{org_name}</a>'

show_df['Organization'] = show_df['Organization'].apply(make_clickable)

# HTML로 링크가 작동하는 데이터프레임 표시
st.write("Click on the organization name to view detailed usage summary:")

# CSS로 테이블 스타일 지정
table_style = """
<style>
    table {
        width: 100%;
    }
    th {
        text-align: left !important;
    }
</style>
"""

# 테이블 HTML과 스타일 함께 표시
st.markdown(
    table_style + show_df.to_html(escape=False, index=False),
    unsafe_allow_html=True) 