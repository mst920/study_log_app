import streamlit as st
import os
import json
from datetime import date
import matplotlib.pyplot as plt
import japanize_matplotlib

DATA_PATH = 'history.json'
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
    return record.get('study_hours', 0.0)

def add_study_hours():
    hours = st.session_state['study_hours_input']
    upsert_today_hours(study_hours = hours)
    st.session_state['study_hours_input'] = 0.0

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

study_hours = st.number_input(
    '勉強時間を入力してください',
    format = "%.1f",
    key = 'study_hours_input'
)

if st.button('追加する', on_click = add_study_hours):
    st.success('追加しました')

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
    value = 3
)

memo = st.text_area(
    '振り返りメモ(任意)',
    placeholder = '気になることがあれば'
)

if st.button('保存する'):
    upsert_today_hours(satisfaction = satisfaction, memo = memo)
    st.success('保存が完了しました')

st.divider()
#===================
# サマリー
#===================
history = load_history()

dates = [r['record_id'] for r in history]
study_hours_list = [r.get('study_hours', 0.0) for r in history]
satisfaction_list = [r.get('satisfaction') for r in history] 

st.subheader('勉強時間の推移')

fig, ax = plt.subplots()

ax.plot(dates, study_hours_list, marker = 'o')
ax.set_xlabel('日付')
ax.set_ylabel('勉強時間 (時間)')
ax.set_title('日別 勉強時間')

ax.tick_params(axis = 'x', rotation = 45)

st.pyplot(fig)

st.subheader("満足度の推移")

fig2, ax2 = plt.subplots()

ax2.plot(dates, satisfaction_list, marker="o")
ax2.set_xlabel("日付")
ax2.set_ylabel("満足度")
ax2.set_ylim(1, 5)
ax2.set_title("日別 満足度")

ax2.tick_params(axis="x", rotation=45)

st.pyplot(fig2)
