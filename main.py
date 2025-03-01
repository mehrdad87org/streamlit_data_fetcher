import requests
import sqlite3
import streamlit as st
from bs4 import BeautifulSoup
import os
import atexit
import time

def delete_database_on_exit():
    if os.path.exists('data.db'):
        os.remove('data.db')

atexit.register(delete_database_on_exit)

# Custom CSS with animations
def load_css():
    st.markdown("""
    <style>
        /* Main container styling */
        .main {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* App title animation */
        .title-animation {
            background: linear-gradient(90deg, #ff4b4b, #ff9d00, #4b8eff);
            background-size: 600% 600%;
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            animation: gradient 6s ease infinite;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        @keyframes gradient {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        
        /* Button styling */
        .stButton > button {
            width: 100%;
            border-radius: 20px;
            font-weight: bold;
            border: none;
            padding: 0.5rem 1rem;
            background: linear-gradient(90deg, #4b8eff, #2774f5);
            color: white;
            transition: all 0.3s ease;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 7px 14px rgba(0, 0, 0, 0.15);
        }
        
        .stButton > button:active {
            transform: translateY(1px);
        }
        
        /* News and post containers */
        .news-container, .post-container {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            opacity: 0;
            animation: fadeIn 0.5s ease forwards;
            border-left: 5px solid #4b8eff;
        }
        
        .news-container:hover, .post-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }
        
        /* News title */
        .news-title {
            color: #2774f5;
            font-size: 1.3rem;
            margin-bottom: 0.5rem;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 0.5rem;
        }
        
        /* News body */
        .news-body {
            color: #555;
            line-height: 1.6;
        }
        
        /* Post styling */
        .post-meta {
            font-size: 0.9rem;
            color: #888;
            margin-bottom: 0.5rem;
        }
        
        .post-title {
            color: #333;
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .post-body {
            color: #555;
            line-height: 1.5;
        }
        
        /* Loading animation */
        .loading {
            display: inline-block;
            width: 50px;
            height: 50px;
            border: 5px solid rgba(75, 142, 255, 0.2);
            border-radius: 50%;
            border-top-color: #4b8eff;
            animation: spin 1s ease-in-out infinite;
            margin: 2rem auto;
        }
        
        @keyframes spin {
            to {transform: rotate(360deg);}
        }
        
        /* Custom separator */
        .separator {
            height: 3px;
            background: linear-gradient(90deg, #ff4b4b, #ff9d00, #4b8eff);
            margin: 1.5rem 0;
            border-radius: 3px;
        }
        
        /* Section headers */
        .section-header {
            background: linear-gradient(90deg, #4b8eff, #2774f5);
            color: white;
            padding: 0.8rem 1.5rem;
            border-radius: 30px;
            margin: 1.5rem 0;
            font-weight: bold;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% {box-shadow: 0 0 0 0 rgba(75, 142, 255, 0.7);}
            70% {box-shadow: 0 0 0 10px rgba(75, 142, 255, 0);}
            100% {box-shadow: 0 0 0 0 rgba(75, 142, 255, 0);}
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 1.5rem;
            color: #888;
            font-size: 0.9rem;
            margin-top: 3rem;
            border-top: 1px solid #eee;
        }
    </style>
    """, unsafe_allow_html=True)

def fetch_and_store_posts():
    conn = sqlite3.connect('data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS posts (user_id INTEGER, post_id INTEGER, title TEXT, body TEXT)")
    
    # Check if we already have data
    cursor.execute("SELECT COUNT(*) FROM posts")
    count = cursor.fetchone()[0]
    
    if count == 0:
        with st.spinner('Fetching posts from JSONPlaceholder...'):
            st.markdown('<div class="loading"></div>', unsafe_allow_html=True)
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
                        cursor.execute("INSERT INTO posts (user_id, post_id, title, body) VALUES (?, ?, ?, ?)", 
                                      (user_id, post_id, title, body))
            conn.commit()
            time.sleep(1)  # For animation effect
    
    conn.close()

def scrape_and_store_news():
    conn = sqlite3.connect('data.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        cursor.execute("CREATE TABLE IF NOT EXISTS news (title TEXT, body TEXT)")
        
        with st.spinner('Scraping tech news from Digiato...'):
            st.markdown('<div class="loading"></div>', unsafe_allow_html=True)
            try:
                response = requests.get("https://digiato.com/", timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                news = soup.find_all("div", class_="rowCard homeTodayItem")
                for item in news:
                    title = item.find("a", class_="rowCard__title").text.strip()
                    body = item.find("p", class_="rowCard__description").text.strip()
                    cursor.execute("INSERT INTO news (title, body) VALUES (?, ?)", (title, body))
                conn.commit()
                time.sleep(1)  # For animation effect
            except Exception as e:
                st.error(f"Error scraping news: {e}")
    
    conn.close()

def display_tech_news():
    conn = sqlite3.connect('data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news")
    data = cursor.fetchall()
    conn.close()
    
    st.markdown('<div class="section-header">Tech News from Digiato</div>', unsafe_allow_html=True)
    
    if not data:
        st.warning("No news data available. Try refreshing the data.")
        return
    
    for i, row in enumerate(data):
        title, body = row
        # Add delay for staggered animation
        delay = i * 0.1
        st.markdown(f"""
        <div class="news-container" style="animation-delay: {delay}s;">
            <div class="news-title">{title}</div>
            <div class="news-body">{body}</div>
        </div>
        <div class="separator"></div>
        """, unsafe_allow_html=True)

def display_user_posts():
    conn = sqlite3.connect('data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    data = cursor.fetchall()
    conn.close()
    
    st.markdown('<div class="section-header">User Posts from JSONPlaceholder</div>', unsafe_allow_html=True)
    
    if not data:
        st.warning("No post data available. Try refreshing the data.")
        return
    
    for i, row in enumerate(data):
        user_id, post_id, title, body = row
        # Add delay for staggered animation
        delay = i * 0.05
        st.markdown(f"""
        <div class="post-container" style="animation-delay: {delay}s;">
            <div class="post-meta">User ID: {user_id} • Post ID: {post_id}</div>
            <div class="post-title">{title}</div>
            <div class="post-body">{body}</div>
        </div>
        <div class="separator"></div>
        """, unsafe_allow_html=True)

def main():
    load_css()
    
    st.markdown('<div class="title-animation"><h1>Animated Database Viewer</h1></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Load Tech News"):
            scrape_and_store_news()
            display_tech_news()
    
    with col2:
        if st.button("Load User Posts"):
            fetch_and_store_posts()
            display_user_posts()
    
    # Add a refresh button
    if st.button("Refresh All Data"):
        # Delete existing database
        if os.path.exists('data.db'):
            os.remove('data.db')
        fetch_and_store_posts()
        scrape_and_store_news()
        st.success("Data refreshed successfully!")
    
    # Footer
    st.markdown("""
    <div class="footer">
        Created with ❤️ using Streamlit • Data sources: JSONPlaceholder API & Digiato.com
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
