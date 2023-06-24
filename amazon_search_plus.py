# imports
from bs4 import BeautifulSoup
from tabulate import tabulate
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# A representation for an Amazon product
class Product:
    def __init__(self, description, price, rating, reviews):
        self.description = description
        self.price = price
        self.rating = rating
        self.reviews = reviews


# Sets up webdriver as a headless Chrome browser
def setup_webdriver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)


# Returns a list of all the products contained in an Amazon HTML page
def parse_html_page(html_page):
    soup = BeautifulSoup(html_page, "html.parser")
    products = []
    for parent in soup.find_all(
        class_="sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20"
    ):
        # Get description
        temp = parent.find(class_="s-image")
        description = temp.get("alt")

        # Get price
        temp = parent.find(class_="a-price")
        price = temp.find("span", class_="a-offscreen").text if temp else None

        # Get rating
        rating = parent.find(class_="a-icon-alt")
        rating = rating.text if rating else None

        # Get number of reviews
        reviews = parent.find(class_="a-size-base s-underline-text")
        reviews = reviews.text if reviews else None

        if temp and price and rating and reviews:
            products.append(Product(description, price, rating, reviews))
    return products


# Displays a table of products
def display_table(products):
    headers = ["Description", "Price", "Rating", "# of Reviews"]
    rows = []
    for product in products:
        row = [product.description, product.price, product.rating, product.reviews]
        rows.append(row)
    table = tabulate(rows, headers, tablefmt="grid")
    print("\n\n\n", table, "\n\n\n")


if __name__ == "__main__":
    # Constants
    URL_TEMPLATE = "https://www.amazon.ca/s?k={search_term}&page={page_num}"
    NUM_OF_PAGES = 3
    MAX_PRICE = 10000000

    # {search_term : products}
    search_cache = {}

    driver = setup_webdriver()
    while True:
        search_term = input("Enter your search term: ")
        if search_term == "exit":
            break
        # Checks to see if the data is already in the cache
        if search_term not in search_cache:
            products = []
            for page_num in range(1, NUM_OF_PAGES + 1):
                url = URL_TEMPLATE.format(search_term=search_term, page_num=page_num)
                # Get HTML page
                driver.get(url)
                # Parse HTML page
                products.extend(parse_html_page(driver.page_source))
            # Sorts the products by price
            products.sort(
                key=lambda product: float(
                    product.price.replace(",", "").replace("$", "")
                )
            )
            search_cache[search_term] = products
        display_table(search_cache[search_term])
    driver.quit()
