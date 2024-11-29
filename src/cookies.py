from playwright.sync_api import sync_playwright

# Extract cookies from the requests session
cookies = session.cookies.get_dict()

# Use Playwright to open the page and use the session cookies
with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()

    # Set cookies in Playwright
    context.add_cookies([{'name': k, 'value': v, 'domain': 'www.example.com'} for k, v in cookies.items()])

    page = context.new_page()
    page.goto('https://www.example.com/wiki/Page_Title')

    # Optionally, generate a PDF of the page
    page.pdf(path='page.pdf')

    browser.close()
