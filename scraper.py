import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urljoin

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


def extract_books_from_page(soup, category_name):
    """Extract all book information from a single page."""
    books = []

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
                'image_url': image_url
            })
        except Exception as e:
            print(f"Error extracting book data: {e}")
            continue

    return books


def get_total_pages(soup):
    """Try to determine total number of pages from pagination."""
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


def check_next_page(soup, current_page):
    """Check if there's a next page in pagination."""
    total_pages = get_total_pages(soup)
    return current_page < total_pages


def scrape_category(category_path):
    """Scrape all books from a category, handling pagination."""
    category_name = category_path.split('/')[-1]
    all_books = []
    page = 1
    total_pages = None

    print(f"\nScraping category: {category_name}")

    while True:
        # Construct URL with pagination
        if page == 1:
            url = urljoin(BASE_URL, category_path)
        else:
            url = urljoin(BASE_URL, f"{category_path}?page={page}")

        if total_pages:
            print(f"  Fetching page {page}/{total_pages}: {url}")
        else:
            print(f"  Fetching page {page}: {url}")

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Get total pages on first iteration
            if page == 1:
                total_pages = get_total_pages(soup)
                if total_pages > 1:
                    print(f"  Total pages detected: {total_pages}")

            # Extract books from current page
            books = extract_books_from_page(soup, category_name)

            if not books:
                print(f"  No books found on page {page}. Stopping.")
                break

            all_books.extend(books)
            print(f"  Found {len(books)} books on page {page}")

            # Check if there's a next page
            if not check_next_page(soup, page):
                print(f"  No more pages. Total books: {len(all_books)}")
                break

            page += 1

            # Be polite - add a small delay between requests
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"  Error fetching page {page}: {e}")
            break
        except Exception as e:
            print(f"  Unexpected error on page {page}: {e}")
            break

    return all_books


def main():
    """Main scraping function."""
    all_books = []

    print("Starting scraper for ebooks.az")
    print(f"Total categories to scrape: {len(CATEGORIES)}")

    for i, category in enumerate(CATEGORIES, 1):
        print(f"\n[{i}/{len(CATEGORIES)}] Processing category: {category}")

        try:
            books = scrape_category(category)
            all_books.extend(books)
            print(f"Category total: {len(books)} books")
            print(f"Overall total: {len(all_books)} books")

            # Add delay between categories
            time.sleep(2)

        except Exception as e:
            print(f"Error processing category {category}: {e}")
            continue

    # Save to CSV
    print(f"\n\nScraping complete! Total books collected: {len(all_books)}")
    print("Saving to CSV...")

    csv_filename = 'ebooks_az_all_books.csv'

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['category', 'title', 'author', 'publisher', 'year', 'book_url', 'image_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(all_books)

    print(f"Data saved to {csv_filename}")
    print(f"Total records: {len(all_books)}")


if __name__ == "__main__":
    main()
