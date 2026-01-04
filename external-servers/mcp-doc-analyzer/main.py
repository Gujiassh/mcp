"""
Document Analyzer MCP Server
A FastMCP server for analyzing text documents with sentiment, keywords, and readability analysis.
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import Counter
from fastmcp import FastMCP
from pydantic import BaseModel


class DocumentData(BaseModel):
    """Document data model"""
    title: str
    content: str
    author: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []


class DocumentAnalysis(BaseModel):
    """Document analysis result model"""
    document_id: str
    sentiment: Dict[str, Any]
    keywords: List[Dict[str, Any]]
    readability: Dict[str, Any]
    stats: Dict[str, Any]
    timestamp: str

class DocumentStore:
    """Simple in-memory document store with sample data"""
    
    def __init__(self):
        self.documents: Dict[str, Dict] = {}
        self.next_id = 1
        self._initialize_sample_documents()
    
    def _initialize_sample_documents(self):
        """Initialize with 15+ sample documents"""
        sample_docs = [
            {
                "title": "The Benefits of Renewable Energy",
                "content": "Renewable energy sources like solar and wind power offer tremendous benefits for our planet. They reduce greenhouse gas emissions, create jobs, and provide sustainable solutions for future generations. Solar panels and wind turbines are becoming more efficient and cost-effective each year.",
                "author": "Dr. Sarah Johnson",
                "category": "Environment",
                "tags": ["renewable", "energy", "sustainability"]
            },
            {
                "title": "Introduction to Machine Learning",
                "content": "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed. It involves algorithms that can identify patterns in data and make predictions. Popular techniques include supervised learning, unsupervised learning, and reinforcement learning.",
                "author": "Prof. Alex Chen",
                "category": "Technology",
                "tags": ["machine learning", "AI", "algorithms"]
            },
            {
                "title": "Healthy Eating Habits",
                "content": "Maintaining a balanced diet is crucial for good health. Include plenty of fruits, vegetables, whole grains, and lean proteins in your meals. Limit processed foods, sugary drinks, and excessive amounts of saturated fats. Regular meal times and proper hydration are equally important.",
                "author": "Lisa Martinez",
                "category": "Health",
                "tags": ["nutrition", "diet", "wellness"]
            },
            {
                "title": "The Art of Photography",
                "content": "Photography is both an art and a science. Understanding composition, lighting, and timing can dramatically improve your photos. The rule of thirds, leading lines, and proper exposure are fundamental concepts every photographer should master.",
                "author": "Michael Thompson",
                "category": "Arts",
                "tags": ["photography", "composition", "art"]
            },
            {
                "title": "Climate Change Impact",
                "content": "Climate change poses significant challenges to our planet. Rising temperatures, melting ice caps, and extreme weather events are becoming more frequent. We must take immediate action to reduce carbon emissions and transition to sustainable practices.",
                "author": "Dr. Emma Wilson",
                "category": "Environment",
                "tags": ["climate", "global warming", "environment"]
            },
            {
                "title": "Financial Planning for Beginners",
                "content": "Starting your financial journey can seem overwhelming, but it doesn't have to be. Begin with creating a budget, building an emergency fund, and understanding the basics of investing. Compound interest is your friend when you start early.",
                "author": "Robert Davis",
                "category": "Finance",
                "tags": ["finance", "budgeting", "investing"]
            },
            {
                "title": "The Future of Transportation",
                "content": "Transportation is evolving rapidly with electric vehicles, autonomous driving, and hyperloop technology. These innovations promise to reduce emissions, improve safety, and revolutionize how we move people and goods.",
                "author": "Jennifer Lee",
                "category": "Technology",
                "tags": ["transportation", "electric vehicles", "innovation"]
            },
            {
                "title": "Effective Team Communication",
                "content": "Clear communication is the foundation of successful teams. Active listening, regular feedback, and open dialogue foster collaboration. Use appropriate communication channels and be respectful of different perspectives and working styles.",
                "author": "David Park",
                "category": "Business",
                "tags": ["communication", "teamwork", "leadership"]
            },
            {
                "title": "Gardening for Beginners",
                "content": "Starting a garden can be incredibly rewarding. Choose plants suitable for your climate and soil type. Proper watering, sunlight, and fertilization are essential for healthy plant growth. Start small and expand your garden as you gain experience.",
                "author": "Mary Rodriguez",
                "category": "Lifestyle",
                "tags": ["gardening", "plants", "outdoor"]
            },
            {
                "title": "The Science of Sleep",
                "content": "Sleep is essential for physical and mental health. During sleep, our bodies repair tissues, consolidate memories, and regulate hormones. Most adults need 7-9 hours of quality sleep per night for optimal functioning.",
                "author": "Dr. James Williams",
                "category": "Health",
                "tags": ["sleep", "health", "wellness"]
            },
            {
                "title": "Digital Marketing Strategies",
                "content": "Digital marketing has transformed how businesses reach customers. Social media, content marketing, and search engine optimization are key components. Understanding your target audience and measuring campaign performance are crucial for success.",
                "author": "Amanda Clark",
                "category": "Business",
                "tags": ["marketing", "digital", "social media"]
            },
            {
                "title": "Mindfulness and Meditation",
                "content": "Mindfulness practices can reduce stress and improve mental clarity. Regular meditation, even for just 10 minutes daily, can have profound benefits. Focus on breathing, body awareness, and present-moment attention.",
                "author": "Sarah Kumar",
                "category": "Wellness",
                "tags": ["mindfulness", "meditation", "stress relief"]
            },
            {
                "title": "Sustainable Living Tips",
                "content": "Small changes in daily habits can make a big environmental impact. Reduce waste, conserve energy, choose eco-friendly products, and support sustainable businesses. Every action contributes to a healthier planet.",
                "author": "Green Living Team",
                "category": "Environment",
                "tags": ["sustainability", "eco-friendly", "green living"]
            },
            {
                "title": "The Power of Reading",
                "content": "Reading books expands knowledge, improves vocabulary, and enhances critical thinking skills. Whether fiction or non-fiction, books provide entertainment, education, and personal growth opportunities. Make reading a daily habit.",
                "author": "Library Association",
                "category": "Education",
                "tags": ["reading", "books", "education"]
            },
            {
                "title": "Coding Best Practices",
                "content": "Writing clean, maintainable code is essential for software development. Use meaningful variable names, write comments, follow coding standards, and test your code regularly. Code review and refactoring improve code quality over time.",
                "author": "Tech Team",
                "category": "Technology",
                "tags": ["coding", "programming", "best practices"]
            },
            {
                "title": "Travel Safety Tips",
                "content": "Traveling safely requires preparation and awareness. Research your destination, keep copies of important documents, stay alert in crowded areas, and trust your instincts. Travel insurance provides additional peace of mind.",
                "author": "Travel Safety Council",
                "category": "Travel",
                "tags": ["travel", "safety", "tips"]
            }
        ]
        
        for doc_data in sample_docs:
            self.add_document(doc_data)
    
    def add_document(self, doc_data: Dict) -> str:
        """Add a new document to the store"""
        doc_id = str(self.next_id)
        self.documents[doc_id] = {
            "id": doc_id,
            "title": doc_data["title"],
            "content": doc_data["content"],
            "author": doc_data.get("author"),
            "category": doc_data.get("category"),
            "tags": doc_data.get("tags", []),
            "created_at": datetime.now().isoformat()
        }
        self.next_id += 1
        return doc_id
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get a document by ID"""
        return self.documents.get(doc_id)
    
    def search_documents(self, query: str) -> List[Dict]:
        """Search documents by content, title, or tags"""
        query = query.lower()
        results = []
        
        for doc in self.documents.values():
            if (query in doc["title"].lower() or 
                query in doc["content"].lower() or 
                any(query in tag.lower() for tag in doc["tags"])):
                results.append(doc)
        
        return results
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents"""
        return list(self.documents.values())


class TextAnalyzer:
    """Text analysis utilities"""
    
    # Simple sentiment word lists
    POSITIVE_WORDS = {
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome',
        'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'delighted',
        'benefits', 'advantages', 'success', 'effective', 'efficient', 'improve',
        'better', 'best', 'perfect', 'outstanding', 'remarkable', 'positive',
        'opportunity', 'solution', 'helpful', 'useful', 'valuable', 'important',
        'essential', 'crucial', 'significant', 'rewarding', 'promising'
    }
    
    NEGATIVE_WORDS = {
        'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'sad',
        'disappointed', 'frustrated', 'angry', 'annoyed', 'problems', 'issues',
        'challenges', 'difficult', 'hard', 'impossible', 'failure', 'fail',
        'worst', 'poor', 'disappointing', 'negative', 'wrong', 'error',
        'mistakes', 'concerning', 'worried', 'stress', 'overwhelming'
    }
    
    # Common stop words
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
        'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'all', 'any',
        'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'not',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now'
    }
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text for analysis"""
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', '', text.lower())
        return text
    
    @staticmethod
    def get_words(text: str) -> List[str]:
        """Extract words from text"""
        clean_text = TextAnalyzer.clean_text(text)
        return [word for word in clean_text.split() if word]
    
    @staticmethod
    def get_sentences(text: str) -> List[str]:
        """Extract sentences from text"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def analyze_sentiment(text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        words = TextAnalyzer.get_words(text)
        
        positive_count = sum(1 for word in words if word in TextAnalyzer.POSITIVE_WORDS)
        negative_count = sum(1 for word in words if word in TextAnalyzer.NEGATIVE_WORDS)
        total_words = len(words)
        
        if total_words == 0:
            return {"sentiment": "neutral", "confidence": 0.0, "scores": {"positive": 0, "negative": 0, "neutral": 0}}
        
        positive_score = positive_count / total_words
        negative_score = negative_count / total_words
        
        # Determine overall sentiment
        if positive_score > negative_score:
            sentiment = "positive"
            confidence = positive_score
        elif negative_score > positive_score:
            sentiment = "negative"
            confidence = negative_score
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 3),
            "scores": {
                "positive": round(positive_score, 3),
                "negative": round(negative_score, 3),
                "neutral": round(1 - positive_score - negative_score, 3)
            }
        }
    
    @staticmethod
    def extract_keywords(text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Extract keywords from text"""
        words = TextAnalyzer.get_words(text)
        
        # Filter out stop words and short words
        filtered_words = [
            word for word in words 
            if word not in TextAnalyzer.STOP_WORDS and len(word) > 2
        ]
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Get top keywords
        top_keywords = word_counts.most_common(limit)
        
        total_words = len(filtered_words)
        keywords = []
        
        for word, count in top_keywords:
            keywords.append({
                "word": word,
                "frequency": count,
                "relevance": round(count / total_words, 3) if total_words > 0 else 0
            })
        
        return keywords
    
    @staticmethod
    def calculate_readability(text: str) -> Dict[str, Any]:
        """Calculate readability metrics"""
        words = TextAnalyzer.get_words(text)
        sentences = TextAnalyzer.get_sentences(text)
        
        if not sentences or not words:
            return {
                "flesch_reading_ease": 0,
                "flesch_grade_level": 0,
                "avg_sentence_length": 0,
                "avg_word_length": 0,
                "difficulty": "unknown"
            }
        
        # Calculate basic metrics
        total_words = len(words)
        total_sentences = len(sentences)
        total_syllables = sum(TextAnalyzer.count_syllables(word) for word in words)
        
        avg_sentence_length = total_words / total_sentences
        avg_syllables_per_word = total_syllables / total_words
        avg_word_length = sum(len(word) for word in words) / total_words
        
        # Flesch Reading Ease Score
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))  # Clamp between 0-100
        
        # Flesch-Kincaid Grade Level
        grade_level = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
        grade_level = max(0, grade_level)
        
        # Determine difficulty level
        if flesch_score >= 90:
            difficulty = "very easy"
        elif flesch_score >= 80:
            difficulty = "easy"
        elif flesch_score >= 70:
            difficulty = "fairly easy"
        elif flesch_score >= 60:
            difficulty = "standard"
        elif flesch_score >= 50:
            difficulty = "fairly difficult"
        elif flesch_score >= 30:
            difficulty = "difficult"
        else:
            difficulty = "very difficult"
        
        return {
            "flesch_reading_ease": round(flesch_score, 2),
            "flesch_grade_level": round(grade_level, 2),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "avg_word_length": round(avg_word_length, 2),
            "difficulty": difficulty
        }
    
    @staticmethod
    def count_syllables(word: str) -> int:
        """Count syllables in a word (simple approximation)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not previous_was_vowel:
                    syllable_count += 1
                previous_was_vowel = True
            else:
                previous_was_vowel = False
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    @staticmethod
    def get_text_stats(text: str) -> Dict[str, Any]:
        """Get basic text statistics"""
        words = TextAnalyzer.get_words(text)
        sentences = TextAnalyzer.get_sentences(text)
        
        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "character_count": len(text),
            "character_count_no_spaces": len(text.replace(' ', '')),
            "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]),
            "avg_words_per_sentence": round(len(words) / len(sentences), 2) if sentences else 0
        }


# Initialize FastMCP server
mcp = FastMCP("Document Analyzer")
document_store = DocumentStore()


@mcp.tool()
def analyze_document(document_id: str) -> Dict[str, Any]:
    """
    Perform complete analysis of a document including sentiment, keywords, readability, and statistics.
    
    Args:
        document_id: The ID of the document to analyze
        
    Returns:
        Complete analysis results for the document
    """
    document = document_store.get_document(document_id)
    if not document:
        return {"error": f"Document with ID {document_id} not found"}
    
    text = document["content"]
    
    # Perform all analyses
    sentiment = TextAnalyzer.analyze_sentiment(text)
    keywords = TextAnalyzer.extract_keywords(text)
    readability = TextAnalyzer.calculate_readability(text)
    stats = TextAnalyzer.get_text_stats(text)
    
    return {
        "document_id": document_id,
        "title": document["title"],
        "author": document["author"],
        "category": document["category"],
        "sentiment": sentiment,
        "keywords": keywords,
        "readability": readability,
        "stats": stats,
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def get_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment of any text.
    
    Args:
        text: The text to analyze for sentiment
        
    Returns:
        Sentiment analysis results
    """
    return TextAnalyzer.analyze_sentiment(text)


@mcp.tool()
def extract_keywords(text: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Extract top keywords from text.
    
    Args:
        text: The text to extract keywords from
        limit: Maximum number of keywords to return (default: 10)
        
    Returns:
        List of keywords with frequency and relevance scores
    """
    return TextAnalyzer.extract_keywords(text, limit)


@mcp.tool()
def add_document(title: str, content: str, author: str|None = None, category: str|None = None, tags: List[str]|None = None) -> Dict[str, Any]:
    """
    Add a new document to the document store.
    
    Args:
        title: Document title
        content: Document content
        author: Document author (optional)
        category: Document category (optional)
        tags: List of tags (optional)
        
    Returns:
        Information about the added document
    """
    if tags is None:
        tags = []
    
    doc_data = {
        "title": title,
        "content": content,
        "author": author,
        "category": category,
        "tags": tags
    }
    
    doc_id = document_store.add_document(doc_data)
    return {
        "document_id": doc_id,
        "title": title,
        "status": "added",
        "message": f"Document '{title}' added successfully with ID {doc_id}"
    }


@mcp.tool()
def search_documents(query: str) -> List[Dict[str, Any]]:
    """
    Search documents by content, title, or tags.
    
    Args:
        query: Search query string
        
    Returns:
        List of matching documents
    """
    results = document_store.search_documents(query)
    return [
        {
            "document_id": doc["id"],
            "title": doc["title"],
            "author": doc["author"],
            "category": doc["category"],
            "tags": doc["tags"],
            "snippet": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
        }
        for doc in results
    ]


@mcp.tool()
def list_documents() -> List[Dict[str, Any]]:
    """
    List all documents in the store.
    
    Returns:
        List of all documents with basic information
    """
    documents = document_store.get_all_documents()
    return [
        {
            "document_id": doc["id"],
            "title": doc["title"],
            "author": doc["author"],
            "category": doc["category"],
            "tags": doc["tags"],
            "created_at": doc["created_at"]
        }
        for doc in documents
    ]


@mcp.tool()
def get_document_info(document_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific document.
    
    Args:
        document_id: The ID of the document to retrieve
        
    Returns:
        Document information and metadata
    """
    document = document_store.get_document(document_id)
    if not document:
        return {"error": f"Document with ID {document_id} not found"}
    
    return document


@mcp.tool()
def get_readability_score(text: str) -> Dict[str, Any]:
    """
    Calculate readability metrics for any text.
    
    Args:
        text: The text to analyze for readability
        
    Returns:
        Readability metrics including Flesch scores and difficulty level
    """
    return TextAnalyzer.calculate_readability(text)


@mcp.tool()
def get_text_statistics(text: str) -> Dict[str, Any]:
    """
    Get basic statistics for any text.
    
    Args:
        text: The text to analyze
        
    Returns:
        Text statistics including word count, sentence count, etc.
    """
    return TextAnalyzer.get_text_stats(text)


if __name__ == "__main__":
    mcp.run()