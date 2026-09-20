import os, pandas as pd, numpy as np
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import PROCESSED_DIR, PROCESSED_TRAIN_DATA_PATH, PROCESSED_TEST_DATA_PATH, CONFIG_PATH, TRAIN_FILE_PATH, TEST_FILE_PATH
from utils.common_functions import load_data, read_yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE


logger = get_logger(__name__)

class DataProcessor:
    def __init__(self, train_path, test_path, processed_dir, config_path):
        self.train_path = train_path
        self.test_path = test_path
        self.processed_dir = processed_dir
        self.config = read_yaml(config_path)

        os.makedirs(self.processed_dir, exist_ok=True)

        logger.info(f"DataProcessor initialized with train_path: {self.train_path}, test_path: {self.test_path}, processed_dir: {self.processed_dir}, config_path: {self.config}")

    def preprocess_data(self, df):
        try:
            logger.info("Starting data preprocessing...")
            logger.info("Dropping the columns")
            df.drop(columns=['Booking_ID'], inplace=True)
            df.drop_duplicates(inplace=True)
            cat_cols = self.config['data_processing']['categorical_columns']
            num_cols = self.config['data_processing']['numerical_columns']

            logger.info("Encoding categorical columns...")

            label_encoder = LabelEncoder()

            mappings={}

            for col in cat_cols:
                df[col] = label_encoder.fit_transform(df[col])

                mappings[col] = {label:code for label,code in zip(label_encoder.classes_ , label_encoder.transform(label_encoder.classes_))}

            logger.info("Label Mappings are :")
            for col, map in mappings.items():
                logger.info(f"{col}: {map}")

            logger.info("Handling Skewness...")

            skewness_threshold = self.config['data_processing']['skewness_threshold']
            skewness = df[num_cols].apply(lambda x: x.skew())

            for column in skewness[skewness > skewness_threshold].index:
                df[column] = np.log1p(df[column])
                logger.info(f"Applied log transformation to {column} due to skewness of {skewness[column]}")

            return df


        except Exception as e:
            logger.error(f"Error occurred during data preprocessing: {e}")
            raise CustomException("Failed to preprocess data: " , e)


    def balance_data(self, df):
        try:
            logger.info("Handling Imbalanced Data")
            X = df.drop(columns='booking_status')
            y = df["booking_status"]

            smote = SMOTE(random_state=42)
            X_resampled , y_resampled = smote.fit_resample(X,y)

            balanced_df = pd.DataFrame(X_resampled , columns=X.columns)
            balanced_df["booking_status"] = y_resampled

            logger.info("Data balanced sucesffuly")
            return balanced_df
        
        except Exception as e:
            logger.error(f"Error occurred during data balancing: {e}")
            raise CustomException("Failed to balance data: " , e)


    def select_features(self, df):
        try:
            logger.info("Starting feature selection using Random Forest Classifier...")
            X = df.drop(columns=['booking_status'])
            y = df['booking_status']

            model = RandomForestClassifier(random_state=42)
            model.fit(X, y)

            feature_importance = model.feature_importances_

            feature_importance_df = pd.DataFrame({
            'feature':X.columns,
            'importance':feature_importance
            })

            top_features_importance_df = feature_importance_df.sort_values(by="importance" , ascending=False)

            num_features_to_select = self.config['data_processing']['no_of_features']

            top_features = top_features_importance_df["feature"].head(num_features_to_select).values.tolist()

            top_df = df[top_features + ["booking_status"]]
            
            logger.info(f"Selected features based on importance: {top_features}")

        except Exception as e:
            logger.error(f"Error occurred during feature selection: {e}")
            raise CustomException("Failed to select features: " , e)

        return top_df

    def save_data(self, df, file_path):
        try:
            logger.info(f"Saving processed data to {file_path}...")
            df.to_csv(file_path, index=False)
            logger.info(f"Processed data saved successfully to {file_path}")
        except Exception as e:
            logger.error(f"Error occurred while saving processed data: {e}")
            raise CustomException("Failed to save processed data: " , e)

    def process(self):
        try:
            logger.info("Loading data from RAW directory...")
            train_df = load_data(self.train_path)
            test_df = load_data(self.test_path)


            logger.info("Data loaded successfully. Starting preprocessing...")

            train_df = self.preprocess_data(train_df)
            test_df = self.preprocess_data(test_df)

            logger.info("Preprocessing completed. Starting data balancing")

            train_df = self.balance_data(train_df)
            test_df = self.balance_data(test_df)

            logger.info("Data balancing completed. Starting feature selection...")

            train_df = self.select_features(train_df)
            test_df = test_df[train_df.columns]

            logger.info("Feature selection completed. Saving processed data...")

            self.save_data(train_df, PROCESSED_TRAIN_DATA_PATH)
            self.save_data(test_df, PROCESSED_TEST_DATA_PATH)

            logger.info("Data processing completed successfully. Processed data saved to PROCESSED directory.")

        except Exception as e:
            logger.error(f"Error occurred during data processing: {e}")
            raise CustomException("Failed to process data: " , e)


if __name__=="__main__":
    processor = DataProcessor(TRAIN_FILE_PATH, TEST_FILE_PATH, PROCESSED_DIR, CONFIG_PATH)
    processor.process() 