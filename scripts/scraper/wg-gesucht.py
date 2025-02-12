import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

class WGGesuchtScraper:
    def __init__(self):
        self.base_url = "https://www.wg-gesucht.de"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def get_listings(self, url: str, limit: int = 10) -> list[dict]:
        """
        Scrapes and extracts listing information from a WG-Gesucht webpage.

        Args:
            url (str): The URL of the WG-Gesucht page to scrape.
            limit (int, optional): Maximum number of listings to retrieve. Defaults to 10.

        Returns:
            list[dict]: List of dictionaries containing listing information with keys:
                - title: The listing title
                - price: Monthly rent amount
                - size: Size in square meters
                - rooms: Number of rooms
                - address: Location/address information
                - available_from: Available date
                - image_url: URL of the listing image
                - details_link: Link to full listing details
        """
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = []
            count = 0

            for item in soup.find_all("div", class_="wgg_card"):
                if count >= limit:
                    break
                    
                listing = {}
                
                # Improved title extraction
                title_elem = item.find("h3", class_="truncate_title")
                listing['title'] = self._clean_text(title_elem.find('a').text) if title_elem else None

                # Extract price
                price_elem = item.find("div", class_="middle").find('b')
                listing['price'] = self._extract_number(price_elem.text) if price_elem else None

                # Extract size
                size_elem = item.find("div", class_="col-xs-3 text-right").find('b')
                listing['size'] = self._extract_number(size_elem.text) if size_elem else None

                # Improved location extraction
                location_elem = item.find("div", class_="col-xs-11")
                if location_elem:
                    location_text = location_elem.get_text(separator='|', strip=True)
                    parts = [self._clean_text(p) for p in location_text.split('|')]
                    
                    # Extract room number from WG size
                    if parts and 'er WG' in parts[0]:
                        listing['rooms'] = self._extract_number(parts[0])
                    
                    # Create clean location string without WG size part
                    location_parts = [p for p in parts[1:] if p and p.strip()]
                    listing['address'] = ', '.join(map(str.strip, location_parts))

                # Extract available date
                date_elem = item.find("div", class_="col-xs-5 text-center")
                listing['available_from'] = date_elem.text.strip() if date_elem else None

                # Extract image URL
                image_elem = item.find("div", class_="card_image").find('a')
                listing['image_url'] = self._extract_image_url(image_elem.get('style')) if image_elem else None

                # Extract details link
                link_elem = item.find("h3", class_="truncate_title").find('a')
                listing['details_link'] = self.base_url + link_elem.get('href') if link_elem else None

                listings.append(listing)
                count += 1

            return listings

        except Exception as e:
            print(f"Error scraping listings: {e}")
            return []

    def _extract_number(self, text: str) -> int:
        """
        Extracts the first number found in a string.

        Args:
            text (str): The input string containing numbers.

        Returns:
            int: The first number found in the string, or None if no number is found.
        """
        if not text:
            return None
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else None

    def _extract_image_url(self, style_text: str) -> str:
        """
        Extracts the image URL from a style attribute text.

        Args:
            style_text (str): The style attribute text containing the image URL.

        Returns:
            str: The extracted image URL, or None if no URL is found.
        """
        if not style_text:
            return None
        url_match = re.search(r'url\((.*?)\)', style_text)
        if url_match:
            url = url_match.group(1)
            return url.replace('.small.', '.large.')
        return None

    def _clean_text(self, text: str) -> str:
        """
        Cleans the input text by replacing newlines and multiple spaces with a single space.

        Args:
            text (str): The input text to clean.

        Returns:
            str: The cleaned text.
        """
        if not text:
            return None
        # Replace newlines and multiple spaces with single space
        cleaned = re.sub(r'\s+', ' ', text)
        return cleaned.strip()

    def save_to_json(self, listings: list[dict], filename: str = None) -> str:
        """
        Saves the listings to a JSON file.

        Args:
            listings (list[dict]): The list of listings to save.
            filename (str, optional): The filename to save the listings to. If not provided, a filename with a timestamp will be generated.

        Returns:
            str: The filename the listings were saved to, or None if an error occurred.
        """
        if filename is None:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wg_listings_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(listings, f, ensure_ascii=False, indent=2)
            print(f"Listings saved to {filename}")
            return filename
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return None

    def scrape_multiple_urls(self, urls: list[str], limit_per_url: int = 100) -> list[dict]:
        """
        Scrape multiple URLs and combine the results.

        Args:
            urls (list[str]): List of URLs to scrape.
            limit_per_url (int, optional): Maximum number of listings to retrieve per URL. Defaults to 100.

        Returns:
            list[dict]: Combined list of listings from all URLs.
        """
        all_listings = []
        for url in urls:
            print(f"Scraping: {url}")
            listings = self.get_listings(url, limit=limit_per_url)
            all_listings.extend(listings)
            print(f"Found {len(listings)} listings from this URL")
        return all_listings

if __name__ == "__main__":
    scraper = WGGesuchtScraper()
    
    urls = [
        "https://www.wg-gesucht.de/wg-zimmer-in-Wuerzburg.141.0.1.0.html",
        "https://www.wg-gesucht.de/wohnungen-in-Wuerzburg.141.2.1.0.html",
        "https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Wuerzburg.141.1.1.0.html"
    ]
    
    all_listings = scraper.scrape_multiple_urls(urls)
    print(f"Total listings found: {len(all_listings)}")
    
    # Save all listings to a single JSON file
    scraper.save_to_json(all_listings)
