"""
Demo Scraper - Working Example
==============================

This is a demo scraper that works with a test website to show
the functionality without getting blocked by Zara.

This demonstrates:
- HTML saving
- Screenshot saving
- Logging
- Error handling
- Cookie popup handling
- Data extraction

Author: Learning Project
Date: 2025
"""

import asyncio
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import hashlib

# Playwright for web scraping
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
# Rich for better console output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
# Loguru for advanced logging
from loguru import logger

# Configuration
DEMO_URL = "https://httpbin.org/html"  # Test website that always works
LOCALE = "en-US"
BROWSER_TYPE = "chromium"
HEADLESS = True

# Output directories
OUTPUT_DIR = Path("data/demo_scrapes")
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"
HTML_DIR = OUTPUT_DIR / "html"
LOGS_DIR = OUTPUT_DIR / "logs"

# Ensure output directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
HTML_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logger.add(
    LOGS_DIR / "demo_scraper_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

console = Console()


class DemoScraper:
    """
    Demo scraper class - shows all the functionality
    
    This class demonstrates:
    - Browser initialization and management
    - Page navigation and interaction
    - HTML and screenshot saving
    - Error handling and logging
    - Data extraction
    """
    
    def __init__(self, headless: bool = True, locale: str = "en-US"):
        """
        Initialize the demo scraper
        
        Args:
            headless (bool): Run browser in headless mode
            locale (str): Browser locale setting
        """
        self.headless = headless
        self.locale = locale
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Track scraping results
        self.scrape_data = {
            "timestamp": self.timestamp,
            "url": DEMO_URL,
            "locale": self.locale,
            "success": False,
            "html_file": None,
            "screenshot_file": None,
            "title": None,
            "headings_found": 0,
            "errors": []
        }
        
        logger.info(f"Initialized DemoScraper with timestamp: {self.timestamp}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup"""
        await self.cleanup()
    
    async def start_browser(self) -> None:
        """
        Start the browser and create context
        
        This method:
        1. Launches Chromium browser
        2. Creates a new browser context with locale
        3. Opens a new page
        4. Sets up error handling
        """
        try:
            console.print(f"[blue]🚀 Starting {BROWSER_TYPE} browser...[/blue]")
            logger.info(f"Starting {BROWSER_TYPE} browser")
            
            # Launch browser
            self.browser = await async_playwright().start()
            browser_instance = await self.browser.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor"
                ]
            )
            
            # Create browser context with locale
            self.context = await browser_instance.new_context(
                locale=self.locale,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Create new page
            self.page = await self.context.new_page()
            
            # Set up error handling
            self.page.on("pageerror", self._handle_page_error)
            self.page.on("requestfailed", self._handle_request_failed)
            
            console.print(f"[green]✅ Browser started successfully[/green]")
            logger.info("Browser started successfully")
            
        except Exception as e:
            error_msg = f"Failed to start browser: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            logger.error(error_msg)
            self.scrape_data["errors"].append(error_msg)
            raise
    
    async def cleanup(self) -> None:
        """
        Clean up browser resources
        
        This method ensures proper cleanup of:
        - Browser context
        - Browser instance
        - Playwright instance
        """
        try:
            if self.context:
                await self.context.close()
                logger.info("Browser context closed")
            
            if self.browser:
                await self.browser.stop()
                logger.info("Browser stopped")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def _handle_page_error(self, error) -> None:
        """Handle page errors"""
        error_msg = f"Page error: {error}"
        logger.error(error_msg)
        self.scrape_data["errors"].append(error_msg)
    
    async def _handle_request_failed(self, request) -> None:
        """Handle failed requests"""
        error_msg = f"Request failed: {request.url} - {request.failure.get('errorText', 'Unknown error')}"
        logger.warning(error_msg)
    
    async def navigate_to_page(self) -> bool:
        """
        Navigate to the demo page
        
        This method:
        1. Navigates to the demo page
        2. Waits for page to load
        3. Verifies page loaded correctly
        
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            console.print(f"[blue]🌐 Navigating to {DEMO_URL}...[/blue]")
            logger.info(f"Navigating to {DEMO_URL}")
            
            # Navigate to page
            await self.page.goto(
                DEMO_URL,
                wait_until="networkidle",
                timeout=30000  # 30 seconds timeout
            )
            
            # Wait for page to be fully loaded
            await self.page.wait_for_load_state("domcontentloaded")
            
            # Verify page loaded correctly
            title = await self.page.title()
            self.scrape_data["title"] = title
            
            console.print(f"[green]✅ Successfully loaded: {title}[/green]")
            logger.info(f"Successfully loaded page: {title}")
            return True
                
        except Exception as e:
            error_msg = f"Failed to navigate to page: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            logger.error(error_msg)
            self.scrape_data["errors"].append(error_msg)
            return False
    
    async def save_html(self) -> Optional[str]:
        """
        Save the current page HTML to file
        
        This method:
        1. Gets the page HTML content
        2. Saves it to a timestamped file
        3. Returns the file path
        
        Returns:
            str: Path to saved HTML file, or None if failed
        """
        try:
            console.print("[blue]💾 Saving HTML content...[/blue]")
            logger.info("Saving HTML content")
            
            # Get page HTML
            html_content = await self.page.content()
            
            # Create filename with timestamp
            html_filename = f"demo_page_{self.timestamp}.html"
            html_filepath = HTML_DIR / html_filename
            
            # Save HTML to file
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            console.print(f"[green]✅ HTML saved: {html_filepath}[/green]")
            logger.info(f"HTML saved: {html_filepath}")
            
            # Update scrape data
            self.scrape_data["html_file"] = str(html_filepath)
            
            return str(html_filepath)
            
        except Exception as e:
            error_msg = f"Failed to save HTML: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            logger.error(error_msg)
            self.scrape_data["errors"].append(error_msg)
            return None
    
    async def save_screenshot(self) -> Optional[str]:
        """
        Save a screenshot of the current page
        
        This method:
        1. Takes a full page screenshot
        2. Saves it to a timestamped file
        3. Returns the file path
        
        Returns:
            str: Path to saved screenshot file, or None if failed
        """
        try:
            console.print("[blue]📸 Taking screenshot...[/blue]")
            logger.info("Taking screenshot")
            
            # Create filename with timestamp
            screenshot_filename = f"demo_page_{self.timestamp}.png"
            screenshot_filepath = SCREENSHOTS_DIR / screenshot_filename
            
            # Take full page screenshot
            await self.page.screenshot(
                path=str(screenshot_filepath),
                full_page=True
            )
            
            console.print(f"[green]✅ Screenshot saved: {screenshot_filepath}[/green]")
            logger.info(f"Screenshot saved: {screenshot_filepath}")
            
            # Update scrape data
            self.scrape_data["screenshot_file"] = str(screenshot_filepath)
            
            return str(screenshot_filepath)
            
        except Exception as e:
            error_msg = f"Failed to save screenshot: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            logger.error(error_msg)
            self.scrape_data["errors"].append(error_msg)
            return None
    
    async def extract_data(self) -> List[Dict[str, str]]:
        """
        Extract data from the page
        
        This method:
        1. Waits for page to be fully loaded
        2. Extracts headings and text
        3. Returns structured data
        
        Returns:
            List[Dict[str, str]]: List of extracted data
        """
        try:
            console.print("[blue]🔍 Extracting page data...[/blue]")
            logger.info("Extracting page data")
            
            # Wait for page to be fully loaded
            await self.page.wait_for_load_state("networkidle")
            
            # Extract headings
            headings = await self.page.query_selector_all("h1, h2, h3, h4, h5, h6")
            extracted_data = []
            
            for i, heading in enumerate(headings):
                try:
                    text = await heading.inner_text()
                    tag_name = await heading.evaluate("el => el.tagName.toLowerCase()")
                    
                    if text.strip():
                        data_item = {
                            "type": tag_name,
                            "text": text.strip(),
                            "index": i
                        }
                        extracted_data.append(data_item)
                        
                except Exception as e:
                    logger.debug(f"Error extracting heading {i}: {str(e)}")
                    continue
            
            console.print(f"[green]✅ Extracted {len(extracted_data)} elements[/green]")
            logger.info(f"Extracted {len(extracted_data)} elements")
            
            # Update scrape data
            self.scrape_data["headings_found"] = len(extracted_data)
            
            return extracted_data
            
        except Exception as e:
            error_msg = f"Failed to extract data: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            logger.error(error_msg)
            self.scrape_data["errors"].append(error_msg)
            return []
    
    async def run_scrape(self) -> Dict:
        """
        Main scraping method
        
        This method orchestrates the entire scraping process:
        1. Navigate to page
        2. Save HTML
        3. Save screenshot
        4. Extract data
        5. Log results
        
        Returns:
            Dict: Complete scraping results
        """
        try:
            console.print(Panel.fit(
                "[bold blue]Demo Scraper - Ticket 2 Implementation[/bold blue]\n"
                f"Timestamp: {self.timestamp}\n"
                f"URL: {DEMO_URL}\n"
                f"Locale: {self.locale}",
                title="🚀 Starting Demo Scrape"
            ))
            
            logger.info("Starting demo scrape")
            
            # Step 1: Navigate to page
            if not await self.navigate_to_page():
                self.scrape_data["success"] = False
                return self.scrape_data
            
            # Step 2: Save HTML
            html_file = await self.save_html()
            
            # Step 3: Save screenshot
            screenshot_file = await self.save_screenshot()
            
            # Step 4: Extract data
            extracted_data = await self.extract_data()
            
            # Step 5: Update final status
            self.scrape_data["success"] = True
            self.scrape_data["extracted_data"] = extracted_data
            
            # Step 6: Display results
            self._display_results()
            
            console.print(Panel.fit(
                "[bold green]✅ Demo Scraping Completed Successfully![/bold green]",
                title="🎉 Success"
            ))
            
            logger.info("Demo scraping completed successfully")
            return self.scrape_data
            
        except Exception as e:
            error_msg = f"Demo scraping failed: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            logger.error(error_msg)
            self.scrape_data["errors"].append(error_msg)
            self.scrape_data["success"] = False
            return self.scrape_data
    
    def _display_results(self) -> None:
        """Display scraping results in a nice format"""
        try:
            # Create results table
            table = Table(title="📊 Demo Scraping Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Status", "✅ Success" if self.scrape_data["success"] else "❌ Failed")
            table.add_row("Timestamp", self.scrape_data["timestamp"])
            table.add_row("Title", self.scrape_data["title"] or "N/A")
            table.add_row("HTML File", self.scrape_data["html_file"] or "❌ Not saved")
            table.add_row("Screenshot", self.scrape_data["screenshot_file"] or "❌ Not saved")
            table.add_row("Elements Found", str(self.scrape_data["headings_found"]))
            table.add_row("Errors", str(len(self.scrape_data["errors"])))
            
            console.print(table)
            
            # Display extracted data if any
            if self.scrape_data.get("extracted_data"):
                data_table = Table(title="🎯 Extracted Elements")
                data_table.add_column("Type", style="cyan")
                data_table.add_column("Text", style="green")
                data_table.add_column("Index", style="blue")
                
                for item in self.scrape_data["extracted_data"][:5]:  # Show first 5
                    data_table.add_row(
                        item["type"],
                        item["text"][:50] + "..." if len(item["text"]) > 50 else item["text"],
                        str(item["index"])
                    )
                
                if len(self.scrape_data["extracted_data"]) > 5:
                    data_table.add_row("...", f"... and {len(self.scrape_data['extracted_data']) - 5} more", "...")
                
                console.print(data_table)
            
            # Display errors if any
            if self.scrape_data["errors"]:
                error_panel = Panel(
                    "\n".join([f"• {error}" for error in self.scrape_data["errors"]]),
                    title="⚠️ Errors Encountered",
                    border_style="red"
                )
                console.print(error_panel)
                
        except Exception as e:
            logger.error(f"Error displaying results: {str(e)}")


async def main():
    """
    Main function to run the demo scraper
    
    This function:
    1. Creates scraper instance
    2. Runs the scraping process
    3. Handles cleanup
    4. Returns results
    """
    try:
        # Create and run scraper
        async with DemoScraper(headless=HEADLESS, locale=LOCALE) as scraper:
            results = await scraper.run_scrape()
            return results
            
    except Exception as e:
        console.print(f"[red]❌ Main function error: {str(e)}[/red]")
        logger.error(f"Main function error: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Run the demo scraper
    results = asyncio.run(main())
    
    # Exit with appropriate code
    exit(0 if results.get("success") else 1)
