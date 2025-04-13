from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

url_to_scrap = 'https://www.google.com/search?q=air+pollution+night+&sca_esv=0843d60fe31b3c05&bih=793&biw=1536&rlz=1C1CHBF_enCA918CA918&udm=2&sxsrf=AHTn8zoEYh6FIdSglfWhwanPb_POGKHXug%3A1744209773478&ei=bYf2Z_PxHKXgseMPysfpoQ0&ved=0ahUKEwiz3Njfl8uMAxUlcGwGHcpjOtQQ4dUDCBE&uact=5&oq=air+pollution+night+&gs_lp=EgNpbWciFGFpciBwb2xsdXRpb24gbmlnaHQgMgcQIxgnGMkCMgYQABgHGB5IlgtQ2wlY2wlwAngAkAEAmAHCAaAB7gKqAQMwLjK4AQPIAQD4AQGYAgSgAv8CmAMAiAYBkgcDMi4yoAeMBbIHAzAuMrgH-AI&sclient=img'
file_name = 'nightPoll2'
delay_wait = 5
max_scroll = 10

# Initialize the Selenium WebDriver (Chrome in this case)
driver = webdriver.Chrome()

# Open the website (use the URL of the page where images are located)
driver.get(url_to_scrap)

# Scroll down to load more images (optional, but useful if images are lazy-loaded)
def scroll_page():
    # Scroll down a little to trigger lazy loading
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(delay_wait)  # Wait for the page to load new images

# Function to get the image URLs
def get_image_urls():
    image_urls = []
    # Find all <g-img> elements with class 'mNsIhb'
    img_elements = driver.find_elements(By.CSS_SELECTOR, "g-img.mNsIhb img")

    for img in img_elements:
          img_url = img.get_attribute("src")  # Get the 'src' attribute (image URL)
          if img_url:
               image_urls.append(img_url)

    return image_urls

# Scroll and scrape image URLs (you can set how many times you want to scroll)
image_urls = []

for _ in range(max_scroll):  # Scroll 5 times, adjust as needed
    image_urls.extend(get_image_urls())
    scroll_page()

# Remove duplicate URLs (optional)
image_urls = list(set(image_urls))

# Save the URLs to a text file
with open(f"{file_name}image_urls.txt", "w") as file:
    for url in image_urls:
        file.write(url + "\n")

print(f"Scraped {len(image_urls)} image URLs and saved to '{file_name}image_urls.txt'")

# Close the WebDriver
driver.quit()
