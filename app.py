import streamlit as st
import os
import json
from datetime import date
import matplotlib.pyplot as plt

DATA_PATH = 'history.json'

if 'study_hours_h' not in st.session_state:
    st.session_state['study_hours_h'] = 0
if 'study_hours_m' not in st.session_state:
    st.session_state['study_hours_m'] = 0
if 'satisfaction_input' not in st.session_state:
    st.session_state['satisfaction_input'] = 3
if 'memo_input' not in st.session_state:
    st.session_state['memo_input'] = ''
 
#===================
# 関数
#===================
def load_history(path = DATA_PATH):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding = 'utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_history(data, path = DATA_PATH):
    with open(path, 'w', encoding = 'utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2) 

def get_today_id():
    return date.today().isoformat()

def find_today_record(history, record_id):
    for record in history:
        if record['record_id'] == record_id:
            return record
    return None

def upsert_today_hours(study_hours = None, satisfaction = None, memo = None):
    history = load_history()
    today_id = get_today_id()

    record = find_today_record(history, today_id)

    if record is None:
        record = {
            'record_id': today_id,
            'study_hours': study_hours if study_hours is not None else 0.0,
            'satisfaction': satisfaction,
            'memo': memo
        }
        history.append(record)
    else:
        if study_hours is not None:
            record['study_hours'] += study_hours
        if satisfaction is not None:
            record['satisfaction'] = satisfaction
        if memo is not None:
            record['memo'] = memo
    save_history(history)

def total_study_hours():
    history = load_history()
    today_id = get_today_id()

    record = find_today_record(history, today_id)
    if record is None:
        return 0.0
    return round(record.get('study_hours', 0.0), 1)

def add_study_hours():
    hours = st.session_state['study_hours_h']
    minutes = st.session_state['study_hours_m']

    study_time = hours + minutes / 60

    if study_time <= 0:
        st.session_state['message_study'] = '時間か分を選択してください'
        return

    upsert_today_hours(study_hours = study_time)

    st.session_state['study_hours_h'] = 0
    st.session_state['study_hours_m'] = 0

    st.session_state['message_study'] = '保存しました'
    
def input_summary():
    satisfaction = st.session_state['satisfaction_input']
    memo = st.session_state['memo_input']

    upsert_today_hours(satisfaction = satisfaction, memo = memo)

    st.session_state['satisfaction_input'] = 3
    st.session_state['memo_input'] = ''

    st.session_state['message_summary'] = '保存されました'

#===================
# タイトル
#===================
st.title('勉強満足度振り返りアプリ')
st.caption('勉強時間とその満足度を日々計測し、振り返れるアプリです')

st.divider()
#===================
# 勉強時間の更新
#===================
st.subheader('勉強時間の入力')

col1, col2 = st.columns(2)

with col1:
    study_hours = st.selectbox(
            '時間',
        options = [0, 1, 2, 3, 4],
        key = 'study_hours_h'
        )

with col2:
    study_minutes = st.selectbox(
            '分',
            options = [0, 10, 20, 30, 40, 50],
            key = 'study_hours_m'
        )
    
st.button('追加する', on_click = add_study_hours)
if 'message_study' in st.session_state:
    st.warning(st.session_state['message_study'])
    del st.session_state['message_study']

total = total_study_hours()
st.metric(
    '今日の合計時間',
    total
)

st.divider()
#===================
# 今日の振り返り
#===================
st.subheader('今日の振り返り')

satisfaction = st.slider(
    '満足度',
    min_value = 1,
    max_value = 5,
    value = 3,
    key = 'satisfaction_input'
)

memo = st.text_area(
    '振り返りメモ(任意)',
    key = 'memo_input',
    placeholder = '気になることがあれば'
)

st.button('保存する', on_click = input_summary)

if 'message_summary' in st.session_state:
    st.success(st.session_state['message_summary'])
    del st.session_state['message_summary']

st.divider()
#===================
# サマリー
#===================
history = load_history()

if len(history) < 2:
    st.info('まだデータが十分ではありません。データが溜まると表示されます')
else:
    history = sorted(history, key= lambda r: r['record_id'])
    recent_history = history[-7:]

    dates = [r['record_id'] for r in recent_history]
    study_hours_list = [r.get('study_hours', 0.0) for r in recent_history]
    satisfaction_list = [
        (r['record_id'], r['satisfaction'])
        for r in recent_history
        if r.get('satisfaction') is not None
    ] 

    st.subheader('勉強時間の推移')

    fig, ax = plt.subplots()

    ax.plot(dates, study_hours_list, marker = 'o')
    ax.set_xlabel('Date')
    ax.set_ylabel('Hours')
    ax.set_title('Study Hours (Last 7 Days)')

    ax.tick_params(axis = 'x', rotation = 45)

    st.pyplot(fig)

    st.subheader("満足度の推移")

    if len(satisfaction_list) < 2:
         st.info("満足度のデータがまだ十分ではありません。")
    else:
        sat_dates, sat_values = zip(*satisfaction_list)
        fig2, ax2 = plt.subplots()

        ax2.plot(sat_dates, sat_values, marker="o")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Satisfaction")
        ax2.set_ylim(0.5, 5.5)
        ax2.set_title("Daily Satisfaction")

        ax2.tick_params(axis="x", rotation=45)

        st.pyplot(fig2)

#===================
# 週の振り返り
#===================
today = date.today()
current_year, current_week, _ = today.isocalendar()

weekly_records = []

for r in history:
    d = date.fromisoformat(r['record_id'])
    y, w, _ = d.isocalendar()

    if (y, w) == (current_year, current_week):
        weekly_records.append(r)

weekly_hours = sum(
    r.get('study_hours', 0.0)
    for r in weekly_records
)

weekly_satisfaction = [
    r['satisfaction']
    for r in weekly_records
    if r['satisfaction'] is not None
]

if weekly_satisfaction:
    avg_satisfaction = sum(weekly_satisfaction) / len(weekly_satisfaction)
else:
    avg_satisfaction = None

st.subheader('今週のサマリー')

st.metric('今週の勉強時間(合計)', f'{weekly_hours:.1f}時間')

if avg_satisfaction is not None:
    st.metric('今週の平均満足度', f'{avg_satisfaction:.1f}')
else:
    st.info('今週の満足度データはありません')