from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

# Define the product to be scraped
product = 'candles'

# Define the URL to be scraped
url = f"https://www.amazon.com/s?k={product.replace(' ', '+')}&ref=nb_sb_noss_2"

# Define the webdriver service and options
service = Service('path/to/chromedriver')
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# Create the webdriver instance
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

# Visit the URL
driver.get(url)

# Scroll down to load more products
while True:
    try:
        # Wait for the "Next" button to appear
        next_button = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='s-pagination-container']/span[last()-1]")))
        # Scroll to the bottom of the page to load more products
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Click the "Next" button
        next_button.click()
    except:
        break

# Find all the product links on the page
soup = BeautifulSoup(driver.page_source, 'html.parser')
product_links = []
for link in soup.find_all('a', {'class': 'a-link-normal s-no-outline'}):
    product_links.append('https://www.amazon.com' + link.get('href'))

# Create an empty list to store product data
data = []

# Visit each product link and scrape product data
for link in product_links:
    driver.get(link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Get the product title
    try:
        title = soup.find('span', {'id': 'productTitle'}).text.strip()
    except:
        title = 'Not available'

    # Check if the product name is in the title
    if product.lower() not in title.lower():
        continue

    # Get the product description
    try:
        desc = soup.find('div', {'id': 'productDescription'}).text.strip()
    except:
        desc = 'Not available'

    # Get the review data
    try:
        reviews = soup.find_all('div', {'data-hook': 'review'})
        for review in reviews:
            rating = review.find('i', {'data-hook': 'review-star-rating'}).text.strip()
            date = review.find('span', {'data-hook': 'review-date'}).text.strip()
            text = review.find('span', {'data-hook': 'review-body'}).text.strip()
            data.append((title, desc, rating, date, text))
    except:
        continue

# Create a dataframe from the scraped data
df = pd.DataFrame(data, columns=['Product', 'Description', 'Rating', 'Date', 'Review'])

# Save the dataframe to a CSV file
df.to_csv(f'{product.replace(" ", "_")}_reviews.csv', index=False)

# Close the webdriver instance
driver.quit()
