import streamlit as st
import os
import json
from datetime import date
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams

# 日本語フォント設定（Cloud対応）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "fonts", "IPAexGothic.ttf")

if os.path.exists(FONT_PATH):
    font_manager.fontManager.addfont(FONT_PATH)
    rcParams["font.family"] = "IPAexGothic"
else:
    print("Japanese font not found:", FONT_PATH)


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
    ax.set_xlabel('日付')
    ax.set_ylabel('勉強時間 (時間)')
    ax.set_title('日別 勉強時間')

    ax.tick_params(axis = 'x', rotation = 45)

    st.pyplot(fig)

    st.subheader("満足度の推移")

    if len(satisfaction_list) < 2:
         st.info("満足度のデータがまだ十分ではありません。")
    else:
        sat_dates, sat_values = zip(*satisfaction_list)
        fig2, ax2 = plt.subplots()

        ax2.plot(sat_dates, sat_values, marker="o")
        ax2.set_xlabel("日付")
        ax2.set_ylabel("満足度")
        ax2.set_ylim(1, 5)
        ax2.set_title("日別 満足度")

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