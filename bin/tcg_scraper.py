import pandas as pd
import os
import tcg_scraper_functions as tcg
import logging
import logging.config
from upload_to_s3 import upload_file
import tcg_validations as vtcg

# Load the Logging Configuration File
logging.config.fileConfig(fname='util/logging_to_file.conf')

# Get the custom Logger from Configuration File
logger = logging.getLogger(__name__)

def main():
    """
    Main function to run the scraper
    """
    try:
        print("executing script")
        bucket = os.getenv('S3_OPTCG_BUCKET_NAME')
        logging.info("Executing main function.")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir) # gets parent directory for saving the file
        file_date, date_column = tcg.get_todays_date() 
        file_path = f'{parent_dir}/output/optcg_data_{file_date}.csv'

        driver = tcg.create_driver()
        elements = tcg.download_elements_from_webpage(driver, url="https://www.tcgplayer.com/search/one-piece-card-game/product?productLineName=one-piece-card-game&page=1&view=grid&ProductTypeName=Cards")
        page_nums = tcg.get_max_page_number(driver) # get the max number of pages to scrape

        for page in page_nums:
            url = f"https://www.tcgplayer.com/search/one-piece-card-game/product?productLineName=one-piece-card-game&page={page}&view=grid&ProductTypeName=Cards"
            elements = tcg.download_elements_from_webpage(driver, url=url) # get the webpage elements to scrape
            card_data = tcg.get_card_data(elements, driver, date_column) # scrape card data from page
            tcg.write_csv(file_path, card_data)

        # Validate the data 
        logging.info("Starting data validation...")
        df = pd.read_csv(file_path)
        df_validator = vtcg.DataFrameValidator(df)
        df_validator.df_show_schema()
        df_validator.validate_lowest_price()
        df_validator.check_for_dupes()
        df_validator.count_nulls()
        df_validator.row_count()
        logging.info("Validation completed...")

        logging.info("Removing duplicates...")
        df = df.drop_duplicates()
        logging.info("Duplicates removed...")

        # once data is scraped, load files to s3 
        #logging.info("Loading data into s3 bucket...")
        #upload_file(file_path, bucket=bucket) # upload today's data to s3
        #upload_file(file_name='../logs/tcg_pipeline.log', bucket=bucket) # upload logs to s3
        logging.info("Logging completed...")

    except Exception as e:
        logging.error(f"Error occured in the main() method. Please check the Stack Trace to go to the respective module and fix it {str(e)}",
                      exc_info=True)
        raise e
    else:
        logging.info("TCG Pipeline script is completed.")
if __name__== "__main__":
    main()