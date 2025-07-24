# backend/nlp/emoji_processor.py
import re

class EmojiProcessor:
    """Process emojis using regex patterns without external dependencies"""
    
    def __init__(self):
        # Comprehensive emoji regex pattern
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002500-\U00002BEF"  # chinese char
            "\U00002702-\U000027B0"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"  # dingbats
            "\u3030"
            "]+", 
            flags=re.UNICODE
        )
        
        # Emoji sentiment mapping
        self.emoji_sentiments = {
            # Positive emojis
            '😀': 'positive', '😃': 'positive', '😄': 'positive', '😁': 'positive',
            '😆': 'positive', '😅': 'positive', '😂': 'positive', '🤣': 'positive',
            '😊': 'positive', '😇': 'positive', '🙂': 'positive', '🙃': 'positive',
            '😉': 'positive', '😌': 'positive', '😍': 'positive', '🥰': 'positive',
            '😘': 'positive', '😗': 'positive', '😙': 'positive', '😚': 'positive',
            '😋': 'positive', '😛': 'positive', '😜': 'positive', '🤪': 'positive',
            '😝': 'positive', '🤗': 'positive', '🤩': 'positive', '🥳': 'positive',
            '👍': 'positive', '👌': 'positive', '✌️': 'positive', '🤟': 'positive',
            '🤘': 'positive', '💪': 'positive', '👏': 'positive', '🙌': 'positive',
            '❤️': 'positive', '🧡': 'positive', '💛': 'positive', '💚': 'positive',
            '💙': 'positive', '💜': 'positive', '🖤': 'positive', '🤍': 'positive',
            '🤎': 'positive', '💕': 'positive', '💖': 'positive', '✨': 'positive',
            '⭐': 'positive', '🌟': 'positive', '💫': 'positive', '🎉': 'positive',
            '🎊': 'positive', '🎈': 'positive', '🎁': 'positive', '🏆': 'positive',
            
            # Negative emojis
            '😞': 'negative', '😔': 'negative', '😟': 'negative', '😕': 'negative',
            '🙁': 'negative', '☹️': 'negative', '😣': 'negative', '😖': 'negative',
            '😫': 'negative', '😩': 'negative', '🥺': 'negative', '😢': 'negative',
            '😭': 'negative', '😤': 'negative', '😠': 'negative', '😡': 'negative',
            '🤬': 'negative', '😰': 'negative', '😥': 'negative', '😓': 'negative',
            '🤯': 'negative', '😱': 'negative', '😨': 'negative', '😰': 'negative',
            '😥': 'negative', '😓': 'negative', '👎': 'negative', '💔': 'negative',
            '🚫': 'negative', '❌': 'negative', '⛔': 'negative', '🛑': 'negative',
            
            # Neutral emojis
            '😐': 'neutral', '😑': 'neutral', '😶': 'neutral', '🙄': 'neutral',
            '🤔': 'neutral', '🤨': 'neutral', '😏': 'neutral', '😒': 'neutral',
            '😬': 'neutral', '🤐': 'neutral', '😷': 'neutral', '🤒': 'neutral',
            '🤕': 'neutral', '😵': 'neutral', '🥴': 'neutral', '😪': 'neutral',
            '😴': 'neutral', '💤': 'neutral', '🤷': 'neutral', '🤦': 'neutral'
        }
    
    def extract_emojis(self, text):
        """Extract all emojis from text"""
        if not text:
            return []
        return self.emoji_pattern.findall(text)
    
    def remove_emojis(self, text):
        """Remove all emojis from text"""
        if not text:
            return text
        return self.emoji_pattern.sub(' ', text).strip()
    
    def replace_emojis_with_text(self, text):
        """Replace emojis with their text representation"""
        if not text:
            return text
            
        result = text
        emojis = self.extract_emojis(text)
        
        for emoji in emojis:
            if emoji in self.emoji_sentiments:
                sentiment = self.emoji_sentiments[emoji]
                result = result.replace(emoji, f' {sentiment}_emoji ')
            else:
                result = result.replace(emoji, ' emoji ')
        
        # Clean up multiple spaces
        result = ' '.join(result.split())
        return result
    
    def analyze_emoji_sentiment(self, text):
        """Analyze sentiment based on emojis in text"""
        emojis = self.extract_emojis(text)
        
        if not emojis:
            return {
                'has_emojis': False,
                'emoji_count': 0,
                'emoji_sentiment': None,
                'emoji_sentiment_score': 0
            }
        
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for emoji in emojis:
            sentiment = self.emoji_sentiments.get(emoji, 'neutral')
            sentiment_counts[sentiment] += 1
        
        # Calculate dominant emoji sentiment
        total_emojis = sum(sentiment_counts.values())
        dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        
        # Calculate emoji sentiment score (-1 to 1)
        score = (sentiment_counts['positive'] - sentiment_counts['negative']) / total_emojis
        
        return {
            'has_emojis': True,
            'emoji_count': total_emojis,
            'emoji_sentiment': dominant_sentiment,
            'emoji_sentiment_score': score,
            'emoji_breakdown': sentiment_counts,
            'emojis_found': emojis
        }
    
    def get_emoji_context(self, text, window_size=10):
        """Get context around emojis for better understanding"""
        contexts = []
        
        for match in self.emoji_pattern.finditer(text):
            emoji = match.group()
            start = max(0, match.start() - window_size)
            end = min(len(text), match.end() + window_size)
            
            context = {
                'emoji': emoji,
                'position': match.start(),
                'context_before': text[start:match.start()].strip(),
                'context_after': text[match.end():end].strip(),
                'sentiment': self.emoji_sentiments.get(emoji, 'unknown')
            }
            contexts.append(context)
        
        return contexts