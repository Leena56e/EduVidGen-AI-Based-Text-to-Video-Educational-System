from __future__ import annotations

from pathlib import Path
from playwright.sync_api import sync_playwright


def capture_snapshots_from_html(
    html_file: str,
    output_dir: str = "outputs/frames",
    card_selector: str = ".scene-card",
    page_width: int = 1400,
    page_height: int = 1000,
):
    html_path = Path(html_file).resolve()
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": page_width, "height": page_height})

        page.goto(html_path.as_uri(), wait_until="load")
        page.wait_for_timeout(1500)

        cards = page.locator(card_selector)
        count = cards.count()

        if count == 0:
            browser.close()
            raise ValueError(f"No elements found with selector: {card_selector}")

        for i in range(count):
            card = cards.nth(i)
            card.scroll_into_view_if_needed()
            page.wait_for_timeout(300)

            output_path = out_dir / f"frame_{i + 1:03d}.png"
            card.screenshot(path=str(output_path))

        browser.close()

    print(f"Saved {count} snapshots in: {out_dir}")


def main():
    subtopic = input("Enter subtopic (e.g., linked_list): ").strip().lower().replace(" ", "_")
    if not subtopic:
        print("No subtopic entered. Exiting.")
        return

    html_file = f"outputs/html/{subtopic}.html"
    capture_snapshots_from_html(html_file=html_file)


if __name__ == "__main__":
    main()