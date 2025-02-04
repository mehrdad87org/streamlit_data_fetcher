# README

## Project Overview

This project is a Streamlit-based web application that fetches data from two sources:
1. **JSONPlaceholder API**: Retrieves user posts and stores them in a SQLite database.
2. **Digiato Website**: Scrapes tech news articles and stores them in the same SQLite database.

The application displays the fetched data in a clean and interactive UI using Streamlit. The SQLite database (`data.db`) is automatically deleted when the Streamlit server process stops, ensuring a fresh start on subsequent runs.

---

## Features

- Fetches and stores user posts from the JSONPlaceholder API.
- Scrapes and stores tech news articles from the Digiato website.
- Displays the stored data in a user-friendly interface.
- Automatically deletes the SQLite database (`data.db`) when the Streamlit server stops.

---

## Requirements

To run this project, you need the following Python libraries installed:

- `streamlit`
- `requests`
- `beautifulsoup4`
- `sqlite3`

You can install the required libraries using the following command:

```bash
pip install streamlit requests beautifulsoup4
