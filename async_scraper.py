import asyncio
import aiohttp
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import logging
from typing import List, Dict
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Base URL
BASE_URL = "https://www.ebooks.az"

# All category URLs extracted from the dropdown menu
CATEGORIES = [
    "/az/category/philosophy",      # Fəlsəfə
    "/az/category/history",         # Tarix
    "/az/category/historyaz",       # Azərbaycan tarixi
    "/az/category/sociology",       # Sosiologiya
    "/az/category/ethnography",     # Etnoqrafiya
    "/az/category/economy",         # İqtisadiyyat
    "/az/category/law",             # Dövlət və hüquq
    "/az/category/politics",        # Siyasət. Siyasi elmlər
    "/az/category/education",       # Elm və təhsil
    "/az/category/cultourism",      # Mədəniyyət
    "/az/category/library",         # Kitabxana işi
    "/az/category/psikol",          # Psixologiya
    "/az/category/luget",           # Dilçilik
    "/az/category/philology",       # Ədəbiyyatşünaslıq
    "/az/category/folklor",         # Folklor
    "/az/category/belleslettres",   # Bədii ədəbiyyat
    "/az/category/art",             # İncəsənət
    "/az/category/journalism",      # Kütləvi informasiya vasitələri
    "/az/category/informatics",     # İnformatika
    "/az/category/relijion",        # Din
    "/az/category/natscien",        # Təbiət elmləri
    "/az/category/oil",             # Neft
    "/az/category/commun",          # Rabitə
    "/az/category/techscien",       # Texnika. Texniki elmlər
    "/az/category/architec",        # Arxitektura
    "/az/category/agriculture",     # Kənd və meşə təsərrüfatı
    "/az/category/tours",           # Тurizm
    "/az/category/customs",         # Gömrük işi
    "/az/category/health",          # Tibb və səhiyyə
    "/az/category/military",        # Hərbi iş
    "/az/category/spo",             # İdman
    "/az/category/statistics",      # Statistika
    "/az/category/ecology",         # Ekologiya
    "/az/category/refeditions",     # Məlumat nəşrləri
]

# Semaphore to limit concurrent requests
MAX_CONCURRENT_REQUESTS = 10


async def fetch_page(session: aiohttp.ClientSession, url: str) -> str:
    """Fetch a page and return its content."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


def extract_detail_from_dl(soup: BeautifulSoup, label: str) -> str:
    """Extract a specific detail from the book detail page."""
    try:
        dt_elements = soup.find_all('dt')
        for dt in dt_elements:
            if label in dt.get_text():
                dd = dt.find_next_sibling('dd')
                if dd:
                    # Remove any nested links and get just the text
                    return dd.get_text(strip=True)
    except Exception as e:
        logger.debug(f"Error extracting {label}: {e}")
    return ""


async def fetch_book_details(session: aiohttp.ClientSession, book_url: str, semaphore: asyncio.Semaphore) -> Dict[str, str]:
    """Fetch detailed information from individual book page."""
    async with semaphore:
        try:
            html = await fetch_page(session, book_url)
            if not html:
                return {}

            soup = BeautifulSoup(html, 'html.parser')

            # Extract additional details from the book page
            details = {
                'publication_place': extract_detail_from_dl(soup, 'Nəşr yeri:'),
                'page_count': extract_detail_from_dl(soup, 'Səhifə:'),
            }

            return details
        except Exception as e:
            logger.error(f"Error fetching book details from {book_url}: {e}")
            return {}


def extract_books_from_page(html: str, category_name: str) -> List[Dict]:
    """Extract all book information from a single category page."""
    books = []

    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Find all book cards
        cards = soup.find_all('div', class_='card mb-5 border-0 shadow-lg p-4 w-100')

        for card in cards:
            try:
                # Extract book URL and title
                title_element = card.find('h5', class_='card-title')
                link_element = card.find('a', href=True)

                title = title_element.get_text(strip=True) if title_element else ""
                book_url = link_element['href'] if link_element else ""

                # Extract image URL
                img_element = card.find('img', class_='img-fluid')
                image_url = img_element['src'] if img_element else ""
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(BASE_URL, image_url)

                # Extract author, publisher, and year from list items
                list_items = card.find_all('li', class_='list-group-item text-muted')
                author = list_items[0].get_text(strip=True) if len(list_items) > 0 else ""
                publisher = list_items[1].get_text(strip=True) if len(list_items) > 1 else ""
                year = list_items[2].get_text(strip=True) if len(list_items) > 2 else ""

                books.append({
                    'category': category_name,
                    'title': title,
                    'author': author,
                    'publisher': publisher,
                    'year': year,
                    'book_url': book_url,
                    'image_url': image_url,
                    'publication_place': '',  # Will be filled from detail page
                    'page_count': ''  # Will be filled from detail page
                })
            except Exception as e:
                logger.error(f"Error extracting book data from card: {e}")
                continue

    except Exception as e:
        logger.error(f"Error parsing page HTML: {e}")

    return books


def get_total_pages(html: str) -> int:
    """Try to determine total number of pages from pagination."""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        pagination = soup.find('nav', attrs={'aria-label': 'Page navigation'})
        if not pagination:
            return 1

        # Look for all page links
        page_links = pagination.find_all('a', class_='page-link')
        max_page = 1

        for link in page_links:
            # Try to extract page number from the link href
            href = link.get('href', '')
            if 'page=' in href:
                try:
                    page_str = href.split('page=')[1].split('&')[0]
                    page_num = int(page_str)
                    if page_num > max_page:
                        max_page = page_num
                except (ValueError, IndexError):
                    pass

            # Also try to get it from the link text
            try:
                page_num = int(link.get_text(strip=True))
                if page_num > max_page:
                    max_page = page_num
            except ValueError:
                continue

        return max_page
    except Exception as e:
        logger.error(f"Error determining total pages: {e}")
        return 1


async def scrape_category(session: aiohttp.ClientSession, category_path: str, detail_semaphore: asyncio.Semaphore) -> List[Dict]:
    """Scrape all books from a category, handling pagination."""
    category_name = category_path.split('/')[-1]
    all_books = []

    logger.info(f"\nScraping category: {category_name}")

    # Fetch first page to determine total pages
    url = urljoin(BASE_URL, category_path)
    html = await fetch_page(session, url)

    if not html:
        logger.error(f"Failed to fetch first page for category {category_name}")
        return []

    total_pages = get_total_pages(html)
    logger.info(f"  Total pages detected: {total_pages}")

    # Extract books from first page
    books = extract_books_from_page(html, category_name)
    all_books.extend(books)
    logger.info(f"  Page 1/{total_pages}: Found {len(books)} books")

    # Fetch remaining pages
    for page in range(2, total_pages + 1):
        url = urljoin(BASE_URL, f"{category_path}?page={page}")
        html = await fetch_page(session, url)

        if not html:
            logger.warning(f"  Failed to fetch page {page}")
            continue

        books = extract_books_from_page(html, category_name)
        all_books.extend(books)
        logger.info(f"  Page {page}/{total_pages}: Found {len(books)} books")

        # Small delay to be polite
        await asyncio.sleep(0.5)

    logger.info(f"  Category total: {len(all_books)} books")

    # Now fetch details for each book in batches
    logger.info(f"  Fetching detailed information for {len(all_books)} books...")

    tasks = []
    for book in all_books:
        if book['book_url']:
            task = fetch_book_details(session, book['book_url'], detail_semaphore)
            tasks.append(task)
        else:
            tasks.append(asyncio.sleep(0))  # Placeholder for books without URLs

    # Fetch all book details concurrently with rate limiting
    details_list = await asyncio.gather(*tasks)

    # Merge details into books
    for i, details in enumerate(details_list):
        if isinstance(details, dict):
            all_books[i].update(details)

    logger.info(f"  Completed category {category_name}: {len(all_books)} books with full details")

    return all_books


async def main():
    """Main scraping function."""
    logger.info("Starting async scraper for ebooks.az")
    logger.info(f"Total categories to scrape: {len(CATEGORIES)}")

    all_books = []
    detail_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    # Create a single session for all requests
    connector = aiohttp.TCPConnector(limit=50, limit_per_host=10)
    timeout = aiohttp.ClientTimeout(total=60)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        for i, category in enumerate(CATEGORIES, 1):
            logger.info(f"\n[{i}/{len(CATEGORIES)}] Processing category: {category}")

            try:
                books = await scrape_category(session, category, detail_semaphore)
                all_books.extend(books)
                logger.info(f"Overall total: {len(all_books)} books")

                # Add delay between categories
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error processing category {category}: {e}")
                continue

    # Save to CSV
    logger.info(f"\n\nScraping complete! Total books collected: {len(all_books)}")
    logger.info("Saving to CSV...")

    csv_filename = 'ebooks_az_all_books_detailed.csv'

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['category', 'title', 'author', 'publisher', 'year',
                     'publication_place', 'page_count', 'book_url', 'image_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(all_books)

    logger.info(f"Data saved to {csv_filename}")
    logger.info(f"Total records: {len(all_books)}")


if __name__ == "__main__":
    asyncio.run(main())
