# backend/config/competitors.py
COMPETITOR_BRANDS = {
    'Electronics': {
        'Cameras': ['Canon', 'Nikon', 'Sony', 'Fujifilm', 'Panasonic', 'Olympus', 'Leica', 'GoPro', 'DJI'],
        'Smartphones': ['Apple', 'Samsung', 'Google', 'OnePlus', 'Xiaomi', 'Motorola', 'Nokia', 'LG', 'Huawei'],
        'Laptops': ['Apple', 'Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'Microsoft', 'Razer', 'MSI'],
        'Headphones': ['Sony', 'Bose', 'Apple', 'Sennheiser', 'Audio-Technica', 'JBL', 'Beats', 'Skullcandy'],
        'Tablets': ['Apple', 'Samsung', 'Microsoft', 'Amazon', 'Lenovo', 'Huawei']
    },
    'Home & Kitchen': {
        'Appliances': ['Instant Pot', 'Ninja', 'KitchenAid', 'Cuisinart', 'Breville', 'Hamilton Beach', 'Black+Decker'],
        'Cookware': ['All-Clad', 'T-fal', 'Calphalon', 'Lodge', 'Le Creuset', 'Cuisinart', 'GreenPan'],
        'Decor': ['IKEA', 'West Elm', 'CB2', 'Pottery Barn', 'Crate & Barrel', 'Wayfair'],
        'Storage': ['Rubbermaid', 'Sterilite', 'OXO', 'The Container Store', 'mDesign', 'SimpleHouseware'],
        'Furniture': ['IKEA', 'Herman Miller', 'Steelcase', 'West Elm', 'Ashley', 'Wayfair', 'CB2']
    },
    'Fashion': {
        'Watches': ['Apple', 'Garmin', 'Fitbit', 'Samsung', 'Fossil', 'Casio', 'Timex', 'Citizen', 'Seiko'],
        'Clothing': ['Nike', 'Adidas', 'Lululemon', 'Under Armour', 'Patagonia', 'North Face', 'Columbia'],
        'Shoes': ['Nike', 'Adidas', 'New Balance', 'ASICS', 'Puma', 'Reebok', 'Vans', 'Converse', 'Allbirds'],
        'Bags': ['Tumi', 'Samsonite', 'Herschel', 'JanSport', 'North Face', 'Patagonia', 'Coach', 'Kate Spade'],
        'Accessories': ['Ray-Ban', 'Oakley', 'Fossil', 'Michael Kors', 'Coach', 'Kate Spade', 'Pandora']
    },
    'Sports': {
        'Outdoor': ['North Face', 'Patagonia', 'Columbia', 'Arc\'teryx', 'Marmot', 'Outdoor Research', 'REI Co-op'],
        'Team Sports': ['Nike', 'Adidas', 'Under Armour', 'Wilson', 'Spalding', 'Rawlings', 'Mizuno'],
        'Winter Sports': ['Burton', 'Salomon', 'K2', 'Rossignol', 'Volkl', 'Atomic', 'Head'],
        'Fitness': ['Bowflex', 'Peloton', 'NordicTrack', 'Life Fitness', 'Rogue', 'CAP Barbell', 'Yes4All'],
        'Water Sports': ['Speedo', 'TYR', 'Arena', 'O\'Neill', 'Rip Curl', 'Billabong', 'Quiksilver']
    },
    'Beauty': {
        'Haircare': ['Dyson', 'Olaplex', 'Moroccanoil', 'Redken', 'L\'Oreal', 'Pantene', 'Head & Shoulders'],
        'Skincare': ['La Mer', 'Olay', 'CeraVe', 'Cetaphil', 'Neutrogena', 'Clinique', 'Estee Lauder'],
        'Makeup': ['Charlotte Tilbury', 'Fenty Beauty', 'MAC', 'Urban Decay', 'NARS', 'Too Faced', 'Maybelline'],
        'Fragrance': ['Chanel', 'Dior', 'Tom Ford', 'Jo Malone', 'Marc Jacobs', 'Viktor & Rolf', 'YSL'],
        'Tools': ['Dyson', 'ghd', 'CHI', 'Hot Tools', 'Conair', 'Revlon', 'BaByliss']
    }
}

# Generic competitors that appear across categories
GENERIC_COMPETITORS = ['Amazon', 'Walmart', 'Target', 'Costco', 'Sephora', 'Ulta', 'Best Buy']

def get_competitors_for_product(category, subcategory=None):
    """Get relevant competitors for a product based on category and subcategory"""
    competitors = set(GENERIC_COMPETITORS)
    
    if category in COMPETITOR_BRANDS:
        if isinstance(COMPETITOR_BRANDS[category], dict):
            # Category has subcategories
            if subcategory and subcategory in COMPETITOR_BRANDS[category]:
                competitors.update(COMPETITOR_BRANDS[category][subcategory])
            else:
                # Add all competitors from all subcategories
                for subcat_competitors in COMPETITOR_BRANDS[category].values():
                    competitors.update(subcat_competitors)
        else:
            # Category doesn't have subcategories
            competitors.update(COMPETITOR_BRANDS[category])
    
    return list(competitors)