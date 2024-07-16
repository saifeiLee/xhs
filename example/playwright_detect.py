from playwright.sync_api import sync_playwright
import time


def detect_playwright():
    stealth_js_path = "/Users/lisaifei/code/js/stealth.min.js/stealth.min.js"
    local_chrome_path = f"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(headless=False, executable_path=local_chrome_path, user_data_dir="/tmp/playwright")
        # browser_context = browser.new_context(
        #     viewport={"width": 1920, "height": 1080},
        #     user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        # )
        browser.add_init_script(path=stealth_js_path)
        page = browser.new_page()
        page.goto("https://bot.sannysoft.com/")
        time.sleep(1000)
        browser.close()


if __name__ == "__main__":
    detect_playwright()
