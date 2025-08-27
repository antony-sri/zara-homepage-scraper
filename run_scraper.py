#!/usr/bin/env python3
"""
Simple script to run the Zara scraper
=====================================

This script runs the enhanced scraper and displays results.
Use this for testing and development.

Usage:
    python run_scraper.py
"""

import asyncio
import sys
from pathlib import Path

# Add the scraper directory to Python path
sys.path.append(str(Path(__file__).parent / "scraper"))

from zara_scraper import main


async def run_test():
    """Run the scraper and display results"""
    print("🚀 Starting Zara Homepage Scraper Test")
    print("=" * 50)
    
    try:
        # Run the scraper
        results = await main()
        
        # Display summary
        print("\n" + "=" * 50)
        print("📊 SCRAPING SUMMARY")
        print("=" * 50)
        print(f"Success: {'✅ Yes' if results.get('success') else '❌ No'}")
        print(f"Timestamp: {results.get('timestamp', 'N/A')}")
        print(f"HTML File: {results.get('html_file', 'Not saved')}")
        print(f"Screenshot: {results.get('screenshot_file', 'Not saved')}")
        print(f"Banners Found: {results.get('banners_found', 0)}")
        print(f"Errors: {len(results.get('errors', []))}")
        
        if results.get('errors'):
            print("\n⚠️ ERRORS:")
            for error in results['errors']:
                print(f"  • {error}")
        
        return results.get('success', False)
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Run the test
    success = asyncio.run(run_test())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
