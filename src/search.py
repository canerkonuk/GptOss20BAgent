"""
Search functionality using DuckDuckGo
Provides free web search capabilities
"""

from ddgs import DDGS
import config
from typing import List, Dict


class SearchEngine:
    """DuckDuckGo search wrapper"""

    def __init__(self):
        """Initialize search engine"""
        self.config = config.SEARCH_CONFIG

    def search(self, query: str, max_results: int = None) -> tuple[bool, List[Dict] | str]:
        """
        Perform a web search

        Args:
            query: Search query string
            max_results: Number of results to return (uses config default if None)

        Returns:
            (success: bool, results: List[Dict] or error_message: str)
        """
        if not query or not query.strip():
            return False, "Search query cannot be empty"

        if max_results is None:
            max_results = self.config["max_results"]

        try:
            print(f"Searching for: {query}")

            # Initialize DDGS and perform search
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    query=query,
                    region=self.config["region"],
                    safesearch=self.config["safesearch"],
                    max_results=max_results
                ))

            if not results:
                return False, "No results found"

            print(f"Found {len(results)} results")
            return True, results

        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            print(error_msg)
            return False, error_msg

    def format_results(self, results: List[Dict]) -> str:
        """
        Format search results into readable text

        Args:
            results: List of search result dictionaries

        Returns:
            Formatted string of results
        """
        if not results:
            return "No results to format"

        formatted = []
        for idx, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("href", "No URL")
            snippet = result.get("body", "No description")

            formatted.append(f"**Result {idx}:**")
            formatted.append(f"Title: {title}")
            formatted.append(f"URL: {url}")
            formatted.append(f"Description: {snippet}")
            formatted.append("")  # Empty line between results

        return "\n".join(formatted)

    def search_and_format(self, query: str, max_results: int = None) -> tuple[bool, str]:
        """
        Search and return formatted results

        Args:
            query: Search query
            max_results: Number of results

        Returns:
            (success: bool, formatted_results: str)
        """
        success, results = self.search(query, max_results)

        if not success:
            return False, results  # results contains error message

        formatted = self.format_results(results)
        return True, formatted


# Global search engine instance
search_engine = None

def get_search_engine() -> SearchEngine:
    """Get the global search engine instance"""
    global search_engine
    if search_engine is None:
        search_engine = SearchEngine()
    return search_engine


def perform_search(query: str) -> str:
    """
    Convenience function to perform search and return formatted results

    Args:
        query: Search query

    Returns:
        Formatted search results or error message
    """
    engine = get_search_engine()
    success, results = engine.search_and_format(query)

    if success:
        return results
    else:
        return f"Search failed: {results}"
