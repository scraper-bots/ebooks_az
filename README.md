# Ebooks.az Web Scraper

## Overview
This project contains web scrapers to extract book data from ebooks.az for analytics purposes.

## Features

### Async Scraper (async_scraper.py) - **RECOMMENDED**
- Uses `aiohttp` and `asyncio` for high-performance concurrent scraping
- Scrapes all 34 book categories with full pagination support
- Extracts detailed information from individual book pages
- Rate-limited to be respectful to the server (10 concurrent requests max)
- Comprehensive logging to `scraper.log`

### Basic Scraper (scraper.py)
- Synchronous scraper using `requests`
- Good for testing or smaller scraping tasks
- Slower but simpler implementation

## Data Collected

The scraper extracts the following fields for each book:

### From Category Pages:
- **category**: Book category name
- **title**: Book title (Sərlövhə)
- **author**: Author name(s) (Müəllif)
- **publisher**: Publisher name (Nəşriyyat)
- **year**: Publication year (Nəşr ili)
- **book_url**: Link to individual book page
- **image_url**: Cover image URL

### From Individual Book Pages:
- **publication_place**: Publication location (Nəşr yeri) - e.g., "Bakı"
- **page_count**: Number of pages (Səhifə)

## Output

The async scraper saves data to: `ebooks_az_all_books_detailed.csv`

CSV includes all fields listed above, making it ready for:
- Statistical analysis
- Data visualization
- Publisher/author analysis
- Publication trend analysis
- Category distribution studies

## Categories Scraped (34 total)

1. Philosophy (Fəlsəfə)
2. History (Tarix)
3. Azerbaijan History (Azərbaycan tarixi)
4. Sociology (Sosiologiya)
5. Ethnography (Etnoqrafiya)
6. Economy (İqtisadiyyat)
7. State and Law (Dövlət və hüquq)
8. Politics (Siyasət. Siyasi elmlər)
9. Science and Education (Elm və təhsil)
10. Culture (Mədəniyyət)
11. Library Science (Kitabxana işi)
12. Psychology (Psixologiya)
13. Linguistics (Dilçilik)
14. Literary Studies (Ədəbiyyatşünaslıq)
15. Folklore (Folklor)
16. Fiction (Bədii ədəbiyyat)
17. Art (İncəsənət)
18. Mass Media (Kütləvi informasiya vasitələri)
19. Informatics (İnformatika)
20. Religion (Din)
21. Natural Sciences (Təbiət elmləri)
22. Oil (Neft)
23. Communications (Rabitə)
24. Technology (Texnika. Texniki elmlər)
25. Architecture (Arxitektura)
26. Agriculture and Forestry (Kənd və meşə təsərrüfatı)
27. Tourism (Тurizm)
28. Customs (Gömrük işi)
29. Medicine and Health (Tibb və səhiyyə)
30. Military (Hərbi iş)
31. Sports (İdman)
32. Statistics (Statistika)
33. Ecology (Ekologiya)
34. Reference Publications (Məlumat nəşrləri)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Run the async scraper (recommended):
```bash
python async_scraper.py
```

### Run the basic scraper:
```bash
python scraper.py
```

### Monitor progress:
```bash
tail -f scraper.log
```

## Performance

- **Async scraper**: Much faster due to concurrent requests
  - Approximately 10-20x faster than synchronous version
  - Completes all categories in 1-2 hours (depending on server response times)

- **Basic scraper**: Slower, sequential processing
  - Takes 3-4 hours to complete all categories

## Configuration

You can adjust these parameters in `async_scraper.py`:
- `MAX_CONCURRENT_REQUESTS`: Number of concurrent requests (default: 10)
- Delays between requests and categories for rate limiting

## Logging

All operations are logged to:
- `scraper.log`: Detailed log file with timestamps
- Console output: Real-time progress updates

## Notes

- The scraper is designed to be respectful to the server with rate limiting
- All requests include appropriate delays to avoid overwhelming the server
- Error handling is built-in to skip problematic pages and continue scraping
- Progress is logged in real-time for monitoring

## Analytics Use Cases

This data is ideal for:
1. **Publication trends**: Analyze books published over time
2. **Publisher analysis**: Most active publishers, publication patterns
3. **Category distribution**: Which categories have the most books
4. **Author analysis**: Prolific authors, multi-category authors
5. **Geographic analysis**: Publication places (mostly Bakı)
6. **Book length analysis**: Page count statistics by category
7. **Recent publications**: Filter by year for recent books
8. **Cross-category analysis**: Authors/publishers working across multiple categories
