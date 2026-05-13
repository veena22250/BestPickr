import unittest
import os
import tempfile
import shutil
import json
import pandas as pd
from pathlib import Path

# Add the parent directory to the path so we can import our modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import DataLoader

class TestDataLoader(unittest.TestCase):
    """Test cases for the DataLoader class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data and environment before any tests run."""
        # Create a temporary directory for test data
        cls.test_dir = tempfile.mkdtemp()
        cls.raw_data_dir = Path(cls.test_dir) / 'raw'
        cls.processed_data_dir = Path(cls.test_dir) / 'processed'
        
        # Create the directories
        os.makedirs(cls.raw_data_dir, exist_ok=True)
        os.makedirs(cls.processed_data_dir, exist_ok=True)
        
        # Create test user data
        cls.test_users = [
            {
                "user_id": "user1",
                "name": "John Doe",
                "age": 30,
                "gender": "Male",
                "location": "New York",
                "preferences": {
                    "categories": ["Electronics", "Books"],
                    "brands": ["Apple", "Samsung"],
                    "price_range": [100, 1000]
                },
                "purchase_history": ["p1", "p2"]
            },
            {
                "user_id": "user2",
                "name": "Jane Smith",
                "age": 25,
                "gender": "Female",
                "location": "San Francisco",
                "preferences": {
                    "categories": ["Fashion", "Beauty"],
                    "brands": ["Nike", "L'Oreal"],
                    "price_range": [50, 500]
                },
                "purchase_history": ["p3"]
            }
        ]
        
        # Create test product data
        cls.test_products = [
            {
                "id": "p1",
                "name": "iPhone 13",
                "category": "Electronics/Smartphones",
                "brand": "Apple",
                "price": 999.99,
                "rating": 4.8,
                "review_count": 1245,
                "in_stock": True,
                "features": ["5G", "Face ID", "Dual Camera"],
                "specs": {
                    "storage": "128GB",
                    "color": "Midnight",
                    "screen_size": "6.1\""
                }
            },
            {
                "id": "p2",
                "name": "Galaxy S21",
                "category": "Electronics/Smartphones",
                "brand": "Samsung",
                "price": 799.99,
                "rating": 4.6,
                "review_count": 987,
                "in_stock": True,
                "features": ["5G", "120Hz Display", "Triple Camera"],
                "specs": {
                    "storage": "256GB",
                    "color": "Phantom Black",
                    "screen_size": "6.2\""
                }
            }
        ]
        
        # Save test data to files
        with open(cls.raw_data_dir / 'test_users.json', 'w') as f:
            json.dump(cls.test_users, f)
            
        with open(cls.raw_data_dir / 'test_products.json', 'w') as f:
            json.dump(cls.test_products, f)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests have run."""
        # Remove the temporary directory and all its contents
        shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """Set up test fixtures before each test method is called."""
        self.data_loader = DataLoader(data_dir=self.test_dir)
    
    def test_load_json(self):
        """Test loading data from a JSON file."""
        # Test loading existing file
        filepath = self.raw_data_dir / 'test_users.json'
        data = self.data_loader.load_json(filepath)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['user_id'], 'user1')
        
        # Test caching
        with open(filepath, 'w') as f:
            json.dump([{"test": "data"}], f)
        
        # Should return cached data, not the new data
        cached_data = self.data_loader.load_json(filepath)
        self.assertEqual(len(cached_data), 2)  # Still has 2 items from cache
        
        # Clear cache and load again
        self.data_loader._cache = {}
        new_data = self.data_loader.load_json(filepath)
        self.assertEqual(len(new_data), 1)  # Now has 1 item from file
    
    def test_save_json(self):
        """Test saving data to a JSON file."""
        test_data = {"key": "value", "list": [1, 2, 3]}
        filepath = self.processed_data_dir / 'test_save.json'
        
        # Test saving new file
        result = self.data_loader.save_json(test_data, filepath)
        self.assertTrue(result)
        self.assertTrue(filepath.exists())
        
        # Verify content
        with open(filepath, 'r') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, test_data)
        
        # Test saving to non-existent directory (should create it)
        new_dir = self.processed_data_dir / 'new_dir'
        new_file = new_dir / 'test.json'
        result = self.data_loader.save_json(test_data, new_file)
        self.assertTrue(result)
        self.assertTrue(new_file.exists())
    
    def test_load_csv(self):
        """Test loading data from a CSV file."""
        # Create a test CSV file
        csv_data = "id,name,value\n1,test1,100\n2,test2,200"
        filepath = self.raw_data_dir / 'test.csv'
        with open(filepath, 'w') as f:
            f.write(csv_data)
        
        # Test loading with default parameters
        df = self.data_loader.load_csv(filepath)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 3))
        self.assertEqual(df['name'].tolist(), ['test1', 'test2'])
        
        # Test loading with custom parameters
        df_custom = self.data_loader.load_csv(filepath, index_col='id')
        self.assertEqual(df_custom.index.tolist(), [1, 2])
    
    def test_save_csv(self):
        """Test saving a DataFrame to a CSV file."""
        # Create a test DataFrame
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['a', 'b', 'c'],
            'value': [10, 20, 30]
        })
        
        # Test saving
        filepath = self.processed_data_dir / 'test_save.csv'
        result = self.data_loader.save_csv(df, filepath, index=False)
        self.assertTrue(result)
        self.assertTrue(filepath.exists())
        
        # Verify content
        loaded_df = pd.read_csv(filepath)
        pd.testing.assert_frame_equal(loaded_df, df)
    
    def test_load_users(self):
        """Test loading user data."""
        # Test with default path (shouldn't exist yet)
        with self.assertRaises(FileNotFoundError):
            self.data_loader.load_users()
        
        # Test with explicit path
        users = self.data_loader.load_users(self.raw_data_dir / 'test_users.json')
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]['user_id'], 'user1')
    
    def test_load_products(self):
        """Test loading product data."""
        # Test with default path (shouldn't exist yet)
        with self.assertRaises(FileNotFoundError):
            self.data_loader.load_products()
        
        # Test with explicit path
        products = self.data_loader.load_products(self.raw_data_dir / 'test_products.json')
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0]['id'], 'p1')
    
    def test_preprocess_users(self):
        """Test preprocessing user data."""
        # Load and preprocess test users
        users = self.test_users
        df = self.data_loader.preprocess_users(users)
        
        # Check basic structure
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 2)
        
        # Check that preferences are expanded
        self.assertIn('preferences.categories', df.columns)
        self.assertIn('preferences.brands', df.columns)
        self.assertIn('preferences.price_range', df.columns)
        
        # Check that list columns are properly handled
        self.assertTrue(all(isinstance(x, str) for x in df['preferences.categories']))
        
        # Check that count columns are created
        self.assertIn('preferences.categories_count', df.columns)
        self.assertEqual(df['preferences.categories_count'].iloc[0], 2)  # 2 categories for user1
    
    def test_preprocess_products(self):
        """Test preprocessing product data."""
        # Load and preprocess test products
        products = self.test_products
        df = self.data_loader.preprocess_products(products)
        
        # Check basic structure
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 2)
        
        # Check that price is numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(df['price']))
        
        # Check that list columns are expanded
        self.assertIn('features_5G', df.columns)
        self.assertEqual(df['features_5G'].sum(), 2)  # Both products have 5G
        
        # Check that specs are expanded
        self.assertIn('specs.storage', df.columns)
        self.assertEqual(df['specs.storage'].iloc[0], '128GB')
    
    def test_generate_synthetic_products(self):
        """Test generating synthetic product data."""
        # Generate a small number of products
        n_products = 10
        products = self.data_loader.generate_synthetic_products(n=n_products)
        
        # Check basic structure
        self.assertIsInstance(products, list)
        self.assertEqual(len(products), n_products)
        
        # Check a few products
        for product in products:
            self.assertIn('id', product)
            self.assertIn('name', product)
            self.assertIn('price', product)
            self.assertIn('category', product)
            self.assertIn('brand', product)
            self.assertIn('rating', product)
            self.assertIn('features', product)
            self.assertIn('specs', product)
            
            # Check price is within expected range
            self.assertGreaterEqual(product['price'], 10)
            self.assertLessEqual(product['price'], 200000)
            
            # Check rating is within 1-5
            self.assertGreaterEqual(product['rating'], 1.0)
            self.assertLessEqual(product['rating'], 5.0)
        
        # Test saving to file
        filepath = self.processed_data_dir / 'synthetic_test.json'
        products = self.data_loader.generate_synthetic_products(n=5, save_path=filepath)
        self.assertTrue(filepath.exists())
        
        # Verify the saved file
        with open(filepath, 'r') as f:
            saved_products = json.load(f)
        self.assertEqual(len(saved_products), 5)
    
    def test_split_data(self):
        """Test splitting data into train/validation/test sets."""
        # Create a test DataFrame
        n_samples = 100
        df = pd.DataFrame({
            'feature1': range(n_samples),
            'feature2': range(n_samples, 2*n_samples),
            'target': [i % 3 for i in range(n_samples)]  # 3 classes
        })
        
        # Test with stratification
        splits = self.data_loader.split_data(
            df, 
            target='target',
            test_size=0.2,
            val_size=0.1,
            random_state=42
        )
        
        # Check the splits
        self.assertEqual(set(splits.keys()), {'train', 'val', 'test'})
        
        # Check sizes (approximately)
        self.assertAlmostEqual(len(splits['train']) / n_samples, 0.7, delta=0.05)
        self.assertAlmostEqual(len(splits['val']) / n_samples, 0.1, delta=0.05)
        self.assertAlmostEqual(len(splits['test']) / n_samples, 0.2, delta=0.05)
        
        # Check that all data is used
        all_indices = set(splits['train'].index) | set(splits['val'].index) | set(splits['test'].index)
        self.assertEqual(len(all_indices), n_samples)
        
        # Check stratification (proportions should be similar)
        def get_class_proportions(s):
            return s['target'].value_counts(normalize=True).sort_index()
        
        train_props = get_class_proportions(splits['train'])
        val_props = get_class_proportions(splits['val'])
        test_props = get_class_proportions(splits['test'])
        
        # Proportions should be similar (within 10%)
        for i in range(3):
            self.assertAlmostEqual(train_props[i], 1/3, delta=0.1)
            self.assertAlmostEqual(val_props[i], 1/3, delta=0.1)
            self.assertAlmostEqual(test_props[i], 1/3, delta=0.1)

if __name__ == '__main__':
    unittest.main()
