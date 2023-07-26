import logging
import logging.config

# Load the Logging Configuration File
logging.config.fileConfig(fname='util/logging_to_file.conf')

# Get the custom Logger from Configuration File
logger = logging.getLogger(__name__)

class DataFrameValidator:
    def __init__(self, df):
        self.df = df

    def df_show_schema(self):
        try:
            logging.info(f"The DataFrame Schema Validation...")
            sch = self.df.schema.fields
            logging.info(f"The DataFrame schema is: ")
            for i in sch:
                logging.info(f"\t{i}")
        except Exception as e:
            logging.error("Error in the method - df_show_schema(). Please check the Stack Trace. " + str(e))
            raise e
        else:
            logging.info("The DataFrame Schema Validation is completed.")

    def validate_lowest_price(self):
        try:
            logging.info("Validating the lowest price...")
            price_cols = [col for col in self.df.columns if 'price' in col]
            df = self.df[price_cols]
            check_result = df[price_cols].ge(df['current_lowest_price'], axis=0).all(axis=1)
            false_count = (~check_result).sum()
        except Exception as e:
            logging.error(f"There was an issue with the method validate_lowest_price: {e}")
            raise e
        else:
            logging.info(f"There are {false_count} price(s) where current_lowest_price is greater than the other stored prices.")
        return false_count

    def check_for_dupes(self):
        try:
            logging.info("Counting duplicate rows...")
            duplicate_rows = self.df.duplicated()
            num_of_dupes = duplicate_rows.sum()
        except Exception as e:
            logging.error(f"There was an issue with the method check_for_dupes(): {e}")
            raise e
        else:
            logging.info(f"There are {num_of_dupes} duplicated row(s) that will be removed.")
        return num_of_dupes

    def count_nulls(self):
        try:
            logging.info("Counting number of null values by column...")
            # Initialize a dictionary to hold the null counts
            null_count_dict = {}
            # Count nulls in each column
            null_counts = self.df.isnull().sum()

            # Print the count for each column
            for column, null_count in null_counts.iteritems():
                null_count_dict[column] = null_count
        except Exception as e:
            logging.error(f"There is an issue with the method count_nulls(): {e}")
            raise e 
        else:
            for key, value in null_count_dict.items():
                logging.info(f"Column {key} has {value} null value(s).")
        return null_count_dict

    def row_count(self):
        try:
            logging.info("Getting the total row count...")            
            df_count = len(self.df)
        except Exception as e:
            logging.error(f"There was an error with the method row_count(): {e}")
            raise e
        else:
            logging.info(f"There are {df_count} row(s) in this table.")
        return df_count
