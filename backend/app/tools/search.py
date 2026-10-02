from ddgs import DDGS
from langchain.tools import tool

# this tools enables AI Agent to search DuckDuckGo for latest information

@tool
def web_search(query: str) -> str:
    """Search the web for current information using DuckDuckGo."""
    results = DDGS().text(
        query,
        max_results=5
    )

    if not results:
        return "No results were found!"

    # creatig a list results with proper formatting
    formatted_results = []

    for result in results:
        title = result.get("title", "")
        body = result.get("body", "")
        url = result.get("href", "")

        formatted_results.append(
            f"Title: {title}\n"
            f"Body: {body}\n"
            f"URL: {url}\n"
        )

    return "\n\n".join(formatted_results)