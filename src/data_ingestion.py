import os, pandas as pd
from src.logger import get_logger
from google.cloud import storage
from sklearn.model_selection import train_test_split
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, config):
        self.config = config['data_ingestion']
        self.bucket_name = self.config['bucket_name']
        self.file_name = self.config['bucket_file_name']
        self.train_test_ratio = self.config['train_ratio']

        os.makedirs(RAW_DIR, exist_ok=True)

        logger.info(f"DataIngestion initialized with config: {self.bucket_name} and file {self.file_name}")

    def download_csv_from_gcp(self):
        try:
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.file_name)
            blob.download_to_filename(RAW_FILE_PATH)
            logger.info(f"Downloaded SUCCESSFULLY {self.file_name} from GCP bucket {self.bucket_name} to {RAW_FILE_PATH}")
        except Exception as e:
            logger.error(f"Error occurred while downloading file from GCP: {e}")
            raise CustomException("Failed to download file from GCP: " , e)

    def split_data(self):
        try:
            logger.info(f"Starting data split with train_test_ratio: {self.train_test_ratio}")
            data = pd.read_csv(RAW_FILE_PATH)
            train_df, test_df = train_test_split(data, test_size=1 - self.train_test_ratio, random_state=42)
            train_df.to_csv(TRAIN_FILE_PATH, index=False)
            test_df.to_csv(TEST_FILE_PATH, index=False)
            logger.info(f"Data split into train and test sets with ratio {self.train_test_ratio}. Train data saved to {TRAIN_FILE_PATH}, Test data saved to {TEST_FILE_PATH}")
        except Exception as e:
            logger.error(f"Error occurred while splitting data: {e}")
            raise CustomException("Failed to split data: " , e)

    def run(self):
        try:
            logger.info("Starting data ingestion process...")
            self.download_csv_from_gcp()
            self.split_data()
            logger.info("Data ingestion process completed successfully.")
        except Exception as e:
            logger.error(f"Error occurred during data ingestion: {e}")
            raise CustomException("Failed to complete data ingestion process: " , e)

        finally:
            logger.info("Data ingestion process finished.")

if __name__ == "__main__":
    try:
        config = read_yaml(CONFIG_PATH)
        data_ingestion = DataIngestion(config)
        data_ingestion.run()
    except Exception as e:
        logger.error(f"Error occurred in main execution: {e}")
        raise CustomException("Failed in main execution: " , e)


