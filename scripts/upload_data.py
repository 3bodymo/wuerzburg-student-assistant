###########################################################
# This block appends the root project path to the         #
# system path for access to project files and modules.    #
###########################################################
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
###########################################################

import json
from pathlib import Path
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from app.db.base import SessionLocal, engine
from app.db import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JSON_DATA_PATH = Path("data/json_data")

def load_json_file(filename: str) -> list:
    """
    Loads and parses JSON data from a file.

    Args:
        filename (str): Name of the JSON file to load from the JSON_DATA_PATH directory.

    Returns:
        list: Parsed JSON data as a list of dictionaries.
            Returns empty list if file is not found or contains invalid JSON.
    """
    try:
        with open(JSON_DATA_PATH / filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in file: {filename}")
        return []

def reset_sequence(db: Session, model_class: models.Base) -> None:
    """
    Resets the auto-increment sequence for a database table.

    Args:
        db (Session): SQLAlchemy database session.
        model_class (Base): SQLAlchemy model class whose sequence needs to be reset.

    Returns:
        None
    """
    try:
        table_name = model_class.__tablename__
        sql = text(f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1")
        db.execute(sql)
        db.commit()
        logger.info(f"Successfully reset sequence for table {table_name}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error resetting sequence for table {table_name}: {str(e)}")

def clean_table(db: Session, model_class: models.Base) -> None:
    """
    Removes all records from a specified table and resets its sequence.

    Args:
        db (Session): SQLAlchemy database session.
        model_class (Base): SQLAlchemy model class whose table needs to be cleaned.

    Returns:
        None
    """
    try:
        db.query(model_class).delete()
        db.commit()
        logger.info(f"Successfully cleaned table {model_class.__tablename__}")
        reset_sequence(db, model_class)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error cleaning table {model_class.__tablename__}: {str(e)}")

def upload_data(db: Session, model_class: models.Base, data_list: list) -> None:
    """
    Cleans existing data and uploads new data to specified table.

    Args:
        db (Session): SQLAlchemy database session.
        model_class (Base): SQLAlchemy model class representing the target table.
        data_list (list): List of dictionaries containing the data to be uploaded.
            Each dictionary should match the model's column structure.

    Returns:
        None
    """
    try:
        # First, clean existing data
        clean_table(db, model_class)
        
        # Then upload new data
        for item in data_list:
            db_item = model_class(**item)
            db.add(db_item)
        db.commit()
        logger.info(f"Successfully uploaded {len(data_list)} items to {model_class.__tablename__}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error uploading to {model_class.__tablename__}: {str(e)}")

def main() -> None:
    """
    Main execution function that processes JSON files and uploads data to database.

    Iterates through predefined mappings of JSON files to database models,
    loads the JSON data, and uploads it to the corresponding database tables.

    Returns:
        None
    """
    # Mapping of JSON files to their corresponding models
    data_mapping = {
        'private_apartments.json': models.Apartment,
        'places.json': models.Place,
        'whatsapp_groups.json': models.WhatsAppGroup,
        'insurances.json': models.Insurance,
        'general_info.json': models.GeneralInfo,
        'banks.json': models.Bank,
        'telecom_providers.json': models.TelecomProvider,
        'useful_apps.json': models.UsefulApp,
    }

    db = SessionLocal()
    try:
        for json_file, model_class in data_mapping.items():
            logger.info(f"Processing {json_file}...")
            data = load_json_file(json_file)
            if data:
                upload_data(db, model_class, data)
    finally:
        db.close()

if __name__ == "__main__":
    main()
