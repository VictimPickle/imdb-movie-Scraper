"""
Movie Finder - IMDb Movie Information Scraper & Local Database Viewer

A desktop application that allows users to search for movies in a local JSON database.
If a movie is not found, it scrapes movie information from IMDb and saves it to the database.

Features:
- Search local database by movie name
- Fallback to IMDb web scraping for movies not in database
- Browse movie results and select the correct one
- View detailed movie information (cast, directors, writers, genres, ratings, etc.)
- Automatic database persistence

Requirements:
    pip install selenium beautifulsoup4 tk

Author: Movie Finder
License: MIT
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import sys
from typing import Tuple, Optional, Dict, List


# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

def resource_path(relative: str) -> str:
    """
    Get correct path to bundled assets for PyInstaller compatibility.
    
    Args:
        relative (str): Relative path to asset
        
    Returns:
        str: Absolute path to asset
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.abspath("."), relative)


DB_FILE = resource_path("all_movies.json")


# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def load_db() -> Dict:
    """
    Load movies from local JSON database.
    
    Returns:
        Dict: Dictionary of movies, or empty dict if DB doesn't exist
    """
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading database: {e}")
            return {}
    return {}


def save_db(db: Dict) -> None:
    """
    Save movies to local JSON database.
    
    Args:
        db (Dict): Dictionary of movies to save
    """
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    except IOError as e:
        messagebox.showerror("Save Error", f"Failed to save database: {str(e)}")


# ============================================================================
# UI DISPLAY FUNCTIONS
# ============================================================================

def display_movie_details(movie_data: Dict, movie_title: str) -> None:
    """
    Display interactive movie information menu.
    
    Shows user options to view different aspects of movie details in messageboxes.
    Loops until user chooses to go back.
    
    Args:
        movie_data (Dict): Movie information dictionary with keys:
                           title, year, rating, genres, directors, writers, 
                           cast, certificate, description
        movie_title (str): Display title of the movie
    """
    while True:
        menu_text = f"Movie: {movie_title}\n\n"
        menu_text += "What information do you want to see?\n\n"
        menu_text += "1. Title & Year\n"
        menu_text += "2. IMDb Rating & Certificate\n"
        menu_text += "3. Genres\n"
        menu_text += "4. Directors\n"
        menu_text += "5. Writers\n"
        menu_text += "6. Cast\n"
        menu_text += "7. Plot/Description\n"
        menu_text += "8. Full Information (All)\n"
        menu_text += "0. Back to Search\n\n"
        menu_text += "Enter your choice (0-8):"
        
        root = tk.Tk()
        root.withdraw()
        
        choice = simpledialog.askinteger(
            "Movie Details",
            menu_text,
            minvalue=0,
            maxvalue=8,
            parent=root
        )
        root.destroy()
        
        if choice is None or choice == 0:
            break
        
        # Display selected information
        if choice == 1:
            response = (
                f"Title: {movie_data['title']}\n"
                f"Year: {movie_data.get('year', 'N/A')}"
            )
            messagebox.showinfo("Title & Year", response)
        
        elif choice == 2:
            response = (
                f"IMDb Rating: {movie_data.get('rating', 'N/A')}\n"
                f"Certificate: {movie_data.get('certificate', 'N/A')}"
            )
            messagebox.showinfo("Rating & Certificate", response)
        
        elif choice == 3:
            genres = ', '.join(movie_data.get('genres', [])) if movie_data.get('genres') else 'N/A'
            response = f"Genres: {genres}"
            messagebox.showinfo("Genres", response)
        
        elif choice == 4:
            directors = ', '.join(movie_data.get('directors', [])) if movie_data.get('directors') else 'N/A'
            response = f"Directors:\n{directors}"
            messagebox.showinfo("Directors", response)
        
        elif choice == 5:
            writers = ', '.join(movie_data.get('writers', [])) if movie_data.get('writers') else 'N/A'
            response = f"Writers:\n{writers}"
            messagebox.showinfo("Writers", response)
        
        elif choice == 6:
            cast = ', '.join(movie_data.get('cast', [])) if movie_data.get('cast') else 'N/A'
            response = f"Cast (Top 10):\n{cast}"
            messagebox.showinfo("Cast", response)
        
        elif choice == 7:
            description = movie_data.get('description', 'N/A')
            messagebox.showinfo("Plot/Description", f"Plot:\n{description}")
        
        elif choice == 8:
            response = (
                f"Title: {movie_data['title']} ({movie_data.get('year', 'N/A')})\n"
                f"IMDb Rating: {movie_data.get('rating', 'N/A')}\n"
                f"Genres: {', '.join(movie_data.get('genres', []) or ['N/A'])}\n"
                f"Directors: {', '.join(movie_data.get('directors', []) or ['N/A'])}\n"
                f"Writers: {', '.join(movie_data.get('writers', []) or ['N/A'])}\n"
                f"Stars: {', '.join(movie_data.get('cast', [])[:5] or ['N/A'])}\n"
                f"Certificate: {movie_data.get('certificate', 'N/A')}\n"
                f"\nPlot: {movie_data.get('description', '')}\n"
            )
            messagebox.showinfo("Full Movie Information", response)


# ============================================================================
# WEB SCRAPING FUNCTIONS
# ============================================================================

def scrape_imdb(movie_name: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Search IMDb for a movie and scrape its details.
    
    Workflow:
    1. Opens IMDb homepage
    2. Searches for the movie
    3. Shows top 10 results to user
    4. User selects the correct movie
    5. Scrapes detailed movie information from selected movie page
    6. Returns structured movie data
    
    Args:
        movie_name (str): Name of movie to search for
        
    Returns:
        Tuple[Dict | None, str | None]: (movie_data, selected_title) or (None, None) if cancelled
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.keys import Keys
        import time
        from bs4 import BeautifulSoup
        
    except ImportError as e:
        messagebox.showerror(
            "Missing Library",
            f"Missing library: {str(e)}\n\nInstall with:\n"
            "pip install selenium beautifulsoup4"
        )
        return None, None
    
    driver = webdriver.Chrome()
    
    try:
        # Step 1: Open IMDb and search
        driver.get("https://www.imdb.com/")
        
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "suggestion-search"))
        )
        
        search_box.clear()
        search_box.send_keys(movie_name)
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(3)
        
        # Step 2: Parse search results
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        results = []
        result_links = soup.find_all('a', {'data-testid': 'find-result-title-link'})
        
        if not result_links:
            result_links = soup.find_all('a', href=lambda x: x and '/title/tt' in x)
        
        for idx, link in enumerate(result_links[:10]):
            title_text = link.text.strip()
            href = link.get('href', '')
            
            year = "N/A"
            if '(' in title_text and ')' in title_text:
                try:
                    year = title_text.split('(')[-1].replace(')', '')
                except:
                    pass
            
            results.append({
                'index': idx + 1,
                'title': title_text,
                'year': year,
                'href': href if href.startswith('http') else f"https://www.imdb.com{href}",
                'id': href.split('/title/')[1].split('/')[0] if '/title/' in href else None
            })
        
        if not results:
            driver.quit()
            messagebox.showerror("No Results", "No search results found on IMDb.")
            return None, None
        
        # Step 3: Present selection dialog
        selection_text = "Found multiple results. Please select the correct movie:\n\n"
        for result in results:
            selection_text += f"{result['index']}. {result['title']} ({result['year']})\n"
        selection_text += f"\nEnter number (1-{len(results)}) or 0 to cancel:"
        
        root = tk.Tk()
        root.withdraw()
        
        user_choice = simpledialog.askinteger(
            "Movie Selection",
            selection_text,
            minvalue=0,
            maxvalue=len(results),
            parent=root
        )
        root.destroy()
        
        if user_choice is None or user_choice == 0:
            driver.quit()
            return None, None
        
        # Step 4: Navigate to selected movie
        selected_movie = results[user_choice - 1]
        selected_title = selected_movie['title']
        movie_url = selected_movie['href']
        
        driver.get(movie_url)
        time.sleep(2)
        
        # Step 5: Scrape movie details (robust selectors)
        movie_soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        movie_data = _extract_movie_data(movie_soup, selected_movie)
        
        driver.quit()
        
        return movie_data, selected_title
    
    except Exception as e:
        driver.quit()
        messagebox.showerror("Error", f"Error during scraping: {str(e)}")
        return None, None


def _extract_movie_data(soup, fallback_data: Dict) -> Dict:
    """
    Extract movie details from IMDb movie page HTML using robust selectors.
    
    Uses data-testid attributes (more stable than class names) with fallbacks
    for fields that may change structure.
    
    Args:
        soup: BeautifulSoup parsed HTML
        fallback_data (Dict): Fallback info from search results
        
    Returns:
        Dict: Movie information with keys: title, year, rating, genres, 
              directors, writers, cast, certificate, description
    """
    
    # Title
    title_tag = soup.find('h1', {'data-testid': 'hero-title-block__title'})
    title = title_tag.text.strip() if title_tag else fallback_data.get('title', 'N/A')
    
    # Year
    year = "N/A"
    year_tag = soup.find('a', {'data-testid': 'title-details-releasedate'})
    if year_tag:
        year_text = year_tag.text.strip()
        if year_text:
            year = year_text.split()[-1]
    
    # IMDb Rating (primary and fallback selectors)
    rating = "N/A"
    rating_tag = soup.find('span', {'data-testid': 'hero-rating-bar__aggregate-rating__score'})
    if rating_tag and rating_tag.text:
        rating = rating_tag.text.strip().split('/')[0]
    if rating == "N/A":
        alt_rating_tag = soup.find('span', class_=lambda x: x and "AggregateRatingButton__RatingScore" in x)
        if alt_rating_tag and alt_rating_tag.text:
            rating = alt_rating_tag.text.strip()
    
    # Genres (with fallback)
    genres = []
    genre_section = soup.find('div', {'data-testid': 'genres'})
    if genre_section:
        genre_spans = genre_section.find_all('span', {'class': 'ipc-chip__text'})
        genres = [span.text.strip() for span in genre_spans]
    if not genres:
        genre_links = soup.find_all('a', href=lambda x: x and '/search/title?genres=' in x)
        genres = [g.text.strip() for g in genre_links]
    
    # Certificate
    certificate = "N/A"
    certificate_tag = soup.find('span', {'data-testid': 'title-details-certificate'})
    if certificate_tag:
        certificate = certificate_tag.text.strip()
    
    # Plot/Description
    description = "N/A"
    plot_tag = soup.find('span', {'data-testid': 'plot-l'})
    if not plot_tag:
        plot_tag = soup.find('span', {'data-testid': 'plot-xl'})
    if plot_tag:
        description = plot_tag.text.strip()
    
    # Directors and Writers
    directors = []
    writers = []
    credits = soup.find_all('li', {'data-testid': 'title-pc-principal-credit'})
    for credit in credits:
        label = credit.find('span', {'class': 'ipc-metadata-list-item__label'})
        if label:
            label_text = label.text.strip()
            names = [a.text.strip() for a in credit.find_all('a')]
            if 'Director' in label_text:
                directors = names
            elif 'Writer' in label_text:
                writers = names
    
    # Cast (top 10)
    cast = []
    cast_items = soup.find_all('div', {'data-testid': 'title-cast-item'})
    for item in cast_items[:10]:
        actor_tag = item.find('a', {'data-testid': 'title-cast-item__actor'})
        if actor_tag:
            cast.append(actor_tag.text.strip())
    
    return {
        "title": title,
        "year": year,
        "rating": rating,
        "genres": genres,
        "directors": directors,
        "writers": writers,
        "cast": cast,
        "certificate": certificate,
        "description": description
    }


# ============================================================================
# SEARCH & MAIN LOGIC
# ============================================================================

def search_movie() -> None:
    """
    Main search handler - queries local DB first, then IMDb if not found.
    
    Workflow:
    1. Get user input from search entry
    2. Check local database
    3. If found: display details
    4. If not found: scrape IMDb, save to DB, display details
    """
    name = entry.get().strip()
    
    if not name:
        messagebox.showwarning("Empty Input", "Please enter a movie name.")
        return
    
    db = load_db()
    
    # Search local database
    found = None
    found_key = None
    for key, v in db.items():
        if v.get("title", "").lower() == name.lower():
            found = v
            found_key = key
            break
    
    if found:
        messagebox.showinfo(
            "Movie Found",
            f"Found '{found['title']}' in database!"
        )
        display_movie_details(found, found_key)
    else:
        # Search IMDb
        movie_data, selected_title = scrape_imdb(name)
        
        if movie_data is None:
            return
        
        # Save to database
        db[selected_title] = movie_data
        save_db(db)
        
        messagebox.showinfo(
            "Movie Added",
            f"Successfully added '{movie_data['title']}' to database!"
        )
        display_movie_details(movie_data, selected_title)


# ============================================================================
# GUI INITIALIZATION
# ============================================================================

def init_gui() -> None:
    """Initialize and run the Tkinter GUI."""
    global root_window, entry
    
    root_window = tk.Tk()
    root_window.title("Movie Finder")
    root_window.geometry("500x200")
    root_window.config(bg="#1a1a2e")
    
    # Main frame
    main_frame = tk.Frame(root_window, bg="#1a1a2e")
    main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        main_frame,
        text="🎬 Movie Finder",
        font=("Arial", 24, "bold"),
        bg="#1a1a2e",
        fg="#00d4ff"
    )
    title_label.pack(pady=20)
    
    # Search label
    search_label = tk.Label(
        main_frame,
        text="Enter movie name:",
        font=("Arial", 12),
        bg="#1a1a2e",
        fg="#ffffff"
    )
    search_label.pack(pady=5)
    
    # Search entry
    entry = tk.Entry(
        main_frame,
        width=40,
        font=("Arial", 12),
        bg="#16213e",
        fg="#00d4ff",
        insertbackground="#00d4ff",
        relief=tk.FLAT,
        bd=0
    )
    entry.pack(ipady=10, pady=10)
    
    # Search button
    search_button = tk.Button(
        main_frame,
        text="Search",
        command=search_movie,
        font=("Arial", 12, "bold"),
        bg="#00d4ff",
        fg="#1a1a2e",
        relief=tk.FLAT,
        bd=0,
        cursor="hand2",
        padx=40,
        pady=10
    )
    search_button.pack(pady=15)
    
    # Bind Enter key
    entry.bind("<Return>", lambda event: search_movie())
    
    root_window.mainloop()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    init_gui()
