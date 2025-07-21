import streamlit as st
import json
from datetime import datetime
import os

# Получаем user_id из URL-параметров через st.query_params (новый способ)
query_params = st.query_params
user_id = query_params.get("user_id", "guest").strip()

if not user_id:
    st.stop()

DATA_FILE = f"goal_data__{user_id}.json"

# ------------------- Функции -------------------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def calculate_day(start_date):
    today = datetime.today().date()
    delta = today - datetime.strptime(start_date, "%Y-%m-%d").date()
    return min(delta.days + 1, 90)

# ------------------- Интерфейс -------------------

st.set_page_config(page_title="Успеть за 90 дней", layout="centered")
st.title("🚀 Успеть за 90 дней")

st.markdown(f"👤 Вы вошли как: **{user_id}**")

data = load_data()

if not data:
    st.subheader("Начни с постановки цели:")
    goal = st.text_input("🎯 Введи свою цель")
    description = st.text_area("📝 Описание цели", height=100)
    if st.button("🔒 Зафиксировать цель"):
        if goal.strip() == "":
            st.warning("Цель не может быть пустой!")
        else:
            start_date = datetime.today().strftime("%Y-%m-%d")
            data = {
                "goal": goal,
                "description": description,
                "start_date": start_date,
                "completed_days": [],
                "tasks": {}
            }
            save_data(data)
            st.rerun()
else:
    day = calculate_day(data["start_date"])
    st.subheader(f"📅 Сегодня: День {day} из 90")
    st.progress(day / 90)

    st.markdown(f"**🎯 Цель:** {data['goal']}")
    if data["description"]:
        st.markdown(f"**📝 Описание:** {data['description']}")

    today_str = datetime.today().strftime("%Y-%m-%d")
    today_tasks = data["tasks"].get(today_str, [])

    with st.form("tasks_form"):
        new_task = st.text_input("Добавь задачу на сегодня:")
        if st.form_submit_button("➕ Добавить"):
            if new_task.strip():
                today_tasks.append(new_task)
                data["tasks"][today_str] = today_tasks
                save_data(data)
                st.rerun()

    st.markdown("### 📋 Задачи на сегодня:")
    if today_tasks:
        for i, task in enumerate(today_tasks):
            col1, col2 = st.columns([0.8, 0.2])
            col1.write(f"- {task}")
            if col2.button("✅", key=f"done_{i}"):
                today_tasks.pop(i)
                data["tasks"][today_str] = today_tasks
                save_data(data)
                st.rerun()
    else:
        st.info("Нет задач на сегодня")

    if today_str not in data["completed_days"]:
        if st.button("☑️ Отметить день как выполненный"):
            data["completed_days"].append(today_str)
            save_data(data)
            st.success("День засчитан!")
            st.rerun()
    else:
        st.success("✅ Этот день уже отмечен.")

    with st.expander("⚙️ Настройки"):
        if st.button("🗑️ Сбросить данные пользователя"):
            os.remove(DATA_FILE)
            st.rerun()
