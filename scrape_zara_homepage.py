import asyncio
from typing import List, Dict

from playwright.async_api import async_playwright
from rich import print


ZARA_HOME_URL = "https://www.zara.com/"


async def extract_hero_banners(page) -> List[Dict[str, str]]:
    await page.wait_for_load_state("networkidle")
    # Zara homepage uses dynamic content; we target anchor tags in hero sections
    locator = page.locator("a:visible").filter(has_text="SHOP")
    banners: List[Dict[str, str]] = []
    count = await locator.count()
    for i in range(min(count, 20)):
        element = locator.nth(i)
        href = await element.get_attribute("href")
        text = await element.inner_text()
        if href:
            banners.append({"text": text.strip(), "href": href})
    return banners


async def main() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(locale="en-US")
        page = await context.new_page()
        await page.goto(ZARA_HOME_URL, wait_until="load")

        # Accept cookies if prompt exists to avoid blocking content
        try:
            accept = page.get_by_role("button", name=lambda n: n and "accept" in n.lower())
            if await accept.count() > 0:
                await accept.first.click()
        except Exception:
            pass

        banners = await extract_hero_banners(page)
        print({"count": len(banners), "banners": banners})

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())


