import requests
import sqlite3
import streamlit as st
from bs4 import BeautifulSoup
import os
import atexit
import time
import signal

# Initialize database with proper table structure and cleanup on exit
def init_database():
    # Register cleanup function
    atexit.register(cleanup_database)
    
    conn = sqlite3.connect('data.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Create news table if it doesn't exist with proper columns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT,
        source_url TEXT,
        category TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create index for better search performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_category ON news(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_title ON news(title)")
    
    conn.commit()
    conn.close()

# Cleanup database when app exits
def cleanup_database():
    try:
        if os.path.exists('data.db'):
            os.remove('data.db')
            print("Database cleaned up successfully")
    except Exception as e:
        print(f"Error cleaning up database: {e}")

# Custom CSS with animations and neon theme
def load_css():
    st.markdown("""
    <style>
        /* Main container styling */
        .main {
            background-color: #0a0a12;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #e6f1ff;
        }
        
        /* App title animation - Neon effect */
        .title-animation {
            color: #fff;
            text-align: center;
            text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px #0073e6, 0 0 20px #0073e6, 0 0 25px #0073e6, 0 0 30px #0073e6, 0 0 35px #0073e6;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            animation: flicker 1.5s infinite alternate;
            font-size: 2.5rem;
            border: 2px solid #4b8eff;
            box-shadow: 0 0 10px #4b8eff, inset 0 0 10px #4b8eff;
        }
        
        @keyframes flicker {
            0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {
                text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px #0073e6, 0 0 20px #0073e6, 0 0 25px #0073e6, 0 0 30px #0073e6, 0 0 35px #0073e6;
                box-shadow: 0 0 10px #4b8eff, inset 0 0 10px #4b8eff;
            }
            20%, 24%, 55% {
                text-shadow: none;
                box-shadow: none;
            }
        }
        
        /* Button styling with neon effect */
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
            box-shadow: 0 0 10px #4b8eff;
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 0 20px #4b8eff;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
        }
        
        .stButton > button:active {
            transform: translateY(1px);
        }
        
        /* News and post containers - deep dark blue with neon border */
        .news-container {
            background: #0a192f !important;
            color: #e6f1ff !important;
            padding: 1.5rem !important;
            border-radius: 10px !important;
            margin-bottom: 1.5rem !important;
            box-shadow: 0 0 15px rgba(100, 255, 218, 0.2) !important;
            transition: all 0.3s ease !important;
            border-left: 5px solid #64ffda !important;
            position: relative;
            overflow: hidden;
        }
        
        .news-container:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 0 25px rgba(100, 255, 218, 0.4) !important;
        }
        
        /* Glow effect on hover */
        .news-container::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            z-index: -1;
            background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000);
            background-size: 400%;
            border-radius: 10px;
            opacity: 0;
            transition: 0.5s;
            animation: animate 20s linear infinite;
        }
        
        .news-container:hover::before {
            opacity: 0.2;
            filter: blur(5px);
        }
        
        @keyframes animate {
            0% { background-position: 0 0; }
            50% { background-position: 400% 0; }
            100% { background-position: 0 0; }
        }
        
        /* News title with neon text */
        .news-title {
            color: #64ffda !important;
            font-size: 1.3rem !important;
            margin-bottom: 0.5rem !important;
            border-bottom: 2px solid #172a45 !important;
            padding-bottom: 0.5rem !important;
            text-shadow: 0 0 5px rgba(100, 255, 218, 0.5);
        }
        
        /* News body */
        .news-body {
            color: #8892b0 !important;
            line-height: 1.6 !important;
            margin-bottom: 1rem !important;
        }
        
        /* Category tag with neon effect */
        .category-tag {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.8rem;
            background: #172a45 !important;
            color: #64ffda !important;
            margin-left: 10px;
            border: 1px solid #64ffda !important;
            text-shadow: 0 0 5px rgba(100, 255, 218, 0.5);
            box-shadow: 0 0 5px rgba(100, 255, 218, 0.3);
        }
        
        /* News link button with neon effect */
        .news-link-btn {
            background: transparent !important;
            border: 1px solid #64ffda !important;
            color: #64ffda !important;
            padding: 0.5rem 1rem !important;
            border-radius: 5px !important;
            font-weight: bold !important;
            transition: all 0.3s ease !important;
            text-decoration: none !important;
            display: inline-block !important;
            margin-top: 10px !important;
            text-shadow: 0 0 5px rgba(100, 255, 218, 0.5);
            box-shadow: 0 0 5px rgba(100, 255, 218, 0.3);
        }
        
        .news-link-btn:hover {
            background: #64ffda !important;
            color: #0a192f !important;
            text-decoration: none !important;
            box-shadow: 0 0 15px rgba(100, 255, 218, 0.7);
            text-shadow: none;
        }
        
        /* Loading animation */
        .loading {
            display: inline-block;
            width: 50px;
            height: 50px;
            border: 5px solid rgba(100, 255, 218, 0.2);
            border-radius: 50%;
            border-top-color: #64ffda;
            animation: spin 1s ease-in-out infinite;
            margin: 2rem auto;
            box-shadow: 0 0 10px rgba(100, 255, 218, 0.5);
        }
        
        @keyframes spin {
            to {transform: rotate(360deg);}
        }
        
        /* Section headers with neon effect */
        .section-header {
            background: linear-gradient(90deg, #0a192f, #172a45);
            color: #64ffda;
            padding: 0.8rem 1.5rem;
            border-radius: 30px;
            margin: 1.5rem 0;
            font-weight: bold;
            text-align: center;
            box-shadow: 0 0 15px rgba(100, 255, 218, 0.3);
            text-shadow: 0 0 5px rgba(100, 255, 218, 0.5);
            border: 1px solid #64ffda;
        }
        
        /* Footer with neon effect */
        .footer {
            text-align: center;
            padding: 1.5rem;
            color: #888;
            font-size: 0.9rem;
            margin-top: 3rem;
            border-top: 1px solid #333;
            text-shadow: 0 0 5px rgba(136, 136, 136, 0.5);
        }
        
        /* Filter select box with neon effect */
        .stSelectbox > div > div {
            background-color: #0a192f;
            color: #64ffda;
            border: 1px solid #64ffda;
            border-radius: 5px;
            box-shadow: 0 0 5px rgba(100, 255, 218, 0.3);
        }
        
        .stSelectbox > label {
            color: #64ffda !important;
            text-shadow: 0 0 5px rgba(100, 255, 218, 0.3);
        }
        
        /* Pagination container */
        .pagination-container {
            display: flex;
            justify-content: center;
            margin: 2rem 0;
            gap: 10px;
        }
        
        .pagination-btn {
            background: #0a192f !important;
            color: #64ffda !important;
            border: 1px solid #64ffda !important;
            border-radius: 5px !important;
            padding: 0.5rem 1rem !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            text-shadow: 0 0 5px rgba(100, 255, 218, 0.3);
            box-shadow: 0 0 5px rgba(100, 255, 218, 0.3);
        }
        
        .pagination-btn:hover {
            background: #64ffda !important;
            color: #0a192f !important;
            box-shadow: 0 0 15px rgba(100, 255, 218, 0.7);
            text-shadow: none;
        }
        
        .pagination-btn.active {
            background: #64ffda !important;
            color: #0a192f !important;
            font-weight: bold !important;
            box-shadow: 0 0 15px rgba(100, 255, 218, 0.7);
        }
        
        .pagination-btn.disabled {
            opacity: 0.5 !important;
            cursor: not-allowed !important;
            box-shadow: none !important;
        }
        
        /* Social icons container */
        .social-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 2rem 0;
            flex-wrap: wrap;
        }
        
        /* Social icons with neon glow effect */
        .social-icon {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        }
        
        .social-icon img {
            width: 40px;
            height: 40px;
            transition: all 0.3s ease;
            filter: brightness(0.8);
        }
        
        .social-icon:hover {
            transform: translateY(-5px);
        }
        
        .social-icon:hover img {
            filter: brightness(1.2);
        }
        
        /* Individual social icon effects */
        .telegram {
            background: rgba(0, 136, 204, 0.1);
            border: 1px solid #0088cc;
        }
        
        .telegram:hover {
            box-shadow: 0 0 20px #0088cc;
        }
        
        .whatsapp {
            background: rgba(37, 211, 102, 0.1);
            border: 1px solid #25d366;
        }
        
        .whatsapp:hover {
            box-shadow: 0 0 20px #25d366;
        }
        
        .github {
            background: rgba(24, 23, 23, 0.1);
            border: 1px solid #181717;
        }
        
        .github:hover {
            box-shadow: 0 0 20px #181717;
        }
        
        .email {
            background: rgba(219, 68, 55, 0.1);
            border: 1px solid #db4437;
        }
        
        .email:hover {
            box-shadow: 0 0 20px #db4437;
        }
        
        .instagram {
            background: rgba(193, 53, 132, 0.1);
            border: 1px solid #c13584;
        }
        
        .instagram:hover {
            box-shadow: 0 0 20px #c13584;
        }
        
        .linkedin {
            background: rgba(0, 119, 181, 0.1);
            border: 1px solid #0077b5;
        }
        
        .linkedin:hover {
            box-shadow: 0 0 20px #0077b5;
        }
        
        /* Contact section */
        .contact-section {
            background: rgba(10, 25, 47, 0.7);
            padding: 2rem;
            border-radius: 10px;
            margin: 2rem 0;
            border: 1px solid #64ffda;
            box-shadow: 0 0 15px rgba(100, 255, 218, 0.3);
        }
        
        .contact-title {
            color: #64ffda;
            text-align: center;
            margin-bottom: 1.5rem;
            text-shadow: 0 0 5px rgba(100, 255, 218, 0.5);
        }
        
        /* Emoji styling */
        .emoji {
            font-size: 1.5rem;
            margin: 0 5px;
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .social-icon {
                width: 50px;
                height: 50px;
            }
            
            .social-icon img {
                width: 30px;
                height: 30px;
            }
            
            .title-animation {
                font-size: 1.8rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def scrape_and_store_news():
    # Initialize database first
    init_database()
    
    conn = sqlite3.connect('data.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Clear existing news data
    cursor.execute("DELETE FROM news")
    conn.commit()
    
    with st.spinner('در حال دریافت اخبار از دیجیاتو...'):
        st.markdown('<div class="loading"></div>', unsafe_allow_html=True)
        
        # Categories to scrape
        categories = [
            {"url": "https://digiato.com/topic/tech", "name": "تکنولوژی"},
            {"url": "https://digiato.com/topic/car", "name": "خودرو"},
            {"url": "https://digiato.com/topic/science", "name": "علمی"},
            {"url": "https://digiato.com/topic/business", "name": "کسب و کار"}
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for category in categories:
            try:
                st.info(f'دریافت اخبار {category["name"]}...')
                response = requests.get(category["url"], headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Try different selectors for finding news items
                    articles = soup.select("article") or soup.select(".post") or soup.select(".rowCard") or soup.select(".post-list .post-item")
                    
                    for article in articles:
                        # Extract title
                        title_elem = (
                            article.select_one("h2 a") or 
                            article.select_one("h3 a") or
                            article.select_one(".post-title a") or
                            article.select_one("a[class*='title']") or
                            article.select_one(".entry-title a")
                        )
                        
                        # Extract body
                        body_elem = (
                            article.select_one("p[class*='description']") or
                            article.select_one("p[class*='excerpt']") or
                            article.select_one(".post-excerpt") or
                            article.select_one(".entry-content p") or
                            article.select_one("p")
                        )
                        
                        if title_elem and body_elem:
                            title = title_elem.text.strip()
                            body = body_elem.text.strip()
                            
                            # Get URL
                            if title_elem.has_attr("href"):
                                source_url = title_elem["href"]
                            else:
                                source_url = title_elem.parent.get("href") if title_elem.parent.name == "a" else None
                            
                            # Make URL absolute if needed
                            if source_url and not source_url.startswith(('http://', 'https://')):
                                source_url = f"https://digiato.com{source_url}" if not source_url.startswith('/') else f"https://digiato.com{source_url}"
                            
                            # Use default if no URL found
                            if not source_url:
                                source_url = category["url"]
                            
                            # Store in database
                            cursor.execute(
                                "INSERT INTO news (title, body, source_url, category) VALUES (?, ?, ?, ?)",
                                (title, body, source_url, category["name"])
                            )
            except Exception as e:
                st.error(f"خطا در دریافت اخبار {category['name']}: {str(e)}")
        
        conn.commit()
    conn.close()
    st.success("اخبار با موفقیت دریافت شدند! ✨")
    time.sleep(1)  # For animation effect

def get_news_count(category=None):
    conn = sqlite3.connect('data.db', check_same_thread=False)
    cursor = conn.cursor()
    
    if category and category != "همه":
        cursor.execute("SELECT COUNT(*) FROM news WHERE category=?", (category,))
    else:
        cursor.execute("SELECT COUNT(*) FROM news")
    
    count = cursor.fetchone()[0]
    conn.close()
    return count

def display_news(category=None, page=1, per_page=5):
    # Initialize database first
    init_database()
    
    conn = sqlite3.connect('data.db', check_same_thread=False)
    cursor = conn.cursor()
    
    offset = (page - 1) * per_page
    
    # Get news data based on category
    if category and category != "همه":
        cursor.execute("""
            SELECT title, body, source_url, category 
            FROM news 
            WHERE category=? 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        """, (category, per_page, offset))
    else:
        cursor.execute("""
            SELECT title, body, source_url, category 
            FROM news 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        """, (per_page, offset))
    
    data = cursor.fetchall()
    conn.close()
    
    st.markdown('<div class="section-header">اخبار دیجیاتو 📰</div>', unsafe_allow_html=True)
    
    if not data:
        st.warning("اخباری برای نمایش وجود ندارد. لطفاً دکمه 'دریافت اخبار' را کلیک کنید. 🔄")
        return
    
    for row in data:
        # Extract data
        if len(row) >= 4:
            title, body, source_url, category = row
        else:
            # Handle case where data might be incomplete
            title = row[0]
            body = row[1] if len(row) > 1 else ""
            source_url = row[2] if len(row) > 2 else "#"
            category = row[3] if len(row) > 3 else "تکنولوژی"
        
        # Display news item with custom styling
        st.markdown(f"""
        <div class="news-container">
            <div class="news-title">{title}</div>
            <span class="category-tag">{category}</span>
            <div class="news-body">{body}</div>
            <a href="{source_url}" target="_blank" class="news-link-btn">مشاهده مطلب کامل 🔗</a>
        </div>
        """, unsafe_allow_html=True)
    
    return len(data)

def display_search_results(search_results, search_term, page=1, per_page=5):
    st.markdown(f'<div class="section-header">نتایج جستجو برای "{search_term}" 🔍</div>', unsafe_allow_html=True)
    
    if not search_results:
        st.warning("هیچ نتیجه‌ای یافت نشد. 😞")
        return 0
    
    offset = (page - 1) * per_page
    paginated_results = search_results[offset:offset + per_page]
    
    for row in paginated_results:
        # Extract data
        if len(row) >= 4:
            title, body, source_url, category = row
        else:
            # Handle case where data might be incomplete
            title = row[0]
            body = row[1] if len(row) > 1 else ""
            source_url = row[2] if len(row) > 2 else "#"
            category = row[3] if len(row) > 3 else "تکنولوژی"
        
        # Display news item with custom styling
        st.markdown(f"""
        <div class="news-container">
            <div class="news-title">{title}</div>
            <span class="category-tag">{category}</span>
            <div class="news-body">{body}</div>
            <a href="{source_url}" target="_blank" class="news-link-btn">مشاهده مطلب کامل 🔗</a>
        </div>
        """, unsafe_allow_html=True)
    
    return len(paginated_results)

def render_pagination(total_items, current_page, per_page, key_prefix=""):
    total_pages = (total_items + per_page - 1) // per_page
    
    if total_pages <= 1:
        return current_page
    
    # Create pagination container
    col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])
    
    with col1:
        if current_page > 1:
            if st.button("⏪ قبلی", key=f"{key_prefix}_prev"):
                return current_page - 1
    
    with col2:
        if current_page > 1:
            if st.button(str(current_page - 1), key=f"{key_prefix}_page_{current_page-1}"):
                return current_page - 1
    
    with col3:
        st.markdown(f"<div style='text-align: center; padding: 0.5rem;'><strong>صفحه {current_page}</strong></div>", unsafe_allow_html=True)
    
    with col4:
        if current_page < total_pages:
            if st.button(str(current_page + 1), key=f"{key_prefix}_page_{current_page+1}"):
                return current_page + 1
    
    with col5:
        if current_page < total_pages:
            if st.button("بعدی ⏩", key=f"{key_prefix}_next"):
                return current_page + 1
    
    return current_page

def display_contact_section():
    st.markdown('<div class="contact-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="contact-title">📩 ارتباط با ما</h2>', unsafe_allow_html=True)
    
    # Social media icons with neon effect
    socials = [
        {"name": "Telegram", "url": "https://t.me/mehrdad87org", "icon": "https://img.icons8.com/?size=100&id=k4jADXhS5U1t&format=png&color=000000", "class": "telegram"},
        {"name": "WhatsApp", "url": "https://wa.link/78c7u1", "icon": "https://img.icons8.com/?size=100&id=A1JUR9NRH7sC&format=png&color=000000", "class": "whatsapp"},
        {"name": "GitHub", "url": "https://github.com/mehrdad87org", "icon": "https://img.icons8.com/?size=100&id=LoL4bFzqmAa0&format=png&color=000000", "class": "github"},
        {"name": "Email", "url": "mailto:mehrdad87ourangg@gmail.com", "icon": "https://img.icons8.com/?size=100&id=eFPBXQop6V2m&format=png&color=000000", "class": "email"},
        {"name": "Instagram", "url": "https://instagram.com/mehrdad_ourang87", "icon": "https://img.icons8.com/?size=100&id=nj0Uj45LGUYh&format=png&color=000000", "class": "instagram"},
        {"name": "LinkedIn", "url": "https://www.linkedin.com/in/mehrdad-ourang-4204b734a", "icon": "https://img.icons8.com/?size=100&id=MR3dZdlA53te&format=png&color=000000", "class": "linkedin"}
    ]
    
    social_icons_html = '<div class="social-container">'
    for social in socials:
        social_icons_html += f'<a href="{social["url"]}" target="_blank" class="social-icon {social["class"]}" title="{social["name"]}"><img src="{social["icon"]}" alt="{social["name"]}"></a>'
    social_icons_html += '</div>'
    
    st.markdown(social_icons_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Initialize database at startup
    init_database()
    
    load_css()
    
    st.markdown('<div class="title-animation"><h1>اخبار دیجیاتو 📰</h1></div>', unsafe_allow_html=True)
    
    # Initialize session state for pagination
    if 'news_page' not in st.session_state:
        st.session_state.news_page = 1
    if 'search_page' not in st.session_state:
        st.session_state.search_page = 1
    
    # Items per page
    per_page = 5
    
    # Add search box
    search_term = st.text_input("جستجو در اخبار 🔍", key="search_input")
    
    # Get available categories from database
    conn = sqlite3.connect('data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM news")
    categories = [cat[0] for cat in cursor.fetchall() if cat[0]]
    conn.close()
    
    # If no categories exist yet, use default list
    if not categories:
        categories = ["تکنولوژی", "خودرو", "علمی", "کسب و کار"]
    
    # Category filter select box
    category_filter = st.selectbox(
        "فیلتر بر اساس دسته‌بندی 🏷️",
        options=["همه"] + categories,
        format_func=lambda x: "همه دسته‌بندی‌ها" if x == "همه" else x,
        key="category_filter"
    )
    
    # Button to fetch news from Digiato
    if st.button("دریافت اخبار 🔄", key="fetch_news"):
        scrape_and_store_news()
        st.rerun()
    
    # Check if we need to search
    if search_term:
        # Display search results
        conn = sqlite3.connect('data.db', check_same_thread=False)
        cursor = conn.cursor()
        
        if category_filter != "همه":
            cursor.execute(
                "SELECT title, body, source_url, category FROM news WHERE (title LIKE ? OR body LIKE ?) AND category=? ORDER BY timestamp DESC", 
                (f"%{search_term}%", f"%{search_term}%", category_filter)
            )
        else:
            cursor.execute(
                "SELECT title, body, source_url, category FROM news WHERE title LIKE ? OR body LIKE ? ORDER BY timestamp DESC", 
                (f"%{search_term}%", f"%{search_term}%")
            )
        
        search_results = cursor.fetchall()
        conn.close()
        
        displayed_items = display_search_results(
            search_results, 
            search_term, 
            st.session_state.search_page, 
            per_page
        )
        
        # Pagination for search results
        if len(search_results) > per_page:
            new_page = render_pagination(
                len(search_results),
                st.session_state.search_page,
                per_page,
                "search"
            )
            if new_page != st.session_state.search_page:
                st.session_state.search_page = new_page
                st.rerun()
    else:
        # Display regular news based on category filter
        total_news = get_news_count(category_filter)
        displayed_items = display_news(
            category_filter, 
            st.session_state.news_page, 
            per_page
        )
        
        # Pagination for news
        if total_news > per_page:
            new_page = render_pagination(
                total_news,
                st.session_state.news_page,
                per_page,
                "news"
            )
            if new_page != st.session_state.news_page:
                st.session_state.news_page = new_page
                st.rerun()
    
    # Add a refresh button
    if st.button("به روز رسانی اخبار ✨", key="refresh_btn"):
        scrape_and_store_news()
        st.rerun()
    
    # Display contact section
    display_contact_section()
    
    # Footer
    st.markdown("""
    <div class="footer">
        Created with ❤️ using Streamlit • Data source: Digiato.com
        <br>
        <span class="emoji">✨</span> <span class="emoji">🚀</span> <span class="emoji">📱</span> <span class="emoji">💻</span> <span class="emoji">🔮</span>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
