# 勉強満足度振り返りアプリ

## 概要
日々の勉強時間と満足度を記録し、可視化する個人用アプリです。

## 機能

- 勉強時間の記録（1日に複数回加算可）
- 満足度の記録（1〜5）
- 直近7日間の勉強時間・満足度グラフ表示
- 今週のサマリー表示
  - 今週の勉強時間（合計）
  - 今週の平均満足度（入力がある日のみ）

## 使用技術
- Python
- Streamlit
- matplotlib

## データ構造

- record_id: "YYYY-MM-DD"
- study_hours: float
- satisfaction: int | None
- memo: str | None

## v2で追加した改善
- 日付順にデータをソートして表示
- データが少ない場合はグラフを表示しないガードを追加
- 満足度が未入力の日はグラフに含めない設計

## v3: 週サマリー

- record_id は "YYYY-MM-DD" の文字列
- date.fromisoformat() で date に変換
- isocalendar() で (year, week) を取得
- 今週のデータだけ集計して表示
