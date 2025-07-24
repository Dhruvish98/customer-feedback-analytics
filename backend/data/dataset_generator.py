# backend/data/dataset_generator.py

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json
from faker import Faker

fake = Faker()

class EcommerceReviewGenerator:
    def __init__(self, num_reviews=10000):
        self.num_reviews = num_reviews
        self.categories = {
            'Electronics': ['Smartphone', 'Laptop', 'Headphones', 'Smartwatch', 'Tablet'],
            'Fashion': ['T-Shirt', 'Jeans', 'Dress', 'Shoes', 'Jacket'],
            'Home Appliances': ['Refrigerator', 'Washing Machine', 'Microwave', 'Air Conditioner', 'Vacuum Cleaner'],
            'Beauty': ['Face Cream', 'Shampoo', 'Lipstick', 'Perfume', 'Face Wash'],
            'Sports': ['Running Shoes', 'Yoga Mat', 'Dumbbells', 'Cricket Bat', 'Football']
        }
        
        self.brands = {
            'Electronics': ['TechPro', 'ElectroMax', 'SmartLife', 'DigiWorld', 'FutureTech'],
            'Fashion': ['StyleHub', 'TrendyWear', 'UrbanFit', 'FashionForward', 'ClassicStyle'],
            'Home Appliances': ['HomeEasy', 'AppliancePro', 'SmartHome', 'EcoLiving', 'PowerSave'],
            'Beauty': ['GlowUp', 'NaturalBeauty', 'SkinCare+', 'BeautyEssence', 'PureGlow'],
            'Sports': ['SportZone', 'FitLife', 'ProAthletic', 'ActiveGear', 'SportsMaster']
        }
        
        # Review templates with realistic patterns
        self.review_patterns = {
            'positive': {
                'templates': [
                    "Excellent {product}! {positive_aspect}. {recommendation}",
                    "Very happy with this {product}. {positive_aspect}",
                    "{positive_aspect}. Worth every penny!",
                    "Amazing quality! {positive_aspect}. {recommendation}",
                    "5 stars! {positive_aspect}. {delivery_comment}"
                ],
                'aspects': {
                    'Electronics': ['Great battery life', 'Fast performance', 'Excellent display quality', 'Good build quality'],
                    'Fashion': ['Perfect fit', 'Comfortable material', 'Looks exactly like the picture', 'Great color'],
                    'Home Appliances': ['Energy efficient', 'Works perfectly', 'Easy to use', 'Quiet operation'],
                    'Beauty': ['Visible results', 'Gentle on skin', 'Long lasting', 'Nice fragrance'],
                    'Sports': ['Durable material', 'Comfortable grip', 'Good for workouts', 'Excellent quality']
                }
            },
            'negative': {
                'templates': [
                    "Disappointed with {product}. {negative_aspect}. {complaint}",
                    "{negative_aspect}. Would not recommend.",
                    "Poor quality {product}. {negative_aspect}",
                    "{negative_aspect}. {complaint}. Want refund!",
                    "Worst {product} ever! {negative_aspect}"
                ],
                'aspects': {
                    'Electronics': ['Battery drains quickly', 'Overheating issues', 'Poor camera quality', 'Laggy performance'],
                    'Fashion': ['Size runs small', 'Color faded after wash', 'Material feels cheap', 'Not as described'],
                    'Home Appliances': ['Too noisy', 'Stopped working after 2 months', 'Consumes too much power', 'Difficult to operate'],
                    'Beauty': ['Caused breakouts', 'No visible results', 'Too expensive for quality', 'Strong chemical smell'],
                    'Sports': ['Poor grip', 'Material torn after few uses', 'Not comfortable', 'Overpriced']
                }
            },
            'neutral': {
                'templates': [
                    "{product} is okay. {neutral_aspect}",
                    "Average {product}. {neutral_aspect}. {suggestion}",
                    "{neutral_aspect}. Could be better.",
                    "Mixed feelings about {product}. {neutral_aspect}"
                ],
                'aspects': {
                    'Electronics': ['Average battery life', 'Works as expected', 'Nothing special', 'Decent for the price'],
                    'Fashion': ['Fits okay', 'Average quality', 'Looks decent', 'Material is okay'],
                    'Home Appliances': ['Does the job', 'Average performance', 'Could be quieter', 'Basic features only'],
                    'Beauty': ['Some improvement seen', 'Average results', 'Okay for the price', 'Nothing extraordinary'],
                    'Sports': ['Basic quality', 'Works for beginners', 'Average durability', 'Decent for casual use']
                }
            }
        }
        
        # Realistic typos and variations
        self.typo_patterns = [
            ('excellent', ['excelent', 'excellant', 'exellent']),
            ('recommend', ['recomend', 'reccommend', 'recomand']),
            ('disappointed', ['dissapointed', 'disapponted', 'disapointed']),
            ('quality', ['quallity', 'qualaty', 'qality']),
            ('battery', ['baterry', 'batery', 'battry'])
        ]
        
    def add_realistic_noise(self, text):
        """Add realistic irregularities to text"""
        # Random capitalization issues
        if random.random() < 0.1:
            text = text.upper()
        elif random.random() < 0.1:
            text = text.lower()
        
        # Add typos
        words = text.split()
        for i, word in enumerate(words):
            if random.random() < 0.05:  # 5% chance of typo
                for correct, typos in self.typo_patterns:
                    if word.lower() == correct:
                        words[i] = random.choice(typos)
                        break
        
        # Add extra spaces or remove spaces
        if random.random() < 0.05:
            text = '  '.join(words)
        elif random.random() < 0.05:
            text = ''.join(words[:2]) + ' ' + ' '.join(words[2:])
        else:
            text = ' '.join(words)
        
        # Add emoticons/emojis
        if random.random() < 0.2:
            emoticons = [':)', ':(', ':D', '!!', '...', '😊', '😞', '👍', '👎', '⭐']
            text += ' ' + random.choice(emoticons)
        
        # Add hashtags for younger demographics
        if random.random() < 0.1:
            hashtags = ['#love', '#hate', '#recommended', '#waste', '#awesome', '#fail']
            text += ' ' + random.choice(hashtags)
        
        return text
    
    def generate_review_text(self, category, product, sentiment):
        """Generate realistic review text based on sentiment and category"""
        pattern = random.choice(self.review_patterns[sentiment]['templates'])
        aspect = random.choice(self.review_patterns[sentiment]['aspects'][category])
        
        text = pattern.format(
            product=product,
            positive_aspect=aspect if sentiment == 'positive' else '',
            negative_aspect=aspect if sentiment == 'negative' else '',
            neutral_aspect=aspect if sentiment == 'neutral' else '',
            recommendation="Highly recommend!" if sentiment == 'positive' else "",
            complaint="Not worth the money" if sentiment == 'negative' else "",
            suggestion="Price could be lower" if sentiment == 'neutral' else "",
            delivery_comment="Fast delivery too!" if random.random() < 0.3 else ""
        )
        
        # Clean up empty placeholders
        text = ' '.join(text.split())
        
        # Add noise
        text = self.add_realistic_noise(text)
        
        return text
    
    def generate_dataset(self):
        """Generate the complete dataset with business logic"""
        reviews = []
        
        # Business logic: seasonal trends
        current_date = datetime.now()
        
        for i in range(self.num_reviews):
            # Random category with weighted distribution
            category_weights = [0.3, 0.25, 0.2, 0.15, 0.1]  # Electronics most popular
            category = np.random.choice(list(self.categories.keys()), p=category_weights)
            
            # Random product from category
            product = random.choice(self.categories[category])
            
            # Random brand
            brand = random.choice(self.brands[category])
            
            # Generate review date (last 2 years)
            days_ago = random.randint(0, 730)
            review_date = current_date - timedelta(days=days_ago)
            
            # Business logic: sentiment distribution based on various factors
            # Newer products tend to have more positive reviews
            if days_ago < 30:
                sentiment_weights = [0.6, 0.1, 0.3]  # More positive for new products
            else:
                sentiment_weights = [0.4, 0.2, 0.4]  # Balanced for older products
            
            sentiment = np.random.choice(['positive', 'negative', 'neutral'], p=sentiment_weights)
            
            # Rating based on sentiment
            if sentiment == 'positive':
                rating = np.random.choice([4, 5], p=[0.3, 0.7])
            elif sentiment == 'negative':
                rating = np.random.choice([1, 2], p=[0.7, 0.3])
            else:
                rating = 3
            
            # Generate review text
            review_text = self.generate_review_text(category, product, sentiment)
            
            # User demographics
            age = random.randint(18, 65)
            gender = random.choice(['M', 'F', 'Other'])
            
            # Purchase verification
            verified_purchase = random.random() < 0.8
            
            # Helpful votes (older reviews tend to have more votes)
            max_votes = min(days_ago, 100)
            helpful_votes = random.randint(0, max_votes)
            total_votes = helpful_votes + random.randint(0, max(max_votes - helpful_votes, 1))
            
            review = {
                'review_id': f'REV{i+1:06d}',
                'product_id': f'PROD{hash(product) % 1000:04d}',
                'product_name': product,
                'category': category,
                'brand': brand,
                'user_id': f'USER{random.randint(1, 5000):05d}',
                'age': age,
                'gender': gender,
                'rating': rating,
                'review_text': review_text,
                'review_date': review_date.strftime('%Y-%m-%d'),
                'verified_purchase': verified_purchase,
                'helpful_votes': helpful_votes,
                'total_votes': total_votes,
                'sentiment': sentiment,  # Ground truth for validation
                'review_length': len(review_text.split())
            }
            
            reviews.append(review)
        
        df = pd.DataFrame(reviews)
        
        # Add some business logic patterns
        # Black Friday/Cyber Monday spike
        black_friday_reviews = df.sample(n=int(0.1 * len(df)))
        black_friday_date = datetime(2023, 11, 24)
        for idx in black_friday_reviews.index:
            df.loc[idx, 'review_date'] = (black_friday_date + timedelta(days=random.randint(0, 7))).strftime('%Y-%m-%d')
        
        return df
    
    def save_dataset(self, df, filepath):
        """Save dataset to CSV and JSON formats"""
        df.to_csv(f'{filepath}.csv', index=False)
        df.to_json(f'{filepath}.json', orient='records', indent=2)
        
        # Save metadata
        metadata = {
            'total_reviews': len(df),
            'categories': df['category'].value_counts().to_dict(),
            'sentiment_distribution': df['sentiment'].value_counts().to_dict(),
            'rating_distribution': df['rating'].value_counts().to_dict(),
            'date_range': {
                'start': df['review_date'].min(),
                'end': df['review_date'].max()
            }
        }
        
        with open(f'{filepath}_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Dataset saved successfully!")
        print(f"Total reviews: {len(df)}")
        print(f"Categories: {df['category'].value_counts().to_dict()}")
        print(f"Sentiment distribution: {df['sentiment'].value_counts(normalize=True).to_dict()}")

if __name__ == "__main__":
    generator = EcommerceReviewGenerator(num_reviews=10000)
    df = generator.generate_dataset()
    generator.save_dataset(df, 'backend/data/raw/ecommerce_reviews')