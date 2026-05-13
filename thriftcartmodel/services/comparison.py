import json
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re

class ProductComparator:
    """
    A class for comparing products across different platforms and categories.
    Handles price comparison, feature comparison, and similarity scoring.
    """
    
    def __init__(self, product_data: List[Dict] = None, config: Dict = None):
        """
        Initialize the ProductComparator.
        
        Args:
            product_data: List of product dictionaries
            config: Configuration dictionary with comparison settings
        """
        self.products = product_data or []
        self.config = config or {}
        self.platforms = self.config.get('platforms', {
            'grocery': ['blinkit', 'zomato', 'swiggy', 'dunzo', 'zepto', 'bigb', 'more', 'jiomart'],
            'ride': ['ola', 'uber', 'namma_yatri', 'rapido'],
            'ecommerce': ['myntra', 'ajio', 'flipkart', 'meesho', 'amazon']
        })
        
        # Initialize TF-IDF vectorizer for text similarity
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self.product_texts = []
        
        # Preprocess products if provided
        if self.products:
            self._preprocess_products()
    
    def _preprocess_products(self) -> None:
        """Preprocess product data for comparison."""
        if not self.products:
            return
            
        # Extract text features for similarity comparison
        self.product_texts = []
        
        for product in self.products:
            # Create a text representation of the product
            text_parts = [
                product.get('name', ''),
                product.get('description', ''),
                product.get('category', ''),
                product.get('brand', ''),
                ' '.join(product.get('features', [])),
                ' '.join(f"{k}_{v}" for k, v in product.get('specs', {}).items())
            ]
            
            # Clean and join text
            clean_text = ' '.join(str(part) for part in text_parts if part)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            self.product_texts.append(clean_text)
        
        # Create TF-IDF matrix if we have products
        if self.product_texts:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.product_texts)
    
    def add_products(self, products: List[Dict]) -> None:
        """
        Add products to the comparator.
        
        Args:
            products: List of product dictionaries to add
        """
        self.products.extend(products)
        self._preprocess_products()
    
    def find_similar_products(self, query: Union[str, Dict], n: int = 5, threshold: float = 0.3) -> List[Dict]:
        """
        Find products similar to the query product or text.
        
        Args:
            query: Either a product dictionary or a search query string
            n: Maximum number of similar products to return
            threshold: Minimum similarity score (0-1) to consider
            
        Returns:
            List of similar products with similarity scores
        """
        if not self.products or not self.tfidf_matrix.any():
            return []
        
        # Convert query to text if it's a product dictionary
        if isinstance(query, dict):
            text_parts = [
                query.get('name', ''),
                query.get('description', ''),
                query.get('category', ''),
                query.get('brand', ''),
                ' '.join(query.get('features', [])),
                ' '.join(f"{k}_{v}" for k, v in query.get('specs', {}).items())
            ]
            query_text = ' '.join(str(part) for part in text_parts if part)
        else:
            query_text = str(query)
        
        # Transform query to TF-IDF vector
        query_vec = self.vectorizer.transform([query_text])
        
        # Calculate cosine similarity between query and all products
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get indices of most similar products
        similar_indices = np.argsort(similarities)[::-1]  # Sort in descending order
        
        # Filter by threshold and get top N
        results = []
        for idx in similar_indices:
            if similarities[idx] < threshold:
                continue
                
            result = {
                'product': self.products[idx],
                'similarity_score': float(similarities[idx]),
                'product_id': self.products[idx].get('id', idx)
            }
            results.append(result)
            
            if len(results) >= n:
                break
        
        return results
    
    def compare_products(self, product_ids: List[str], 
                        attributes: List[str] = None) -> Dict[str, Any]:
        """
        Compare multiple products by their attributes.
        
        Args:
            product_ids: List of product IDs to compare
            attributes: List of attributes to compare (if None, compare all)
            
        Returns:
            Dictionary containing comparison results
        """
        if not product_ids:
            return {"error": "No product IDs provided"}
        
        # Find products by IDs
        products_to_compare = []
        for product_id in product_ids:
            product = next((p for p in self.products if p.get('id') == product_id), None)
            if product:
                products_to_compare.append(product)
        
        if not products_to_compare:
            return {"error": "No matching products found"}
        
        # If no attributes specified, use all available attributes
        if not attributes:
            # Get all unique attributes from all products
            all_attributes = set()
            for product in products_to_compare:
                all_attributes.update(product.keys())
            attributes = sorted(all_attributes)
        
        # Build comparison table
        comparison = {
            'attributes': {},
            'products': []
        }
        
        # Add product info
        for product in products_to_compare:
            product_info = {
                'id': product.get('id'),
                'name': product.get('name'),
                'platform': product.get('platform'),
                'price': product.get('price'),
                'rating': product.get('rating'),
                'url': product.get('url', '')
            }
            comparison['products'].append(product_info)
        
        # Compare each attribute
        for attr in attributes:
            if attr in ['id', 'name', 'platform', 'price', 'rating', 'url']:
                continue
                
            values = []
            for product in products_to_compare:
                values.append(product.get(attr, 'N/A'))
            
            # Check if all values are the same
            all_same = all(v == values[0] for v in values)
            
            comparison['attributes'][attr] = {
                'values': values,
                'all_same': all_same
            }
        
        # Calculate price differences
        prices = [p.get('price', 0) for p in products_to_compare if p.get('price') is not None]
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            price_diffs = [{
                'value': price,
                'diff_from_min': price - min_price if price != min_price else 0,
                'is_cheapest': price == min_price,
                'is_most_expensive': price == max_price and len(prices) > 1
            } for price in prices]
            
            comparison['price_comparison'] = {
                'min_price': min_price,
                'max_price': max_price,
                'price_range': max_price - min_price if len(prices) > 1 else 0,
                'prices': price_diffs
            }
        
        # Calculate average ratings
        ratings = [p.get('rating') for p in products_to_compare if p.get('rating') is not None]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            comparison['rating_comparison'] = {
                'average_rating': avg_rating,
                'highest_rated': max(products_to_compare, key=lambda x: x.get('rating', 0))['id']
            }
        
        return comparison
    
    def compare_prices(self, product_name: str, platforms: List[str] = None) -> Dict[str, Any]:
        """
        Compare prices of a product across different platforms.
        
        Args:
            product_name: Name of the product to compare
            platforms: List of platforms to compare (default: all available)
            
        Returns:
            Dictionary containing price comparison results
        """
        if not product_name:
            return {"error": "Product name is required"}
        
        # Use all platforms if none specified
        if not platforms:
            platforms = [p for platform_list in self.platforms.values() for p in platform_list]
        
        # Find matching products
        matching_products = []
        for product in self.products:
            if (product_name.lower() in product.get('name', '').lower() or 
                product_name.lower() in product.get('description', '').lower()):
                if not platforms or product.get('platform') in platforms:
                    matching_products.append(product)
        
        if not matching_products:
            return {"error": f"No matching products found for '{product_name}'"}
        
        # Group by platform and find best price for each
        platform_prices = {}
        for product in matching_products:
            platform = product.get('platform')
            price = product.get('price')
            
            if price is None:
                continue
                
            if platform not in platform_prices or price < platform_prices[platform]['price']:
                platform_prices[platform] = {
                    'product_id': product.get('id'),
                    'product_name': product.get('name'),
                    'price': price,
                    'rating': product.get('rating'),
                    'url': product.get('url', '')
                }
        
        # Convert to list and sort by price
        price_comparison = sorted(
            platform_prices.values(),
            key=lambda x: x['price']
        )
        
        # Calculate price differences
        if len(price_comparison) > 1:
            min_price = price_comparison[0]['price']
            for item in price_comparison:
                item['price_difference'] = item['price'] - min_price
                item['price_difference_pct'] = (item['price'] / min_price - 1) * 100 if min_price > 0 else 0
        
        return {
            'product_name': product_name,
            'platform_count': len(platform_prices),
            'price_range': price_comparison[-1]['price'] - price_comparison[0]['price'] if price_comparison else 0,
            'prices': price_comparison,
            'cheapest': price_comparison[0] if price_comparison else None,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_price_history(self, product_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get historical price data for a product.
        
        Args:
            product_id: ID of the product
            days: Number of days of history to return
            
        Returns:
            Dictionary containing price history
        """
        # In a real implementation, this would query a time-series database
        # For now, return mock data
        product = next((p for p in self.products if p.get('id') == product_id), None)
        if not product:
            return {"error": f"Product with ID {product_id} not found"}
        
        current_price = product.get('price', 100)
        price_history = []
        
        # Generate mock price history
        for i in range(days, -1, -1):
            date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
            # Simulate some price fluctuations
            if i % 7 == 0:  # Weekly sale
                price = current_price * 0.9  # 10% off
            elif i % 30 == 0:  # Monthly sale
                price = current_price * 0.8  # 20% off
            else:
                # Small random variation
                variation = np.random.uniform(-0.05, 0.05)  # ±5%
                price = current_price * (1 + variation)
            
            price_history.append({
                'date': date,
                'price': round(price, 2),
                'is_sale': i % 7 == 0 or i % 30 == 0
            })
        
        # Add current price
        price_history.append({
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
            'price': current_price,
            'is_current': True
        })
        
        # Calculate price statistics
        prices = [p['price'] for p in price_history]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        # Check if current price is the lowest in the period
        is_lowest = current_price <= min_price
        
        # Calculate days since last price change
        last_change_date = None
        for i in range(1, len(price_history)):
            if price_history[-i]['price'] != price_history[-i-1]['price']:
                last_change_date = price_history[-i-1]['date']
                break
        
        return {
            'product_id': product_id,
            'product_name': product.get('name'),
            'current_price': current_price,
            'price_history': price_history,
            'price_stats': {
                'min_price': min_price,
                'max_price': max_price,
                'avg_price': round(avg_price, 2),
                'is_lowest': is_lowest,
                'discount_pct': round((max_price - current_price) / max_price * 100, 1) if max_price > 0 else 0,
                'last_change_date': last_change_date
            },
            'recommendation': self._get_price_recommendation(price_history, current_price)
        }
    
    def _get_price_recommendation(self, price_history: List[Dict], current_price: float) -> Dict[str, Any]:
        """
        Generate a price recommendation based on historical data.
        
        Args:
            price_history: List of historical price points
            current_price: Current price of the product
            
        Returns:
            Dictionary with recommendation
        """
        if not price_history or len(price_history) < 7:  # Need at least a week of data
            return {
                'action': 'neutral',
                'confidence': 0.5,
                'reason': 'Insufficient historical data'
            }
        
        # Extract prices and dates
        prices = [p['price'] for p in price_history]
        dates = [p['date'] for p in price_history]
        
        # Calculate price trend (simple linear regression)
        x = np.arange(len(prices))
        y = np.array(prices)
        z = np.polyfit(x, y, 1)
        trend_slope = z[0]  # Positive = increasing, Negative = decreasing
        
        # Calculate volatility (standard deviation of price changes)
        price_changes = np.diff(prices) / prices[:-1] * 100  # Percentage changes
        volatility = np.std(price_changes) if len(price_changes) > 0 else 0
        
        # Determine if current price is near historical low/high
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        # Calculate position in price range (0 = min, 1 = max)
        if price_range > 0:
            price_position = (current_price - min_price) / price_range
        else:
            price_position = 0.5
        
        # Generate recommendation
        if price_position < 0.2:  # Near historical low
            action = 'buy_now'
            confidence = 0.8 - (volatility * 0.1)  # Higher volatility reduces confidence
            reason = 'Price is near historical low'
        elif price_position > 0.8:  # Near historical high
            action = 'wait'
            confidence = 0.7 + (volatility * 0.1)  # Higher volatility increases confidence
            reason = 'Price is near historical high'
        elif trend_slope < -0.01:  # Price is decreasing
            action = 'wait'
            confidence = 0.6
            reason = 'Price is trending downward'
        elif trend_slope > 0.01:  # Price is increasing
            action = 'buy_now'
            confidence = 0.7
            reason = 'Price is trending upward'
        else:  # Stable price
            action = 'neutral'
            confidence = 0.5
            reason = 'Price is stable'
        
        # Adjust confidence based on data quality
        confidence = max(0.1, min(0.9, confidence))  # Keep within reasonable bounds
        
        return {
            'action': action,
            'confidence': round(confidence, 2),
            'reason': reason,
            'trend_slope': round(trend_slope, 4),
            'volatility': round(volatility, 2),
            'price_position': round(price_position, 2)
        }
    
    def save_comparison_report(self, comparison_data: Dict, filepath: str) -> bool:
        """
        Save a comparison report to a file.
        
        Args:
            comparison_data: Comparison data to save
            filepath: Path to save the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(comparison_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving comparison report: {e}")
            return False
    
    def load_products_from_file(self, filepath: str) -> bool:
        """
        Load products from a JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                self.products = json.load(f)
            self._preprocess_products()
            return True
        except Exception as e:
            print(f"Error loading products: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Example product data
    example_products = [
        {
            "id": "p1",
            "name": "iPhone 13",
            "description": "Latest iPhone with A15 Bionic chip",
            "category": "Electronics/Smartphones",
            "brand": "Apple",
            "price": 69900,
            "rating": 4.7,
            "platform": "amazon",
            "url": "https://amazon.in/iphone13",
            "specs": {
                "storage": "128GB",
                "color": "Midnight",
                "display": "6.1\" Super Retina XDR"
            },
            "features": ["5G", "Dual camera", "Face ID"]
        },
        {
            "id": "p2",
            "name": "iPhone 13",
            "description": "Latest iPhone with A15 Bionic chip",
            "category": "Electronics/Smartphones",
            "brand": "Apple",
            "price": 68900,
            "rating": 4.6,
            "platform": "flipkart",
            "url": "https://flipkart.com/iphone13",
            "specs": {
                "storage": "128GB",
                "color": "Midnight",
                "display": "6.1\" Super Retina XDR"
            },
            "features": ["5G", "Dual camera", "Face ID"]
        },
        {
            "id": "p3",
            "name": "Samsung Galaxy S21",
            "description": "Flagship Android smartphone with Exynos 2100",
            "category": "Electronics/Smartphones",
            "brand": "Samsung",
            "price": 64999,
            "rating": 4.5,
            "platform": "amazon",
            "url": "https://amazon.in/galaxy-s21",
            "specs": {
                "storage": "128GB",
                "color": "Phantom Black",
                "display": "6.2\" Dynamic AMOLED 2X"
            },
            "features": ["5G", "Triple camera", "In-display fingerprint"]
        }
    ]
    
    # Initialize comparator
    comparator = ProductComparator(example_products)
    
    # Example: Compare prices for iPhone 13
    print("=== Price Comparison ===")
    price_comp = comparator.compare_prices("iPhone 13")
    print(f"Found {len(price_comp['prices'])} listings for iPhone 13")
    for item in price_comp['prices']:
        print(f"- {item['platform']}: ₹{item['price']} ({item['product_name']})")
    
    # Example: Compare two products
    print("\n=== Product Comparison ===")
    comp_result = comparator.compare_products(["p1", "p3"], ["brand", "price", "rating", "display"])
    print(f"Comparing {comp_result['products'][0]['name']} vs {comp_result['products'][1]['name']}")
    print(f"Price difference: ₹{comp_result['price_comparison']['price_range']}")
    
    # Example: Find similar products
    print("\n=== Similar Products ===")
    similar = comparator.find_similar_products({"name": "Samsung Galaxy S21"}, n=2)
    for item in similar:
        print(f"- {item['product']['name']} (Score: {item['similarity_score']:.2f})")
