import json
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Set random seed for reproducibility
random.seed(42)

# Base data structures
CITIES = ["Bangalore", "Mumbai", "Delhi", "Chennai", "Pune", "Hyderabad", "Kolkata", "Ahmedabad", "Jaipur", "Kochi"]
GENDERS = ["Male", "Female", "Non-binary"]

# Grocery preferences
GROCERY_CATEGORIES = [
    ["fruits", "vegetables", "dairy"],
    ["meat", "poultry", "seafood"],
    ["beverages", "snacks", "ready to eat"],
    ["bakery", "dairy", "breakfast"],
    ["salads", "juices", "healthy snacks"],
    ["meat", "spices", "rice"],
    ["international cuisine", "frozen food", "desserts"],
    ["canned goods", "pasta", "sauces"],
    ["beverages", "alcohol", "mixers"],
    ["baby food", "diapers", "baby care"]
]

DELIVERY_TIMES = ["morning", "afternoon", "evening", "night"]
PRICE_SENSITIVITY = ["budget", "medium", "premium"]
HEALTH_FILTERS = ["organic", "gluten-free", "vegan", "sugar-free", "low-fat", "fresh", "local", "vegetarian", "eggless"]
ORDER_SIZES = ["1-2 people", "2-3 people", "3-4 people", "4+ people"]
GROCERY_PLATFORMS = ["Swiggy Instamart", "BigBasket", "Blinkit", "Zepto", "Dunzo", "JioMart", "Amazon Fresh"]

# Ride preferences
RIDE_TYPES = ["Bike", "Auto", "Hatchback", "Sedan", "SUV", "Premium"]
SAFETY_FEATURES = ["helmet", "mask", "women driver", "share location", "verified drivers", 
                  "emergency button", "car condition", "driver rating", "share ride details"]
TRAVEL_MODES = ["alone", "with family", "with friends", "with colleagues"]
RIDE_PLATFORMS = ["Uber", "Ola", "Rapido", "InDrive", "Meru"]

# Pincode ranges by city (format: {city: (start_pincode, end_pincode)})
PINCODE_RANGES = {
    "Bangalore": (560001, 560111),
    "Mumbai": (400001, 400107),
    "Delhi": (110001, 110098),
    "Chennai": (600001, 600141),
    "Pune": (411001, 411062),
    "Hyderabad": (500001, 500097),
    "Kolkata": (700001, 700157),
    "Ahmedabad": (380001, 380061),
    "Jaipur": (302001, 302040),
    "Kochi": (682001, 682037)
}

def generate_pincode(city: str) -> str:
    """Generate a random pincode for the given city."""
    start, end = PINCODE_RANGES[city]
    return str(random.randint(start, end))

def generate_user(user_id: int) -> Dict[str, Any]:
    """Generate a single user with random but realistic attributes."""
    gender = random.choice(GENDERS)
    age = random.randint(18, 70)
    city = random.choice(CITIES)
    
    # Generate grocery preferences
    grocery_cats = random.choice(GROCERY_CATEGORIES)
    health_filters = random.sample(HEALTH_FILTERS, k=random.randint(0, 3))
    
    # Generate ride preferences
    source_pincode = generate_pincode(city)
    dest_pincode = generate_pincode(city)
    while dest_pincode == source_pincode:  # Ensure different pincodes
        dest_pincode = generate_pincode(city)
    
    # Generate preferred travel times (2 random non-overlapping time slots)
    time_slots = [f"{h:02d}AM-{h+2:02d}AM" for h in range(6, 11)] + \
                [f"{h:02d}PM-{h+2:02d}PM" for h in range(1, 11)]
    travel_times = random.sample(time_slots, 2)
    
    return {
        "user_id": str(uuid.uuid4()),
        "name": f"User_{user_id}",
        "gender": gender,
        "age": age,
        "location": city,
        "preferences": {
            "grocery_apps": {
                "preferred_categories": grocery_cats,
                "preferred_delivery_time": random.choice(DELIVERY_TIMES),
                "price_sensitivity": random.choice(PRICE_SENSITIVITY),
                "discount_preference": random.choice([True, False]),
                "delivery_speed_importance": random.choice(["standard", "express", "same-day"]),
                "health_based_filters": health_filters,
                "usual_order_size": random.choice(ORDER_SIZES),
                "platforms_used": random.sample(GROCERY_PLATFORMS, k=random.randint(1, 3))
            },
            "ride_apps": {
                "preferred_ride_type": random.choice(RIDE_TYPES),
                "safety_importance": random.sample(SAFETY_FEATURES, k=random.randint(1, 3)),
                "min_driver_rating": round(random.uniform(3.5, 5.0), 1),
                "price_sensitivity": random.choice(PRICE_SENSITIVITY),
                "preferred_travel_times": travel_times,
                "travel_mode": random.choice(TRAVEL_MODES),
                "usual_route": {
                    "source_pincode": source_pincode,
                    "destination_pincode": dest_pincode
                },
                "platform_preference": {
                    "platform": random.choice(RIDE_PLATFORMS),
                    "reason": random.choice(["Price", "Availability", "Safety", "Service quality", "Loyalty rewards"])
                }
            }
        }
    }

def generate_users(count: int, existing_users: List[Dict] = None) -> List[Dict]:
    """Generate a list of users, optionally appending to existing users."""
    if existing_users is None:
        existing_users = []
    
    start_id = len(existing_users) + 1
    new_users = [generate_user(i) for i in range(start_id, start_id + count)]
    return existing_users + new_users

def main():
    # Load existing users
    try:
        with open("synthetic_users_50.json", "r") as f:
            existing_users = json.load(f)
        print(f"Loaded {len(existing_users)} existing users.")
    except FileNotFoundError:
        print("No existing users file found. Starting fresh.")
        existing_users = []
    
    # Generate additional users to reach 2,500 total
    total_users = 2500
    additional_needed = total_users - len(existing_users)
    
    if additional_needed > 0:
        print(f"Generating {additional_needed} new users...")
        all_users = generate_users(additional_needed, existing_users)
        
        # Save to a new file
        output_file = "synthetic_users_250.json"
        with open(output_file, "w") as f:
            json.dump(all_users, f, indent=4)
        print(f"Successfully generated {len(all_users)} users in {output_file}")
    else:
        print(f"Already have {len(existing_users)} users, which meets or exceeds the target of {total_users}.")

if __name__ == "__main__":
    main()
