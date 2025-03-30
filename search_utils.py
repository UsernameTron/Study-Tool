import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

# Download necessary NLTK data (will run on first import)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def preprocess_text(text):
    """Preprocess text for searching"""
    # Convert to lowercase and remove punctuation
    text = re.sub(r'[^\w\s]', '', text.lower())
    # Tokenize
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    return tokens

def index_content(content_dict):
    """Create a searchable index from content"""
    index = {}
    
    for section, content in content_dict.items():
        tokens = preprocess_text(content)
        for token in tokens:
            if token not in index:
                index[token] = []
            index[token].append(section)
    
    return index

def search_content(query, index, content_dict):
    """Search content using the index"""
    query_tokens = preprocess_text(query)
    results = {}
    
    for token in query_tokens:
        if token in index:
            for section in index[token]:
                if section not in results:
                    results[section] = 0
                results[section] += 1
    
    # Sort results by relevance
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    
    # Prepare search results with snippets
    formatted_results = []
    for section, score in sorted_results:
        content = content_dict[section]
        
        # Find a relevant snippet
        snippet = ""
        best_match_count = 0
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        for sentence in sentences:
            match_count = sum(1 for token in query_tokens if token.lower() in sentence.lower())
            if match_count > best_match_count:
                best_match_count = match_count
                snippet = sentence
        
        if not snippet and sentences:
            snippet = sentences[0]  # Use first sentence if no good match
            
        formatted_results.append({
            "section": section,
            "score": score,
            "snippet": snippet
        })
    
    return formatted_results
