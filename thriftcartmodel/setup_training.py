import json
import os
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_json(filepath):
    """Helper function to load JSON data from a file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filepath}: {str(e)}")
        raise

def save_json(data, filepath):
    """Helper function to save data as JSON to a file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Successfully saved data to {filepath}")
    except Exception as e:
        logger.error(f"Error saving to {filepath}: {str(e)}")
        raise

def setup_data_split():
    """Set up training and testing data splits."""
    # Define file paths
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    train_file = data_dir / "train_users.json"
    test_file = data_dir / "test_users.json"
    
    # Load the datasets
    logger.info("Loading datasets...")
    train_users = load_json("synthetic_users_250.json")
    test_users = load_json("synthetic_users_50.json")
    
    # Log dataset sizes
    logger.info(f"Training set size: {len(train_users)} users")
    logger.info(f"Test set size: {len(test_users)} users")
    
    # Save the splits
    save_json(train_users, train_file)
    save_json(test_users, test_file)
    
    logger.info("Data split completed successfully!")
    
    # Return some basic statistics
    return {
        "train_size": len(train_users),
        "test_size": len(test_users),
        "total_users": len(train_users) + len(test_users)
    }

if __name__ == "__main__":
    setup_data_split()
