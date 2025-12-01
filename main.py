import os
from dotenv import dotenv_values
import streamlit as st
from groq import Groq

# Функция для обработки стриминга ответа
def parse_groq_stream(stream):
    for chunk in stream:
        if chunk.choices:
            # Проверяем, есть ли контент в чанке
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

# Конфигурация страницы Streamlit
st.set_page_config(
    page_title="Мой Chat Buddy 🧑‍💻",
    page_icon="🤖",
    layout="centered",
)

# Загрузка переменных окружения (.env или st.secrets) 
try:
    secrets = dotenv_values(".env")  # локальный запуск
    GROQ_API_KEY = secrets["GROQ_API_KEY"]
except:
    secrets = st.secrets  # при деплое в Streamlit Cloud
    GROQ_API_KEY = secrets["GROQ_API_KEY"]

# Сохраняем ключ API в системные переменные
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Загружаем параметры персонализации
INITIAL_RESPONSE = secrets["INITIAL_RESPONSE"]
INITIAL_MSG = secrets["INITIAL_MSG"]
CHAT_CONTEXT = secrets["CHAT_CONTEXT"]

# Инициализация клиента Groq 
client = Groq()

# Инициализация истории чата
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": INITIAL_RESPONSE}
    ]

# Интерфейс приложения 
st.title("Привет, Buddy! 🤓")
st.caption("Добро пожаловать в мой AI-чат на Groq!")

# Отображение всей истории сообщений
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода пользователя 
user_prompt = st.chat_input("Напиши что-нибудь...")

# Если пользователь отправил сообщение
if user_prompt:

    # Показываем сообщение пользователя
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Добавляем сообщение в историю
    st.session_state.chat_history.append(
        {"role": "user", "content": user_prompt}
    )

    # Формируем список сообщений для модели ИИ
    messages = [
        {"role": "system", "content": CHAT_CONTEXT},
        {"role": "assistant", "content": INITIAL_MSG},
        *st.session_state.chat_history
    ]

    # Генерация ответа от модели
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # модель ИИ
            messages=messages,
            stream=True  # включаем стриминг частями
        )

        # Выводим ответ постепенно
        response = st.write_stream(parse_groq_stream(stream))

    # Добавляем ответ в историю
    st.session_state.chat_history.append(
        {"role": "assistant", "content": response}
    )
