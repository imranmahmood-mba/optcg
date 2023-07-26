import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time 
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
import os
from datetime import datetime
import csv 
import logging
import logging.config
import tcg_data_preprocessing as pp
import numpy as np
import time
from selenium.common.exceptions import TimeoutException

# Load the Logging Configuration File
logging.config.fileConfig(fname='util/logging_to_file.conf')

# Get the custom Logger from Configuration File
logger = logging.getLogger(__name__)

def write_csv(file_name, dict_data):
    """
    Writes a list of dictionaries to a CSV file.

    Args:
        file_name (str): The name of the CSV file.
        dict_data (list): A list of dictionaries containing the data to write to the CSV file.

    Raises:
        Exception: If an error occurs while writing to the CSV file.

    Returns:
        None
    """
    try:
        if not os.path.isfile(file_name):
            with open(file_name, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=dict_data[0].keys())
                writer.writeheader()
                for dict_data in dict_data:
                    writer.writerow(dict_data)
        else: # if file does exist then append without writing the header
            with open(file_name, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=dict_data[0].keys())
                for dict_data in dict_data:
                    writer.writerow(dict_data)
    except Exception as e:
        logger.error(f'Error in the method write_csv(): {e}')
        raise e
    else:
        logger.info(f'Successful write to {file_name} was successful.')

def get_todays_date():
    """
    Get today's date and return it in two different formats.

    Returns:
        formatted_date (str): The current date formatted as 'YYYYMMDD'.
        hyphenated_formatted_date (str): The current date formatted as 'YYYY-MM-DD'.
    """
    try:
        current_date = datetime.now()
        formatted_date = current_date.strftime('%Y%m%d')
        hyphenated_formatted_date = current_date.strftime('%Y-%m-%d')
    except Exception as e:
        logger.error(f'Error in the method get_todays_date(): {e}')
        raise e
    else:
        logger.info(f"Today's date is {hyphenated_formatted_date}")
    return formatted_date, hyphenated_formatted_date

def create_driver():
    """
    Creates and returns a Chrome driver with specified options.

    Returns:
        driver (WebDriver): The created Chrome driver.

    Raises:
        Exception: If there is an error while creating the driver.
    """
    try:
        # Setup Chrome options
        logging.info("Creating driver")
        chrome_options = Options()
        chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.set_capability("browserVersion", "98")

        webdriver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    except Exception as e:
        logger.error(f"Failed to start the Chrome driver. Exception: {e}")
        raise e
    else:
        logger.info("Driver successfully created.")
    return driver


def download_elements_from_webpage(driver, url):
    """
    Downloads elements from a webpage using the given driver and URL.

    Args:
        driver: The web driver used to access the webpage.
        url: The URL of the webpage to download elements from.

    Returns:
        A list of elements downloaded from the webpage.

    Raises:
        Exception: If there is an error while downloading elements.

    Example usage:
        elements = download_elements_from_webpage(driver, "https://www.example.com")
    """
    attempts = 0
    wait_time = 12
    max_attempts = 3
    
    while attempts < max_attempts:
        try:
            driver.get(url)
            logging.info("Accessing website...")
            
            # wait for the page to load completely
            wait = WebDriverWait(driver, wait_time)

            # find all the elements
            elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.search-result__content > a")))
            logging.info(f"Elements from {url} successfully loaded.")
            
            return elements
        except TimeoutException as e:
            attempts += 1
            logging.error(f"Attempt {attempts} error in the method download_elements_from_webpage(): {e}")
            if attempts >= max_attempts:
                raise e
            else:
                logging.info(f"Retrying in {wait_time} seconds.")
                wait_time += attempts
        except Exception as e:
            logging.error(f"Error in the method download_elements_from_webpage(): {e} \n URL: {url}")
            raise e
        
    

def get_max_page_number(driver):
    """
    Get the maximum page number from a web page.

    Args:
        driver: The WebDriver instance.

    Returns:
        A list of integers representing the range of page numbers from 1 to the maximum page number.

    Raises:
        Exception: If there is an error getting the maximum page number.
    """

    wait_time = 12
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        try:
            logging.info("Getting last page number...")
            wait = WebDriverWait(driver, wait_time)

            # identify last page number by xpath
            page_number = wait.until(EC.presence_of_all_elements_located((By.XPATH, "/html/body/div[2]/div/div/section[2]/section/section/section/div[2]/div[1]/div/a[6]/span")))[0].text
            logging.info(f"Successfully generate last page. Number is {page_number}")
            
            return list(range(1, int(page_number) + 1)) # return the page max number of pages
        except AttributeError as e:
            attempts += 1
            logging.error(f"Attempt {attempts} error in the method get_max_page_number(): {e}")
            if attempts >= max_attempts:
                raise e
            else:
                logging.info(f"Retrying attempt: {attempts}")
                wait_time += attempts               
        # Get the text from the element
        except Exception as e:
            logging.error(f"Error in the method get_max_page_number(): {e}")
            raise e 

    
def get_card_data(elements, driver, date):
    """
    Get the card data from a list of elements.

    Args:
        elements: A list of elements to get the card data from.
        driver: The WebDriver instance.
        date: The current date.

    Returns:
        A list of dictionaries containing the card data.

   Raises:
        StaleElementReferenceException: If a stale element reference exception occurs when clicking on a web element.
        Exception: If any other exception occurs during the execution of the function.
    Example Usage:
        elements = driver.find_elements(By.CSS_SELECTOR, "div.search-result__content > a")
        card_data = get_card_data(elements, driver, '2021-10-01') """
    
    logging.info("Getting card data...")
    card_list=[]

    wait_time = 12
    attempts = 0
    max_attempts = 3
    # iterate over each element and click on it
    while attempts < max_attempts:
        for i in range(len(elements)):
            try:
                # initiate empty dict to store card data
                # find all the elements again to avoid StaleElementReferenceException
                
                wait = WebDriverWait(driver, wait_time)
                elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.search-result__content > a")))
                
                elements = driver.find_elements(By.CSS_SELECTOR, "div.search-result__content > a")

                # click on the element
                elements[i].click()
                
                # Perform the operations you want on the new page
                time.sleep(wait_time)

                # You can use driver.page_source to get the HTML content of the page 
                # after all JavaScript has been executed

                html = driver.page_source

                # Then, you can parse this HTML as usual using BeautifulSoup

                soup = BeautifulSoup(html, 'html.parser')

                # Now you can select elements from the soup object as usual
                
                current_lowest_listed_price = pp.convert_to_number(soup.find('span', {'class': 'spotlight__price'}).text)
                logging.info("Current lowest price collected...")
                
                product_name = soup.find('h1', {'class': 'product-details__name'}).text
                name = pp.get_card_name(product_name)
                logging.info("Product name collected...")
                
                product_set = re.split('- ', product_name, maxsplit=1)[1].strip()
                logging.info("Product set collected...")
                
                prices_section = soup.find('section', class_='price-points price-guide__points')
                scraped_prices = [pp.convert_to_number(span.text) for span in prices_section.find_all('span', class_='price')]
                #prices = [pp.convert_to_number(price.text) for price in scraped_prices]
                logging.info("Prices collected...")
                
                card_type = pp.get_card_type(product_name)

                card = {
                    'full_product_name': product_name,
                    'name': name,
                    'type': card_type,
                    'set': product_set,
                    'current_lowest_price': current_lowest_listed_price,
                    'normal_market_price': np.nan,
                    'foil_market_price': np.nan,
                    'normal_buylist_price': np.nan,
                    'foil_buylist_price': np.nan,
                    'normal_listed_median_price': np.nan,
                    'foil_listed_median_price': np.nan,
                    'date': date }
            
                price_names = ['normal_market_price', 'foil_market_price', 'normal_buylist_price', 'foil_buylist_price', 
                            'normal_listed_median_price', 'foil_listed_median_price']

                for price_name, price_value in zip(price_names, scraped_prices):
                    card[price_name] = price_value
                
                card_list.append(card) # add the dictionary containing all of the card data to the card_list variable 

                # navigate back to the original page
                driver.back()
            except AttributeError as e:
                attempts += 1
                logging.error(f'Error with get_card_data() method: {e}')
                if attempts >= max_attempts:
                    raise e
                else:
                    logging.info(f'Retrying attempt: {attempts}...')
                    wait_time += 1
            except StaleElementReferenceException as e:
                logging.error(f'Error with get_card_data() method: {e}')
                # this can occur if a page change occurs before the .click() command is executed
                continue
            except Exception as e:
                logging.error(f'Error with get_card_data() method: {e}') 
                raise e
            else:
                logging.info(f"Card data was successfully scraped for {len(card_list)} cards.")
        return card_list
    

    