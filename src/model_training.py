import os, numpy as np, pandas as pd, joblib
from src.logger import get_logger
from sklearn.model_selection import RandomizedSearchCV
import lightgbm as lgb
from src.custom_exception import CustomException
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from config.paths_config import *
from config.model_params import *
from utils.common_functions import read_yaml, load_data
from scipy.stats import uniform, randint
import mlflow, mlflow.sklearn

logger = get_logger(__name__)

class ModelTraining:
    def __init__(self, train_path, test_path, model_output_path):
        self.train_path = train_path
        self.test_path = test_path
        self.model_output_path = model_output_path

        self.params_dist = LIGHTGBM_PARAMS
        self.random_search_params = RANDOM_SEARCH_PARAMS

        logger.info(f"ModelTraining initialized with train_path: {self.train_path}, test_path: {self.test_path}, model_output_path: {self.model_output_path}")

    def load_and_split_data(self):
        try:
            logger.info("Loading training and testing data...")
            train_df = load_data(self.train_path)
            test_df = load_data(self.test_path)

            X_train = train_df.drop(columns=['booking_status'])
            y_train = train_df['booking_status']
            X_test = test_df.drop(columns=['booking_status'])
            y_test = test_df['booking_status']

            logger.info(f"Data loaded and split into features and target. Train shape: {X_train.shape}, Test shape: {X_test.shape}")
            return X_train, y_train.astype(int) , X_test, y_test.astype(int)
        except Exception as e:
            logger.error(f"Error occurred while loading and splitting data: {e}")
            raise CustomException("Failed to load and split data: " , e)

    def train_lgbm(self, X_train, y_train):
        try:
            logger.info("Starting LightGBM model training with hyperparameter tuning...")
            lgbm = lgb.LGBMClassifier(random_state=self.random_search_params['random_state'])

            random_search = RandomizedSearchCV(
                estimator=lgbm,
                param_distributions=self.params_dist,
                n_iter = self.random_search_params["n_iter"],
                cv = self.random_search_params["cv"],
                n_jobs= 1, #self.random_search_params["n_jobs"],
                verbose=self.random_search_params["verbose"],
                random_state=self.random_search_params["random_state"],
                scoring=self.random_search_params["scoring"],
            )

            logger.info("Starting our Hyperparamter tuning")

            random_search.fit(X_train,y_train)

            best_params = random_search.best_params_
            
            best_model = random_search.best_estimator_

            logger.info(f"Model training completed. Best parameters: {best_params}")
            return best_model
        except Exception as e:
            logger.error(f"Error occurred during model training: {e}")
            raise CustomException("Failed to train model: " , e)

    def evaluate_model(self, model, X_test, y_test):
        try:
            logger.info("Evaluating the trained model on test data...")
            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')

            logger.info(f"Model evaluation metrics - Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}, F1 Score: {f1}")
            return {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1
            }
        except Exception as e:
            logger.error(f"Error occurred during model evaluation: {e}")
            raise CustomException("Failed to evaluate model: " , e)

    def save_model(self, model):
        try:
            logger.info(f"Saving the trained model to {self.model_output_path}...")
            os.makedirs(os.path.dirname(self.model_output_path), exist_ok=True)
            joblib.dump(model, self.model_output_path)
            logger.info(f"Model saved successfully at {self.model_output_path}")
        except Exception as e:
            logger.error(f"Error occurred while saving the model: {e}")
            raise CustomException("Failed to save model: " , e)

    def run(self):
        try:
            with mlflow.start_run():

                logger.info("Starting our MLFLow experimentation")

                logger.info("Logging the training and testing data to MLFLOW")

                mlflow.log_artifact(self.train_path, artifact_path="datasets")
                mlflow.log_artifact(self.test_path, artifact_path="datasets")
                    
                X_train, y_train, X_test, y_test = self.load_and_split_data()
                best_lgbm_model = self.train_lgbm(X_train, y_train)
                metrics = self.evaluate_model(best_lgbm_model, X_test, y_test)
                self.save_model(best_lgbm_model)
                logger.info("Model training and evaluation process completed successfully.")

                logger.info("Logging the model into MLFLOW")

                mlflow.log_artifact(self.model_output_path)

                logger.info("Logging the params into MLFLOW")
                mlflow.log_params(best_lgbm_model.get_params())

                logger.info("Logging the metrics into MLFLOW")
                mlflow.log_metrics(metrics)

    

        except Exception as e:
            logger.error(f"Error occurred during the model training pipeline: {e}")
            raise CustomException("Failed to complete model training pipeline: " , e)


if __name__ == "__main__":
    try:
        model_trainer = ModelTraining(PROCESSED_TRAIN_DATA_PATH, PROCESSED_TEST_DATA_PATH, MODEL_OUTPUT_PATH)
        model_trainer.run()
    except Exception as e:
        logger.error(f"Error occurred in main execution: {e}")
        raise CustomException("Failed in main execution: " , e)