#!/usr/bin/env python3
"""
Advanced Web Research - Enhanced Web Search System
Zaawansowany system wyszukiwania w internecie
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Advanced Web Research", description="Enhanced Web Search System", version="1.0.0")

# Add CORS middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Pydantic models
class WebSearchRequest(BaseModel):
    query: str
    search_type: str = "general"  # general, news, academic, images, videos
    language: str = "pl"
    max_results: int = 10
    time_range: Optional[str] = None  # past_hour, past_day, past_week, past_month, past_year
    domain: Optional[str] = None
    user_id: Optional[str] = None

class WebSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_found: int
    search_time: float
    suggestions: List[str]
    related_queries: List[str]
    timestamp: str

class ContentAnalysisRequest(BaseModel):
    url: str
    analysis_type: str = "full"  # full, summary, keywords, sentiment
    user_id: Optional[str] = None

class ContentAnalysisResponse(BaseModel):
    title: str
    content: str
    summary: str
    keywords: List[str]
    sentiment: Dict[str, float]
    language: str
    word_count: int
    reading_time: int
    timestamp: str

# Advanced Web Research System
class AdvancedWebResearch:
    def __init__(self):
        self.search_engines = {
            "google": "https://www.google.com/search",
            "bing": "https://www.bing.com/search",
            "duckduckgo": "https://duckduckgo.com/html"
        }
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        self.search_cache = {}
        self.content_cache = {}
    
    async def search_web(self, query: str, search_type: str = "general", 
                        language: str = "pl", max_results: int = 10,
                        time_range: str = None, domain: str = None) -> Dict[str, Any]:
        """Advanced web search with multiple engines"""
        try:
            start_time = datetime.now()
            
            # Prepare search parameters
            search_params = {
                "q": query,
                "hl": language,
                "num": max_results
            }
            
            # Add time range filter
            if time_range:
                search_params["tbs"] = f"qdr:{time_range}"
            
            # Add domain filter
            if domain:
                search_params["q"] = f"site:{domain} {query}"
            
            # Search multiple engines
            results = []
            for engine_name, engine_url in self.search_engines.items():
                try:
                    engine_results = await self.search_engine(engine_name, engine_url, search_params)
                    results.extend(engine_results)
                except Exception as e:
                    logger.error(f"Search engine {engine_name} failed: {e}")
                    continue
            
            # Remove duplicates and rank results
            unique_results = self.deduplicate_results(results)
            ranked_results = self.rank_results(unique_results, query)
            
            # Generate suggestions and related queries
            suggestions = self.generate_search_suggestions(query)
            related_queries = self.generate_related_queries(query)
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "results": ranked_results[:max_results],
                "total_found": len(ranked_results),
                "search_time": search_time,
                "suggestions": suggestions,
                "related_queries": related_queries
            }
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {
                "results": [],
                "total_found": 0,
                "search_time": 0.0,
                "suggestions": [],
                "related_queries": []
            }
    
    async def search_engine(self, engine_name: str, engine_url: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search specific engine"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(engine_url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self.parse_search_results(html, engine_name)
                    else:
                        logger.error(f"Search engine {engine_name} returned status {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Search engine {engine_name} error: {e}")
            return []
    
    def parse_search_results(self, html: str, engine_name: str) -> List[Dict[str, Any]]:
        """Parse search results from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            results = []
            
            if engine_name == "google":
                # Parse Google results
                for result in soup.find_all('div', class_='g'):
                    title_elem = result.find('h3')
                    link_elem = result.find('a')
                    snippet_elem = result.find('span', class_='aCOpRe')
                    
                    if title_elem and link_elem:
                        results.append({
                            "title": title_elem.get_text(),
                            "url": link_elem.get('href', ''),
                            "snippet": snippet_elem.get_text() if snippet_elem else "",
                            "engine": engine_name
                        })
            
            elif engine_name == "bing":
                # Parse Bing results
                for result in soup.find_all('li', class_='b_algo'):
                    title_elem = result.find('h2')
                    link_elem = result.find('a')
                    snippet_elem = result.find('p')
                    
                    if title_elem and link_elem:
                        results.append({
                            "title": title_elem.get_text(),
                            "url": link_elem.get('href', ''),
                            "snippet": snippet_elem.get_text() if snippet_elem else "",
                            "engine": engine_name
                        })
            
            elif engine_name == "duckduckgo":
                # Parse DuckDuckGo results
                for result in soup.find_all('div', class_='result'):
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem:
                        results.append({
                            "title": title_elem.get_text(),
                            "url": title_elem.get('href', ''),
                            "snippet": snippet_elem.get_text() if snippet_elem else "",
                            "engine": engine_name
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Result parsing failed for {engine_name}: {e}")
            return []
    
    def deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results"""
        try:
            seen_urls = set()
            unique_results = []
            
            for result in results:
                url = result.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
            
            return unique_results
            
        except Exception as e:
            logger.error(f"Deduplication failed: {e}")
            return results
    
    def rank_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rank results by relevance"""
        try:
            query_words = set(query.lower().split())
            
            for result in results:
                score = 0
                title = result.get("title", "").lower()
                snippet = result.get("snippet", "").lower()
                
                # Title relevance
                title_words = set(title.split())
                title_matches = len(query_words & title_words)
                score += title_matches * 3
                
                # Snippet relevance
                snippet_words = set(snippet.split())
                snippet_matches = len(query_words & snippet_words)
                score += snippet_matches * 2
                
                # URL relevance
                url = result.get("url", "").lower()
                url_matches = sum(1 for word in query_words if word in url)
                score += url_matches
                
                result["relevance_score"] = score
            
            # Sort by relevance score
            results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Result ranking failed: {e}")
            return results
    
    def generate_search_suggestions(self, query: str) -> List[str]:
        """Generate search suggestions"""
        try:
            suggestions = []
            
            # Add common search modifiers
            modifiers = ["tutorial", "guide", "how to", "best", "review", "comparison"]
            for modifier in modifiers:
                suggestions.append(f"{query} {modifier}")
            
            # Add question variations
            if not query.endswith("?"):
                suggestions.append(f"{query}?")
                suggestions.append(f"what is {query}")
                suggestions.append(f"how does {query} work")
            
            return suggestions[:5]  # Limit to 5 suggestions
            
        except Exception as e:
            logger.error(f"Search suggestions generation failed: {e}")
            return []
    
    def generate_related_queries(self, query: str) -> List[str]:
        """Generate related queries"""
        try:
            related = []
            
            # Add synonyms and variations
            synonyms = {
                "ai": ["artificial intelligence", "machine learning", "neural networks"],
                "programming": ["coding", "development", "software"],
                "business": ["company", "enterprise", "corporate"],
                "technology": ["tech", "innovation", "digital"]
            }
            
            query_lower = query.lower()
            for key, values in synonyms.items():
                if key in query_lower:
                    for synonym in values:
                        related.append(query.replace(key, synonym))
            
            # Add context variations
            contexts = ["2024", "latest", "new", "trends", "future"]
            for context in contexts:
                related.append(f"{query} {context}")
            
            return related[:5]  # Limit to 5 related queries
            
        except Exception as e:
            logger.error(f"Related queries generation failed: {e}")
            return []
    
    async def analyze_content(self, url: str, analysis_type: str = "full") -> Dict[str, Any]:
        """Analyze web content"""
        try:
            # Check cache first
            if url in self.content_cache:
                return self.content_cache[url]
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract content
                        title = soup.find('title')
                        title = title.get_text() if title else "No title"
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Get text content
                        text = soup.get_text()
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        content = ' '.join(chunk for chunk in chunks if chunk)
                        
                        # Generate summary
                        summary = self.generate_summary(content)
                        
                        # Extract keywords
                        keywords = self.extract_keywords(content)
                        
                        # Analyze sentiment
                        sentiment = self.analyze_sentiment(content)
                        
                        # Detect language
                        language = self.detect_language(content)
                        
                        # Calculate metrics
                        word_count = len(content.split())
                        reading_time = max(1, word_count // 200)  # 200 words per minute
                        
                        result = {
                            "title": title,
                            "content": content,
                            "summary": summary,
                            "keywords": keywords,
                            "sentiment": sentiment,
                            "language": language,
                            "word_count": word_count,
                            "reading_time": reading_time
                        }
                        
                        # Cache result
                        self.content_cache[url] = result
                        
                        return result
                    else:
                        raise HTTPException(status_code=response.status, detail="Failed to fetch content")
                        
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            raise HTTPException(status_code=500, detail="Content analysis failed")
    
    def generate_summary(self, content: str) -> str:
        """Generate content summary"""
        try:
            sentences = content.split('.')
            if len(sentences) <= 3:
                return content
            
            # Simple extractive summarization
            # Take first 3 sentences as summary
            summary_sentences = sentences[:3]
            return '. '.join(summary_sentences) + '.'
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return content[:200] + "..."
    
    def extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content"""
        try:
            # Simple keyword extraction
            words = content.lower().split()
            
            # Filter out common words
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "can", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"}
            
            # Count word frequency
            word_freq = {}
            for word in words:
                if len(word) > 3 and word not in stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords
            keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in keywords[:10]]  # Top 10 keywords
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
    
    def analyze_sentiment(self, content: str) -> Dict[str, float]:
        """Analyze content sentiment"""
        try:
            positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "awesome", "brilliant", "outstanding", "perfect"]
            negative_words = ["bad", "terrible", "awful", "horrible", "disgusting", "hate", "worst", "disappointing", "frustrating", "annoying"]
            
            words = content.lower().split()
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            total_words = len(words)
            if total_words == 0:
                return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
            
            positive_score = positive_count / total_words
            negative_score = negative_count / total_words
            neutral_score = 1.0 - positive_score - negative_score
            
            return {
                "positive": positive_score,
                "negative": negative_score,
                "neutral": max(0.0, neutral_score)
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
    
    def detect_language(self, content: str) -> str:
        """Detect content language"""
        try:
            # Simple language detection based on common words
            polish_words = ["i", "w", "na", "z", "do", "od", "że", "się", "nie", "jest", "być", "mieć", "może", "można", "trzeba", "powinien", "chce", "chcemy", "chcą", "mogą", "mogę", "możemy", "można", "trzeba", "powinien", "chce", "chcemy", "chcą", "mogą", "mogę", "możemy"]
            english_words = ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "can"]
            
            words = content.lower().split()
            polish_count = sum(1 for word in words if word in polish_words)
            english_count = sum(1 for word in words if word in english_words)
            
            if polish_count > english_count:
                return "pl"
            elif english_count > polish_count:
                return "en"
            else:
                return "unknown"
                
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return "unknown"

# Initialize research system
web_research = AdvancedWebResearch()

# API Endpoints
@app.post("/api/research/search", response_model=WebSearchResponse)
async def search_web(request: WebSearchRequest):
    """Advanced web search"""
    try:
        results = await web_research.search_web(
            query=request.query,
            search_type=request.search_type,
            language=request.language,
            max_results=request.max_results,
            time_range=request.time_range,
            domain=request.domain
        )
        
        return WebSearchResponse(
            results=results["results"],
            total_found=results["total_found"],
            search_time=results["search_time"],
            suggestions=results["suggestions"],
            related_queries=results["related_queries"],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        raise HTTPException(status_code=500, detail="Web search failed")

@app.post("/api/research/analyze", response_model=ContentAnalysisResponse)
async def analyze_content(request: ContentAnalysisRequest):
    """Analyze web content"""
    try:
        results = await web_research.analyze_content(
            url=request.url,
            analysis_type=request.analysis_type
        )
        
        return ContentAnalysisResponse(
            title=results["title"],
            content=results["content"],
            summary=results["summary"],
            keywords=results["keywords"],
            sentiment=results["sentiment"],
            language=results["language"],
            word_count=results["word_count"],
            reading_time=results["reading_time"],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Content analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Content analysis failed")

@app.get("/api/research/health")
async def research_health():
    """Health check for research service"""
    return {
        "status": "healthy",
        "service": "advanced_web_research",
        "version": "1.0.0",
        "search_engines": list(web_research.search_engines.keys()),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run("advanced_web_research:app", host="0.0.0.0", port=8004, reload=True)