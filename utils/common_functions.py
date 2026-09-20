import os, pandas as pd, yaml
from src.logger import get_logger
from src.custom_exception import CustomException

logger = get_logger(__name__)

def read_yaml(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, 'r') as yaml_file:
            config = yaml.safe_load(yaml_file)
    except Exception as e:
        logger.error(f"Error occurred while reading YAML file: {file_path}")
        raise CustomException("Failed to read YAML file: " , e)
    logger.info(f"Successfully read YAML file: {file_path}")
    return config

def load_data(file_path):
    try:
        logger.info(f"Loading data from file: {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        data = pd.read_csv(file_path)
        logger.info(f"Data loaded successfully from file: {file_path}, shape: {data.shape}")
    except Exception as e:
        logger.error(f"Error occurred while loading data from file: {file_path}")
        raise CustomException("Failed to load data from file: " , e)
    logger.info(f"Successfully loaded data from file: {file_path}")
    return data