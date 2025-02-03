import requests
import sqlite3
import streamlit as st
from bs4 import BeautifulSoup

def fetch_and_store_posts():
    conn = sqlite3.connect('1.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS posts (user_id INTEGER, post_id INTEGER, title TEXT, body TEXT)")
    user_ids = range(1, 11)
    for user_id in user_ids:
        url = f"https://jsonplaceholder.typicode.com/posts?userId={user_id}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for post in data:
                post_id = post['id']
                title = post['title']
                body = post['body']
                cursor.execute("INSERT INTO posts (user_id, post_id, title, body) VALUES (?, ?, ?, ?)", (user_id, post_id, title, body))
    conn.commit()
    conn.close()

def scrape_and_store_news():
    conn = sqlite3.connect('1.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS news")
    cursor.execute("CREATE TABLE IF NOT EXISTS news (title TEXT, body TEXT)")
    response = requests.get("https://digiato.com/")
    soup = BeautifulSoup(response.text, 'html.parser')
    news = soup.find_all("div", class_="rowCard homeTodayItem")
    for item in news:
        title = item.find("a", class_="rowCard__title").text.strip()
        body = item.find("p", class_="rowCard__description").text.strip()
        cursor.execute("INSERT INTO news (title, body) VALUES (?, ?)", (title, body))
    conn.commit()
    conn.close()

def display_tech_news():
    conn = sqlite3.connect('1.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news")
    data = cursor.fetchall()
    conn.close()
    st.header("Tech News from Digiato")
    for row in data:
        title, body = row
        with st.container():
            st.subheader(title)
            st.write(body)
            st.markdown('<hr style="border: 1px solid red">', unsafe_allow_html=True)
            st.markdown('<hr style="border: 1px solid blue">', unsafe_allow_html=True)

def display_user_posts():
    conn = sqlite3.connect('1.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    data = cursor.fetchall()
    conn.close()
    st.header("User Posts from JSONPlaceholder")
    for row in data:
        user_id, post_id, title, body = row
        with st.container():
            st.write(f"**User ID:** {user_id}")
            st.write(f"**Post ID:** {post_id}")
            st.write(f"**Title:** {title}")
            st.write(f"**Body:** {body}")
            st.markdown('<hr style="border: 1px solid red">', unsafe_allow_html=True)
            st.markdown('<hr style="border: 1px solid blue">', unsafe_allow_html=True)

def main():
    fetch_and_store_posts()
    scrape_and_store_news()
    st.title("Database Viewer")
    if st.button("Tech News (Digiato)"):
        display_tech_news()
    if st.button("User Posts (JSONPlaceholder)"):
        display_user_posts()

if __name__ == "__main__":
    main()

#MEHRDAD