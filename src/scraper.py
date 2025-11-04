"""
Web scraping functionality using BeautifulSoup
Extracts and cleans content from web pages
"""

import requests
from bs4 import BeautifulSoup
import config
from typing import Dict


class WebScraper:
    """Web scraper using BeautifulSoup and requests"""

    def __init__(self):
        """Initialize the scraper"""
        self.config = config.SCRAPER_CONFIG
        self.session = requests.Session()
        self.session.headers.update(self.config["headers"])

    def scrape(self, url: str) -> tuple[bool, Dict | str]:
        """
        Scrape content from a URL

        Args:
            url: The URL to scrape

        Returns:
            (success: bool, data: Dict or error_message: str)
        """
        if not url or not url.strip():
            return False, "URL cannot be empty"

        # Basic URL validation
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            print(f"Scraping: {url}")

            # Fetch the page
            response = self.session.get(
                url,
                timeout=self.config["timeout"]
            )
            response.raise_for_status()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, "lxml")

            # Extract data
            data = {
                "url": url,
                "title": self._extract_title(soup),
                "content": self._extract_content(soup),
                "links": self._extract_links(soup, url),
                "metadata": self._extract_metadata(soup),
            }

            print(f"Successfully scraped: {data['title']}")
            return True, data

        except requests.exceptions.Timeout:
            error_msg = f"Timeout: Page took too long to load"
            print(error_msg)
            return False, error_msg

        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            print(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Scraping error: {str(e)}"
            print(error_msg)
            return False, error_msg

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)

        # Try h1 as fallback
        h1_tag = soup.find("h1")
        if h1_tag:
            return h1_tag.get_text(strip=True)

        return "No title found"

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content"""
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "header", "footer"]):
            element.decompose()

        # Get text from main content areas
        main_content = (
            soup.find("main") or
            soup.find("article") or
            soup.find("div", class_="content") or
            soup.find("body")
        )

        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)

        # Clean up excessive whitespace
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        cleaned_text = "\n".join(lines)

        # Token-aware intelligent truncation (head + tail strategy)
        max_length = self.config["max_content_length"]

        if len(cleaned_text) > max_length:
            # Use head+tail strategy to preserve beginning and end context
            head_chars = self.config.get("head_chars", int(max_length * 0.6))
            tail_chars = self.config.get("tail_chars", int(max_length * 0.4))

            # Ensure head + tail don't exceed max_length
            if head_chars + tail_chars > max_length:
                head_chars = int(max_length * 0.6)
                tail_chars = max_length - head_chars

            head = cleaned_text[:head_chars].rstrip()
            tail = cleaned_text[-tail_chars:].lstrip()

            # Add separator to indicate truncation
            separator = f"\n\n... [Content truncated - showing first {head_chars} and last {tail_chars} chars] ...\n\n"
            cleaned_text = head + separator + tail

        return cleaned_text

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extract links from the page"""
        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            text = a_tag.get_text(strip=True)

            # Basic link filtering
            if href.startswith(("http://", "https://")):
                links.append({"text": text, "url": href})

        # Limit number of links
        return links[:20]

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from meta tags"""
        metadata = {}

        # Description
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag and desc_tag.get("content"):
            metadata["description"] = desc_tag["content"]

        # Open Graph tags
        og_title = soup.find("meta", attrs={"property": "og:title"})
        if og_title and og_title.get("content"):
            metadata["og_title"] = og_title["content"]

        og_desc = soup.find("meta", attrs={"property": "og:description"})
        if og_desc and og_desc.get("content"):
            metadata["og_description"] = og_desc["content"]

        return metadata

    def format_scraped_data(self, data: Dict) -> str:
        """
        Format scraped data into readable text

        Args:
            data: Dictionary of scraped data

        Returns:
            Formatted string
        """
        formatted = []

        formatted.append(f"**URL:** {data.get('url', 'N/A')}")
        formatted.append(f"**Title:** {data.get('title', 'N/A')}")
        formatted.append("")

        # Metadata
        metadata = data.get("metadata", {})
        if metadata:
            formatted.append("**Metadata:**")
            for key, value in metadata.items():
                formatted.append(f"  - {key}: {value}")
            formatted.append("")

        # Main content
        content = data.get("content", "")
        if content:
            formatted.append("**Content:**")
            formatted.append(content)
            formatted.append("")

        # Links (first 10 only)
        links = data.get("links", [])
        if links:
            formatted.append(f"**Links Found ({len(links)}):**")
            for link in links[:10]:
                formatted.append(f"  - {link.get('text', 'No text')}: {link.get('url', '')}")

        return "\n".join(formatted)

    def scrape_and_format(self, url: str) -> tuple[bool, str]:
        """
        Scrape URL and return formatted content

        Args:
            url: URL to scrape

        Returns:
            (success: bool, formatted_content: str)
        """
        success, data = self.scrape(url)

        if not success:
            return False, data  # data contains error message

        formatted = self.format_scraped_data(data)
        return True, formatted


# Global scraper instance
scraper = None

def get_scraper() -> WebScraper:
    """Get the global scraper instance"""
    global scraper
    if scraper is None:
        scraper = WebScraper()
    return scraper


def scrape_url(url: str) -> str:
    """
    Convenience function to scrape URL and return formatted content

    Args:
        url: URL to scrape

    Returns:
        Formatted scraped content or error message
    """
    scraper_instance = get_scraper()
    success, content = scraper_instance.scrape_and_format(url)

    if success:
        return content
    else:
        return f"Scraping failed: {content}"
