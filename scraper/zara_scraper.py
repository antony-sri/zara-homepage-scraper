"""
Zara Homepage Scraper - Ticket 2 Implementation
===============================================

This module implements a comprehensive scraper for Zara homepage with:
- HTML and screenshot saving
- Proper logging with timestamps
- Error handling
- Configurable output directory
- Cookie popup handling

Author: Learning Project
Date: 2025
"""

import asyncio
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import hashlib

# Playwright for web scraping
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
# Rich for better console output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
# Loguru for advanced logging
from loguru import logger

# Configuration constants
ZARA_HOME_URL = "https://www.zara.com/"
LOCALE = "en-US"
BROWSER_TYPE = "chromium"
HEADLESS = True

# Output directories
OUTPUT_DIR = Path("data/scrapes")
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
    LOGS_DIR / "scraper_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

console = Console()

class ZaraScraper:
    """
    Main scraper class for Zara homepage
    """
    
    def __init__(self, headless: bool = True, locale: str = "en-US"):
        """
        Initialize the scraper
        
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
            "url": ZARA_HOME_URL,
            "locale": self.locale,
            "success": False,
            "html_file": None,
            "screenshot_file": None,
            "banners_found": 0,
            "errors": []
        }
        
        logger.info(f"Initialized ZaraScraper with timestamp: {self.timestamp}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - no cleanup needed"""
        pass
    
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
    
    # Cleanup method removed - browser will be managed manually
    
    async def _handle_page_error(self, error) -> None:
        """Handle page errors"""
        error_msg = f"Page error: {error}"
        logger.error(error_msg)
        self.scrape_data["errors"].append(error_msg)
    
    async def _handle_request_failed(self, request) -> None:
        """Handle failed requests"""
        error_msg = f"Request failed: {request.url} - {request.failure.get('errorText', 'Unknown error')}"
        logger.warning(error_msg)

    async def handle_cookie_popup(self) -> bool:
        """
        Handle cookie consent popup
        
        This method looks for and handles various types of cookie popups:
        - Accept buttons
        - Cookie consent banners
        - Privacy policy popups
        
        Returns:
            bool: True if popup was handled, False otherwise
        """
        try:
            console.print("[yellow]🔍 Looking for cookie popup...[/yellow]")
            logger.info("Checking for cookie popup")
            
            # Wait a bit for popup to appear
            await asyncio.sleep(2)
            
            # Common cookie popup selectors
            cookie_selectors = [
                "button[data-testid='cookie-accept']",
                "button:has-text('Accept')",
                "button:has-text('Accept All')",
                "button:has-text('I Accept')",
                "button:has-text('OK')",
                "[data-testid='cookie-banner'] button",
                ".cookie-accept",
                "#cookie-accept",
                "button[aria-label*='Accept']",
                "button[aria-label*='Cookie']"
            ]
            
            for selector in cookie_selectors:
                try:
                    # Check if element exists
                    element = self.page.locator(selector)
                    if await element.count() > 0:
                        await element.first.click()
                        console.print(f"[green]✅ Cookie popup handled with selector: {selector}[/green]")
                        logger.info(f"Cookie popup handled with selector: {selector}")
                        return True
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
            
            # Try role-based approach
            try:
                accept_button = self.page.get_by_role("button", name=lambda n: n and any(
                    word in n.lower() for word in ["accept", "ok", "agree", "continue"]
                ))
                if await accept_button.count() > 0:
                    await accept_button.first.click()
                    console.print("[green]✅ Cookie popup handled via role[/green]")
                    logger.info("Cookie popup handled via role")
                    return True
            except Exception as e:
                logger.debug(f"Role-based approach failed: {str(e)}")
            
            console.print("[blue]ℹ️ No cookie popup found or already handled[/blue]")
            logger.info("No cookie popup found or already handled")
            return False
            
        except Exception as e:
            error_msg = f"Error handling cookie popup: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            logger.error(error_msg)
            self.scrape_data["errors"].append(error_msg)
            return False
    
    async def navigate_to_homepage(self) -> bool:
        """
        Navigate to Zara homepage
        
        This method:
        1. Navigates to the homepage
        2. Waits for page to load
        3. Handles cookie popup
        4. Verifies page loaded correctly
        
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            console.print(f"[blue]🌐 Navigating to {ZARA_HOME_URL}...[/blue]")
            logger.info(f"Navigating to {ZARA_HOME_URL}")
            
            # Navigate to homepage
            await self.page.goto(
                ZARA_HOME_URL,
                wait_until="networkidle",
                timeout=30000  # 30 seconds timeout
            )
            
            # Wait for page to be fully loaded
            await self.page.wait_for_load_state("domcontentloaded")
            
            # Handle cookie popup
            await self.handle_cookie_popup()
            
            # Verify page loaded correctly
            title = await self.page.title()
            if "zara" in title.lower():
                console.print(f"[green]✅ Successfully loaded: {title}[/green]")
                logger.info(f"Successfully loaded page: {title}")
                return True
            else:
                console.print(f"[yellow]⚠️ Unexpected page title: {title}[/yellow]")
                logger.warning(f"Unexpected page title: {title}")
                return False
                
        except Exception as e:
            error_msg = f"Failed to navigate to homepage: {str(e)}"
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
            html_filename = f"zara_homepage_{self.timestamp}.html"
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
            screenshot_filename = f"zara_homepage_{self.timestamp}.png"
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

    async def extract_hero_banners(self) -> List[Dict[str, str]]:
        """
        Extract hero banners from the homepage
        
        This method:
        1. Waits for page to be fully loaded
        2. Looks for hero banner elements
        3. Extracts text and links
        4. Returns structured data
        
        Returns:
            List[Dict[str, str]]: List of banner data
        """
        try:
            console.print("[blue]🔍 Extracting hero banners...[/blue]")
            logger.info("Extracting hero banners")
            
            # Wait for page to be fully loaded
            await self.page.wait_for_load_state("networkidle")
            
            # Look for hero banner elements
            # Zara homepage uses dynamic content; we target anchor tags in hero sections
            locator = self.page.locator("a:visible").filter(has_text="SHOP")
            banners: List[Dict[str, str]] = []
            
            count = await locator.count()
            console.print(f"[blue]Found {count} potential banner elements[/blue]")
            
            # Extract data from first 20 elements
            for i in range(min(count, 20)):
                try:
                    element = locator.nth(i)
                    href = await element.get_attribute("href")
                    text = await element.inner_text()
                    
                    if href and text.strip():
                        banner_data = {
                            "text": text.strip(),
                            "href": href,
                            "index": i
                        }
                        banners.append(banner_data)
                        
                except Exception as e:
                    logger.debug(f"Error extracting banner {i}: {str(e)}")
                    continue
            
            console.print(f"[green]✅ Extracted {len(banners)} banners[/green]")
            logger.info(f"Extracted {len(banners)} banners")
            
            # Update scrape data
            self.scrape_data["banners_found"] = len(banners)
            
            return banners
            
        except Exception as e:
            error_msg = f"Failed to extract banners: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            logger.error(error_msg)
            self.scrape_data["errors"].append(error_msg)
            return []
    
    async def run_scrape(self) -> Dict:
        """
        Main scraping method
        
        This method orchestrates the entire scraping process:
        1. Navigate to homepage
        2. Handle cookie popup
        3. Save HTML
        4. Save screenshot
        5. Extract data
        6. Log results
        
        Returns:
            Dict: Complete scraping results
        """
        try:
            console.print(Panel.fit(
                "[bold blue]Zara Homepage Scraper - Ticket 2[/bold blue]\n"
                f"Timestamp: {self.timestamp}\n"
                f"URL: {ZARA_HOME_URL}\n"
                f"Locale: {self.locale}",
                title="🚀 Starting Scrape"
            ))
            
            logger.info("Starting Zara homepage scrape")
            
            # Step 1: Navigate to homepage
            if not await self.navigate_to_homepage():
                self.scrape_data["success"] = False
                return self.scrape_data
            
            # Step 2: Save HTML
            html_file = await self.save_html()
            
            # Step 3: Save screenshot
            screenshot_file = await self.save_screenshot()
            
            # Step 4: Extract data
            banners = await self.extract_hero_banners()
            
            # Step 5: Update final status
            self.scrape_data["success"] = True
            self.scrape_data["banners"] = banners
            
            # Step 6: Display results
            self._display_results()
            
            console.print(Panel.fit(
                "[bold green]✅ Scraping Completed Successfully![/bold green]",
                title="🎉 Success"
            ))
            
            logger.info("Scraping completed successfully")
            return self.scrape_data
            
        except Exception as e:
            error_msg = f"Scraping failed: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            logger.error(error_msg)
            self.scrape_data["errors"].append(error_msg)
            self.scrape_data["success"] = False
            return self.scrape_data
    
    def _display_results(self) -> None:
        """Display scraping results in a nice format"""
        try:
            # Create results table
            table = Table(title="📊 Scraping Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Status", "✅ Success" if self.scrape_data["success"] else "❌ Failed")
            table.add_row("Timestamp", self.scrape_data["timestamp"])
            table.add_row("HTML File", self.scrape_data["html_file"] or "❌ Not saved")
            table.add_row("Screenshot", self.scrape_data["screenshot_file"] or "❌ Not saved")
            table.add_row("Banners Found", str(self.scrape_data["banners_found"]))
            table.add_row("Errors", str(len(self.scrape_data["errors"])))
            
            console.print(table)
            
            # Display banners if any
            if self.scrape_data.get("banners"):
                banner_table = Table(title="🎯 Extracted Banners")
                banner_table.add_column("Index", style="cyan")
                banner_table.add_column("Text", style="green")
                banner_table.add_column("Link", style="blue")
                
                for banner in self.scrape_data["banners"][:5]:  # Show first 5
                    banner_table.add_row(
                        str(banner["index"]),
                        banner["text"][:50] + "..." if len(banner["text"]) > 50 else banner["text"],
                        banner["href"][:50] + "..." if len(banner["href"]) > 50 else banner["href"]
                    )
                
                if len(self.scrape_data["banners"]) > 5:
                    banner_table.add_row("...", f"... and {len(self.scrape_data['banners']) - 5} more", "...")
                
                console.print(banner_table)
            
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
    Main function to run the scraper
    
    This function:
    1. Creates scraper instance
    2. Runs the scraping process
    3. Handles cleanup
    4. Returns results
    """
    try:
        # Create and run scraper
        async with ZaraScraper(headless=HEADLESS, locale=LOCALE) as scraper:
            results = await scraper.run_scrape()
            return results
            
    except Exception as e:
        console.print(f"[red]❌ Main function error: {str(e)}[/red]")
        logger.error(f"Main function error: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Run the scraper
    results = asyncio.run(main())
    
    # Exit with appropriate code
    exit(0 if results.get("success") else 1)
