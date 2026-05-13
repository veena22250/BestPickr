import json
import pandas as pd
from typing import Dict, List, Any, Union, Optional
from pathlib import Path
import os
import logging
from datetime import datetime
import numpy as np
from sklearn.model_selection import train_test_split

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataLoader:
    """
    A utility class for loading and preprocessing data for the ThrifCart application.
    Handles loading user data, product catalogs, and other data sources.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the DataLoader.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / 'data'
        self.raw_data_dir = self.data_dir / 'raw'
        self.processed_data_dir = self.data_dir / 'processed'
        
        # Create directories if they don't exist
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.processed_data_dir, exist_ok=True)
        
        # Cache for loaded data
        self._cache = {}
        
    def load_json(self, filepath: Union[str, Path]) -> Any:
        """
        Load data from a JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Loaded data (dict or list)
        """
        filepath = Path(filepath)
        cache_key = str(filepath.absolute())
        
        # Return from cache if available
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cache the result
            self._cache[cache_key] = data
            return data
            
        except Exception as e:
            logger.error(f"Error loading JSON file {filepath}: {e}")
            raise
    
    def save_json(self, data: Any, filepath: Union[str, Path], indent: int = 2) -> bool:
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save (must be JSON-serializable)
            filepath: Path to save the file
            indent: Indentation level for pretty printing
            
        Returns:
            bool: True if successful, False otherwise
        """
        filepath = Path(filepath)
        
        try:
            # Create parent directories if they don't exist
            os.makedirs(filepath.parent, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            
            logger.info(f"Data saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving JSON file {filepath}: {e}")
            return False
    
    def load_csv(self, filepath: Union[str, Path], **kwargs) -> pd.DataFrame:
        """
        Load data from a CSV file into a pandas DataFrame.
        
        Args:
            filepath: Path to the CSV file
            **kwargs: Additional arguments to pass to pandas.read_csv()
            
        Returns:
            Loaded DataFrame
        """
        filepath = Path(filepath)
        cache_key = str(filepath.absolute()) + str(kwargs)
        
        # Return from cache if available
        if cache_key in self._cache:
            return self._cache[cache_key].copy()
        
        try:
            df = pd.read_csv(filepath, **kwargs)
            
            # Cache the result
            self._cache[cache_key] = df
            return df.copy()
            
        except Exception as e:
            logger.error(f"Error loading CSV file {filepath}: {e}")
            raise
    
    def save_csv(self, df: pd.DataFrame, filepath: Union[str, Path], **kwargs) -> bool:
        """
        Save a DataFrame to a CSV file.
        
        Args:
            df: DataFrame to save
            filepath: Path to save the file
            **kwargs: Additional arguments to pass to DataFrame.to_csv()
            
        Returns:
            bool: True if successful, False otherwise
        """
        filepath = Path(filepath)
        
        try:
            # Create parent directories if they don't exist
            os.makedirs(filepath.parent, exist_ok=True)
            
            df.to_csv(filepath, **kwargs)
            logger.info(f"Data saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving CSV file {filepath}: {e}")
            return False
    
    def load_users(self, filepath: Union[str, Path] = None) -> List[Dict]:
        """
        Load user data from a JSON file.
        
        Args:
            filepath: Path to the users JSON file. If None, uses default path.
            
        Returns:
            List of user dictionaries
        """
        if filepath is None:
            filepath = self.raw_data_dir / 'synthetic_users_50.json'
        
        return self.load_json(filepath)
    
    def load_products(self, filepath: Union[str, Path] = None) -> List[Dict]:
        """
        Load product catalog from a JSON file.
        
        Args:
            filepath: Path to the products JSON file. If None, uses default path.
            
        Returns:
            List of product dictionaries
        """
        if filepath is None:
            filepath = self.raw_data_dir / 'products.json'
        
        return self.load_json(filepath)
    
    def load_reviews(self, filepath: Union[str, Path] = None) -> List[Dict]:
        """
        Load product reviews from a JSON file.
        
        Args:
            filepath: Path to the reviews JSON file. If None, uses default path.
            
        Returns:
            List of review dictionaries
        """
        if filepath is None:
            filepath = self.raw_data_dir / 'reviews.json'
        
        return self.load_json(filepath)
    
    def preprocess_users(self, users: List[Dict]) -> pd.DataFrame:
        """
        Preprocess user data for modeling.
        
        Args:
            users: List of user dictionaries
            
        Returns:
            Preprocessed DataFrame
        """
        # Convert to DataFrame
        df = pd.json_normalize(users)
        
        # Convert age to numeric, fill missing values with median
        if 'age' in df.columns:
            df['age'] = pd.to_numeric(df['age'], errors='coerce')
            df['age'].fillna(df['age'].median(), inplace=True)
        
        # Convert gender to categorical
        if 'gender' in df.columns:
            df['gender'] = pd.Categorical(df['gender'])
        
        # Process preferences
        pref_columns = [col for col in df.columns if col.startswith('preferences.')]
        for col in pref_columns:
            # Convert lists to strings for categorical encoding
            if df[col].apply(lambda x: isinstance(x, list)).any():
                df[f"{col}_count"] = df[col].apply(lambda x: len(x) if isinstance(x, list) else 0)
                df[col] = df[col].apply(lambda x: ', '.join(map(str, x)) if isinstance(x, list) else '')
        
        return df
    
    def preprocess_products(self, products: List[Dict]) -> pd.DataFrame:
        """
        Preprocess product data for modeling.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            Preprocessed DataFrame
        """
        # Convert to DataFrame
        df = pd.json_normalize(products)
        
        # Convert price to numeric, handle currency symbols, etc.
        if 'price' in df.columns:
            if df['price'].dtype == 'object':
                df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)
        
        # Convert rating to numeric, fill missing values with mean
        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
            df['rating'].fillna(df['rating'].mean(), inplace=True)
        
        # Extract brand from name if not present
        if 'brand' not in df.columns and 'name' in df.columns:
            # Simple brand extraction (first word in the name)
            df['brand'] = df['name'].str.split().str[0]
        
        # Convert category to categorical
        if 'category' in df.columns:
            df['category'] = pd.Categorical(df['category'])
        
        # Process features and specifications
        list_columns = [col for col in df.columns if isinstance(df[col].iloc[0], list)]
        for col in list_columns:
            # Create binary features for each unique value in the list
            unique_values = set()
            for lst in df[col].dropna():
                unique_values.update(lst)
            
            for value in unique_values:
                df[f"{col}_{value}"] = df[col].apply(lambda x: 1 if isinstance(x, list) and value in x else 0)
            
            # Drop the original column
            df.drop(columns=[col], inplace=True, errors='ignore')
        
        return df
    
    def preprocess_reviews(self, reviews: List[Dict]) -> pd.DataFrame:
        """
        Preprocess review data for sentiment analysis.
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Preprocessed DataFrame
        """
        # Convert to DataFrame
        df = pd.json_normalize(reviews)
        
        # Convert rating to numeric
        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        
        # Parse dates
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Extract year, month, day from date columns
        for col in date_columns:
            df[f"{col}_year"] = df[col].dt.year
            df[f"{col}_month"] = df[col].dt.month
            df[f"{col}_day"] = df[col].dt.day
        
        return df
    
    def split_data(self, df: pd.DataFrame, target: str = None, 
                  test_size: float = 0.2, val_size: float = 0.1,
                  random_state: int = 42) -> Dict[str, pd.DataFrame]:
        """
        Split data into train, validation, and test sets.
        
        Args:
            df: Input DataFrame
            target: Name of the target column (for stratification)
            test_size: Proportion of data to use for testing
            val_size: Proportion of training data to use for validation
            random_state: Random seed for reproducibility
            
        Returns:
            Dictionary containing train, val, test DataFrames
        """
        result = {}
        
        # Split into train+val and test
        if target and target in df.columns:
            stratify = df[target]
        else:
            stratify = None
        
        train_val, test = train_test_split(
            df,
            test_size=test_size,
            stratify=stratify,
            random_state=random_state
        )
        
        # Split train into train and validation
        if target and target in train_val.columns:
            stratify = train_val[target]
        else:
            stratify = None
        
        # Adjust val_size to be relative to the original dataset size
        relative_val_size = val_size / (1 - test_size)
        
        train, val = train_test_split(
            train_val,
            test_size=relative_val_size,
            stratify=stratify,
            random_state=random_state
        )
        
        result['train'] = train
        result['val'] = val
        result['test'] = test
        
        logger.info(f"Data split: {len(train)} train, {len(val)} val, {len(test)} test samples")
        
        return result
    
    def generate_synthetic_products(self, n: int = 1000, save_path: str = None) -> List[Dict]:
        """
        Generate synthetic product data for testing.
        
        Args:
            n: Number of products to generate
            save_path: If provided, save the generated data to this path
            
        Returns:
            List of synthetic product dictionaries
        """
        logger.info(f"Generating {n} synthetic products...")
        
        # Sample data for generation
        categories = ["Electronics", "Fashion", "Home", "Grocery", "Beauty", "Books", "Toys"]
        subcategories = {
            "Electronics": ["Smartphones", "Laptops", "Headphones", "Cameras", "Smartwatches"],
            "Fashion": ["Men's Clothing", "Women's Clothing", "Shoes", "Accessories", "Watches"],
            "Home": ["Furniture", "Kitchen", "Bedding", "Bath", "Decor"],
            "Grocery": ["Snacks", "Beverages", "Dairy", "Produce", "Bakery"],
            "Beauty": ["Skincare", "Makeup", "Haircare", "Fragrance"],
            "Books": ["Fiction", "Non-Fiction", "Children's", "Textbooks", "Cookbooks"],
            "Toys": ["Action Figures", "Dolls", "Games", "Outdoor", "Educational"]
        }
        
        brands = {
            "Electronics": ["Samsung", "Apple", "Sony", "LG", "Dell", "HP", "Bose", "Canon", "Nikon", "Xiaomi"],
            "Fashion": ["Nike", "Zara", "H&M", "Levi's", "Adidas", "Puma", "Gucci", "Prada", "Uniqlo", "Tommy Hilfiger"],
            "Home": ["IKEA", "Martha Stewart", "Cuisinart", "KitchenAid", "Dyson", "Shark", "Nestle", "Kellogg's"],
            "Grocery": ["Coca-Cola", "Pepsi", "Kellogg's", "Nestle", "Kraft", "Heinz", "Unilever", "General Mills"],
            "Beauty": ["L'Oreal", "Maybelline", "Estee Lauder", "MAC", "NARS", "Fenty", "The Ordinary", "CeraVe"],
            "Books": ["Penguin", "HarperCollins", "Random House", "Simon & Schuster", "Hachette", "Macmillan"],
            "Toys": ["LEGO", "Hasbro", "Mattel", "Fisher-Price", "Nerf", "Barbie", "Hot Wheels", "Play-Doh"]
        }
        
        # Generate products
        products = []
        for i in range(n):
            # Select random category and subcategory
            category = np.random.choice(categories)
            subcategory = np.random.choice(subcategories[category])
            brand = np.random.choice(brands[category])
            
            # Generate product name
            if category == "Electronics":
                model = f"{np.random.choice(['Pro', 'Air', 'Max', 'Ultra', 'Lite'])}-{np.random.randint(1, 10)}"
                name = f"{brand} {subcategory.split()[0]} {model}"
            elif category == "Fashion":
                colors = ["Black", "White", "Blue", "Red", "Green", "Gray", "Navy", "Beige"]
                name = f"{brand} {np.random.choice(colors)} {subcategory.split()[-1]}"
            else:
                name = f"{brand} {subcategory.split()[-1]}"
            
            # Generate price based on category
            price_ranges = {
                "Electronics": (5000, 200000),
                "Fashion": (500, 50000),
                "Home": (200, 100000),
                "Grocery": (10, 5000),
                "Beauty": (100, 20000),
                "Books": (100, 5000),
                "Toys": (200, 20000)
            }
            min_price, max_price = price_ranges[category]
            price = round(np.random.uniform(min_price, max_price) / 100) * 100  # Round to nearest 100
            
            # Generate rating (4.0-5.0 with some variance)
            rating = round(np.random.normal(4.2, 0.3), 1)
            rating = min(5.0, max(1.0, rating))  # Ensure within 1-5 range
            
            # Generate review count (skewed distribution)
            review_count = int(np.random.lognormal(mean=3, sigma=1.5))
            
            # Generate features/specs
            features = []
            specs = {}
            
            if category == "Electronics":
                specs["Storage"] = f"{np.random.choice([64, 128, 256, 512, 1024])}GB"
                specs["Color"] = np.random.choice(["Black", "Silver", "Space Gray", "Gold", "Blue"])
                features.extend(["Fast Charging", "Wireless", "Bluetooth"])
                
                if "phone" in subcategory.lower():
                    specs["Screen Size"] = f"{np.random.choice([5.8, 6.1, 6.5, 6.7])}\""
                    specs["Camera"] = f"{np.random.choice([12, 48, 64, 108])}MP"
                    features.extend(["5G", "Face ID", "Water Resistant"])
                
                elif "laptop" in subcategory.lower():
                    specs["Processor"] = f"{np.random.choice(['Intel i5', 'Intel i7', 'AMD Ryzen 5', 'AMD Ryzen 7'])}"
                    specs["RAM"] = f"{np.random.choice([8, 16, 32])}GB"
                    features.extend(["Backlit Keyboard", "Touchscreen", "Fingerprint Reader"])
            
            elif category == "Fashion":
                sizes = ["XS", "S", "M", "L", "XL", "XXL"]
                specs["Size"] = np.random.choice(sizes)
                specs["Material"] = np.random.choice(["Cotton", "Polyester", "Wool", "Silk", "Denim"])
                
                if "shirt" in name.lower() or "top" in name.lower():
                    specs["Fit"] = np.random.choice(["Slim", "Regular", "Oversized"])
                    specs["Sleeve"] = np.random.choice(["Short Sleeve", "Long Sleeve", "Sleeveless"])
                
                elif "pants" in name.lower() or "jeans" in name.lower():
                    specs["Fit"] = np.random.choice(["Skinny", "Slim", "Regular", "Relaxed"])
                    specs["Rise"] = np.random.choice(["Low", "Mid", "High"])
                
                elif "shoes" in name.lower():
                    specs["Size"] = np.random.randint(6, 13)  # US shoe sizes
                    specs["Width"] = np.random.choice(["Narrow", "Regular", "Wide"])
                    features.extend(["Cushioned Insole", "Slip Resistant", "Arch Support"])
            
            # Create product dictionary
            product = {
                "id": f"p{1000 + i}",
                "name": name,
                "description": f"High-quality {name} for all your needs. {np.random.choice(['Best in class.', 'Premium quality.', 'Top rated.'])}",
                "category": f"{category}/{subcategory}",
                "brand": brand,
                "price": price,
                "original_price": round(price * np.random.uniform(1.1, 1.5)),  # 10-50% higher than sale price
                "rating": rating,
                "review_count": review_count,
                "in_stock": np.random.choice([True, False], p=[0.9, 0.1]),  # 90% in stock
                "features": features,
                "specs": specs,
                "platform": np.random.choice(["amazon", "flipkart", "myntra", "ajio", "jiomart"]),
                "url": f"https://example.com/products/p{1000 + i}",
                "image_url": f"https://example.com/images/p{1000 + i}.jpg",
                "last_updated": (datetime.now() - pd.Timedelta(days=np.random.randint(0, 30))).strftime("%Y-%m-%d"),
                "tags": [category.lower(), subcategory.lower().replace("'", "").replace(" ", "-"), brand.lower()]
            }
            
            products.append(product)
        
        # Save to file if path is provided
        if save_path:
            save_path = Path(save_path)
            os.makedirs(save_path.parent, exist_ok=True)
            self.save_json(products, save_path)
            logger.info(f"Saved {len(products)} synthetic products to {save_path}")
        
        return products

# Example usage
if __name__ == "__main__":
    # Initialize data loader
    data_loader = DataLoader()
    
    # Example: Load and preprocess user data
    try:
        users = data_loader.load_users()
        print(f"Loaded {len(users)} users")
        
        # Preprocess user data
        users_df = data_loader.preprocess_users(users)
        print(f"Preprocessed users DataFrame shape: {users_df.shape}")
        print("Columns:", users_df.columns.tolist())
        
    except FileNotFoundError:
        print("User data file not found. Skipping user data example.")
    
    # Example: Generate and save synthetic product data
    output_dir = data_loader.raw_data_dir
    output_file = output_dir / 'synthetic_products_1000.json'
    
    if not output_file.exists():
        print(f"Generating synthetic products to {output_file}...")
        products = data_loader.generate_synthetic_products(n=1000, save_path=output_file)
        print(f"Generated {len(products)} synthetic products")
    else:
        print(f"Synthetic products file already exists at {output_file}")
    
    # Example: Load and preprocess product data
    try:
        products = data_loader.load_products(output_file)
        print(f"\nLoaded {len(products)} products")
        
        # Preprocess product data
        products_df = data_loader.preprocess_products(products)
        print(f"Preprocessed products DataFrame shape: {products_df.shape}")
        print("Sample columns:", [col for col in products_df.columns if 'specs' in col][:5])
        
        # Split data into train/val/test
        splits = data_loader.split_data(products_df, target='rating')
        print(f"\nData split sizes:")
        for split_name, split_df in splits.items():
            print(f"- {split_name}: {len(split_df)} samples")
        
    except Exception as e:
        print(f"Error processing products: {e}")
