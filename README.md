# Movie Finder 🎬

A desktop application that searches for movies in a local JSON database and scrapes IMDb for additional information on missing movies.

## Features

✨ **Local Database Search** - Quickly search movies stored locally in JSON format
🌐 **IMDb Web Scraping** - Automatically fetch movie details from IMDb if not in database
📋 **Rich Movie Information** - Get cast, directors, writers, genres, ratings, certificates, and plot summaries
💾 **Auto-Save** - Scraped movies are automatically saved to the local database
🎨 **Modern GUI** - Clean, dark-themed Tkinter interface
📌 **Smart Selection** - User-friendly movie selection from search results

## Installation

### Prerequisites

- Python 3.7+
- Chrome browser (for Selenium WebDriver)
- ChromeDriver (compatible with your Chrome version)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/movie-finder.git
cd movie-finder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download ChromeDriver from https://chromedriver.chromium.org/ and add it to your PATH or place it in the project directory.

## Usage

Run the application:
```bash
python movie_finder.py
```

### Workflow

1. **Enter a movie name** in the search field
2. **If found locally**: Movie details appear instantly
3. **If not found**: 
   - Application searches IMDb
   - Shows top 10 results
   - You select the correct movie
   - Details are fetched and saved to database

4. **Browse details** through the interactive menu:
   - Title & Year
   - Rating & Certificate
   - Genres
   - Directors
   - Writers
   - Cast
   - Plot/Description
   - Full Information

## Project Structure

```
movie-finder/
├── movie_finder.py         # Main application
├── all_movies.json         # Local movie database (auto-created)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Database Format

The `all_movies.json` file stores movies with this structure:

```json
{
  "Movie Title (Year)": {
    "title": "Movie Title",
    "year": "2023",
    "rating": "8.5",
    "genres": ["Drama", "Thriller"],
    "directors": ["Director Name"],
    "writers": ["Writer Name"],
    "cast": ["Actor 1", "Actor 2"],
    "certificate": "PG-13",
    "description": "Movie plot summary..."
  }
}
```

## Configuration

### Chrome WebDriver

If you don't have ChromeDriver in your PATH:

1. Download from: https://chromedriver.chromium.org/
2. Place in project directory
3. Update line in `scrape_imdb()`:
```python
driver = webdriver.Chrome('./chromedriver')  # or './chromedriver.exe' on Windows
```

## Known Issues & Limitations

- **IMDb Structure Changes**: If IMDb redesigns their site, some selectors may break
- **Rate Limiting**: IMDb may temporarily block requests if scraping too rapidly
- **JavaScript Content**: Static HTML parsing may miss dynamically-loaded content
- **Chrome Requirement**: Application requires Chrome and ChromeDriver

## Troubleshooting

### "Missing library: selenium" or "beautifulsoup4"
```bash
pip install selenium beautifulsoup4
```

### ChromeDriver Issues
- Ensure ChromeDriver version matches your Chrome version
- Add ChromeDriver to system PATH or specify full path in code
- On Linux: `chmod +x chromedriver` to make executable

### No results found on IMDb
- Check your internet connection
- IMDb may be temporarily blocking requests (wait a few minutes)
- Try a simpler movie title

### Empty fields (cast, writers, directors)
- IMDb page structure may have changed
- The application tries multiple selector fallbacks
- Some older movies may have incomplete data on IMDb

## Building Standalone Executable

To create a standalone `.exe` file for Windows:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed movie_finder.py
```

The executable will be in the `dist/` folder.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Enhancements

- [ ] Search by IMDb ID
- [ ] Movie recommendations based on ratings
- [ ] Export database to CSV
- [ ] Dark/Light theme toggle
- [ ] Advanced search filters
- [ ] Movie watchlist functionality
- [ ] Integration with other databases (TMDB, etc.)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Always respect IMDb's terms of service and robots.txt when web scraping.

## Contact

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for movie enthusiasts**
