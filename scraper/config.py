"""
Configuration for Zara Scraper
==============================

This module contains all configuration settings for the scraper.
You can modify these settings to change behavior.
"""

# Target URLs (try different ones if one fails)
ZARA_URLS = [
    "https://www.zara.com/",
    "https://www.zara.com/us/",
    "https://www.zara.com/en/",
    "https://www.zara.com/us/en/",
]

# Default URL to use
DEFAULT_URL = "https://www.zara.com/us/en/"

# Browser settings
BROWSER_SETTINGS = {
    "headless": True,
    "locale": "en-US",
    "timeout": 30000,  # 30 seconds
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "viewport": {"width": 1920, "height": 1080},
    "args": [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--no-first-run",
        "--disable-default-apps",
        "--disable-popup-blocking",
        "--disable-notifications",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-field-trial-config",
        "--disable-ipc-flooding-protection",
        "--enable-features=NetworkService,NetworkServiceLogging",
        "--force-color-profile=srgb",
        "--metrics-recording-only",
        "--no-default-browser-check",
        "--no-pings",
        "--no-zygote",
        "--password-store=basic",
        "--use-mock-keychain",
        "--hide-scrollbars",
        "--mute-audio",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-accelerated-2d-canvas",
        "--no-first-run",
        "--no-zygote",
        "--disable-gpu"
    ]
}

# Cookie popup selectors
COOKIE_SELECTORS = [
    "button[data-testid='cookie-accept']",
    "button:has-text('Accept')",
    "button:has-text('Accept All')",
    "button:has-text('I Accept')",
    "button:has-text('OK')",
    "button:has-text('Continue')",
    "button:has-text('Got it')",
    "[data-testid='cookie-banner'] button",
    ".cookie-accept",
    "#cookie-accept",
    "button[aria-label*='Accept']",
    "button[aria-label*='Cookie']",
    ".accept-cookies",
    "#accept-cookies",
    "button[class*='accept']",
    "button[class*='cookie']",
    ".gdpr-accept",
    "#gdpr-accept"
]

# Output directories
OUTPUT_DIRS = {
    "base": "data/scrapes",
    "html": "data/scrapes/html",
    "screenshots": "data/scrapes/screenshots",
    "logs": "data/scrapes/logs",
    "json": "data/scrapes/json"
}

# Logging settings
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    "rotation": "1 day",
    "retention": "7 days",
    "compression": "zip"
}

# Scraping settings
SCRAPING_CONFIG = {
    "max_retries": 3,
    "retry_delay": 5,  # seconds
    "wait_for_load": 5,  # seconds
    "max_banners": 20,
    "screenshot_quality": 90
}

# Banner extraction selectors
BANNER_SELECTORS = [
    "a:visible:has-text('SHOP')",
    "a[href*='/shop']",
    "a[href*='/collection']",
    ".hero-banner a",
    ".banner a",
    ".promotion a",
    "[data-testid*='banner'] a",
    "[class*='banner'] a",
    "[class*='hero'] a"
]
