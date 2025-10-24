#!/usr/bin/env python3
"""
Autonauka Pro - Real-time Learning System
System uczenia w locie - uczy się z każdej interakcji
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import sqlite3
import threading
import time

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Autonauka Pro", description="Real-time Learning System", version="2.0.0")

# Add CORS middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Pydantic models
class LearningData(BaseModel):
    user_id: str
    interaction_type: str
    input_data: str
    output_data: str
    context: Optional[Dict[str, Any]] = None
    feedback: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

class LearningInsight(BaseModel):
    pattern: str
    confidence: float
    frequency: int
    examples: List[str]
    recommendations: List[str]

class LearningResponse(BaseModel):
    learned: bool
    insights: List[LearningInsight]
    improvements: List[str]
    next_actions: List[str]

# Real-time Learning System
class AutonaukaPro:
    def __init__(self):
        self.db_path = "autonauka.db"
        self.learning_queue = asyncio.Queue()
        self.patterns = {}
        self.user_profiles = {}
        self.learning_thread = None
        self.is_learning = False
        
        # Initialize database
        self.init_database()
        
        # Start learning thread
        self.start_learning_thread()
    
    def init_database(self):
        """Initialize learning database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create learning data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    interaction_type TEXT NOT NULL,
                    input_data TEXT NOT NULL,
                    output_data TEXT NOT NULL,
                    context TEXT,
                    feedback TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    confidence REAL DEFAULT 0.5,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create user profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    profile_data TEXT NOT NULL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Learning database initialized")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    def start_learning_thread(self):
        """Start background learning thread"""
        try:
            self.is_learning = True
            self.learning_thread = threading.Thread(target=self.learning_loop, daemon=True)
            self.learning_thread.start()
            logger.info("Learning thread started")
        except Exception as e:
            logger.error(f"Learning thread start failed: {e}")
    
    def learning_loop(self):
        """Main learning loop running in background"""
        while self.is_learning:
            try:
                # Process learning queue
                if not self.learning_queue.empty():
                    learning_data = self.learning_queue.get_nowait()
                    self.process_learning_data(learning_data)
                
                # Analyze patterns every 30 seconds
                if int(time.time()) % 30 == 0:
                    self.analyze_patterns()
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Learning loop error: {e}")
                time.sleep(5)
    
    async def add_learning_data(self, learning_data: LearningData):
        """Add new learning data to queue"""
        try:
            learning_data.timestamp = datetime.now().isoformat()
            await self.learning_queue.put(learning_data)
            
            # Also store in database immediately
            self.store_learning_data(learning_data)
            
            logger.info(f"Learning data added for user {learning_data.user_id}")
            
        except Exception as e:
            logger.error(f"Failed to add learning data: {e}")
    
    def store_learning_data(self, learning_data: LearningData):
        """Store learning data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO learning_data 
                (user_id, interaction_type, input_data, output_data, context, feedback, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                learning_data.user_id,
                learning_data.interaction_type,
                learning_data.input_data,
                json.dumps(learning_data.context) if learning_data.context else None,
                json.dumps(learning_data.feedback) if learning_data.feedback else None,
                learning_data.timestamp
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store learning data: {e}")
    
    def process_learning_data(self, learning_data: LearningData):
        """Process learning data for patterns"""
        try:
            # Extract patterns from input/output
            patterns = self.extract_patterns(learning_data)
            
            # Update pattern database
            for pattern in patterns:
                self.update_pattern(pattern)
            
            # Update user profile
            self.update_user_profile(learning_data)
            
            logger.info(f"Processed learning data for user {learning_data.user_id}")
            
        except Exception as e:
            logger.error(f"Failed to process learning data: {e}")
    
    def extract_patterns(self, learning_data: LearningData) -> List[Dict[str, Any]]:
        """Extract patterns from learning data"""
        try:
            patterns = []
            
            # Text patterns
            if learning_data.input_data and learning_data.output_data:
                # Question-answer patterns
                if learning_data.interaction_type == "chat":
                    patterns.append({
                        "type": "qa_pattern",
                        "data": {
                            "question": learning_data.input_data,
                            "answer": learning_data.output_data,
                            "context": learning_data.context
                        },
                        "confidence": 0.8
                    })
                
                # Keyword patterns
                input_words = learning_data.input_data.lower().split()
                output_words = learning_data.output_data.lower().split()
                
                common_words = set(input_words) & set(output_words)
                if common_words:
                    patterns.append({
                        "type": "keyword_pattern",
                        "data": {
                            "keywords": list(common_words),
                            "context": learning_data.context
                        },
                        "confidence": 0.6
                    })
                
                # Sentiment patterns
                sentiment = self.analyze_sentiment(learning_data.input_data)
                if sentiment != "neutral":
                    patterns.append({
                        "type": "sentiment_pattern",
                        "data": {
                            "sentiment": sentiment,
                            "input": learning_data.input_data,
                            "output": learning_data.output_data
                        },
                        "confidence": 0.7
                    })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Pattern extraction failed: {e}")
            return []
    
    def analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        try:
            positive_words = ["dobry", "świetny", "wspaniały", "super", "fajny", "miły"]
            negative_words = ["zły", "gorszy", "okropny", "brzydki", "smutny", "zły"]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                return "positive"
            elif negative_count > positive_count:
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return "neutral"
    
    def update_pattern(self, pattern: Dict[str, Any]):
        """Update pattern in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if pattern exists
            cursor.execute('''
                SELECT id, frequency FROM patterns 
                WHERE pattern_type = ? AND pattern_data = ?
            ''', (pattern["type"], json.dumps(pattern["data"])))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing pattern
                pattern_id, frequency = result
                new_frequency = frequency + 1
                new_confidence = (pattern["confidence"] + (frequency * 0.5)) / (frequency + 1)
                
                cursor.execute('''
                    UPDATE patterns 
                    SET frequency = ?, confidence = ?, last_seen = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_frequency, new_confidence, pattern_id))
            else:
                # Insert new pattern
                cursor.execute('''
                    INSERT INTO patterns (pattern_type, pattern_data, frequency, confidence)
                    VALUES (?, ?, 1, ?)
                ''', (pattern["type"], json.dumps(pattern["data"]), pattern["confidence"]))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Pattern update failed: {e}")
    
    def update_user_profile(self, learning_data: LearningData):
        """Update user profile with learning data"""
        try:
            user_id = learning_data.user_id
            
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = {
                    "interaction_count": 0,
                    "preferred_topics": {},
                    "response_style": "neutral",
                    "learning_speed": "normal",
                    "last_updated": datetime.now().isoformat()
                }
            
            profile = self.user_profiles[user_id]
            profile["interaction_count"] += 1
            
            # Update preferred topics
            if learning_data.context and "topic" in learning_data.context:
                topic = learning_data.context["topic"]
                if topic not in profile["preferred_topics"]:
                    profile["preferred_topics"][topic] = 0
                profile["preferred_topics"][topic] += 1
            
            # Update response style based on output
            if learning_data.output_data:
                sentiment = self.analyze_sentiment(learning_data.output_data)
                if sentiment != "neutral":
                    profile["response_style"] = sentiment
            
            profile["last_updated"] = datetime.now().isoformat()
            
            # Store in database
            self.store_user_profile(user_id, profile)
            
        except Exception as e:
            logger.error(f"User profile update failed: {e}")
    
    def store_user_profile(self, user_id: str, profile: Dict[str, Any]):
        """Store user profile in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_profiles (user_id, profile_data, last_updated)
                VALUES (?, ?, ?)
            ''', (user_id, json.dumps(profile), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"User profile storage failed: {e}")
    
    def analyze_patterns(self):
        """Analyze patterns for insights"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get frequent patterns
            cursor.execute('''
                SELECT pattern_type, pattern_data, frequency, confidence
                FROM patterns 
                WHERE frequency > 2
                ORDER BY frequency DESC
                LIMIT 10
            ''')
            
            patterns = cursor.fetchall()
            
            for pattern in patterns:
                pattern_type, pattern_data, frequency, confidence = pattern
                
                if pattern_type not in self.patterns:
                    self.patterns[pattern_type] = []
                
                self.patterns[pattern_type].append({
                    "data": json.loads(pattern_data),
                    "frequency": frequency,
                    "confidence": confidence
                })
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
    
    def get_learning_insights(self, user_id: str) -> List[LearningInsight]:
        """Get learning insights for user"""
        try:
            insights = []
            
            # Get user-specific patterns
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT interaction_type, COUNT(*) as count
                FROM learning_data 
                WHERE user_id = ?
                GROUP BY interaction_type
                ORDER BY count DESC
            ''', (user_id,))
            
            user_patterns = cursor.fetchall()
            
            for pattern_type, count in user_patterns:
                if count > 3:  # Only patterns with enough data
                    insights.append(LearningInsight(
                        pattern=f"Użytkownik często używa {pattern_type}",
                        confidence=min(count / 10, 1.0),
                        frequency=count,
                        examples=[f"Przykład {i+1}" for i in range(min(count, 3))],
                        recommendations=[f"Zoptymalizuj obsługę {pattern_type}"]
                    ))
            
            conn.close()
            
            return insights
            
        except Exception as e:
            logger.error(f"Learning insights failed: {e}")
            return []
    
    def get_improvements(self, user_id: str) -> List[str]:
        """Get improvement suggestions"""
        try:
            improvements = []
            
            # Get user profile
            if user_id in self.user_profiles:
                profile = self.user_profiles[user_id]
                
                if profile["interaction_count"] < 5:
                    improvements.append("Zbierz więcej danych o użytkowniku")
                
                if profile["response_style"] == "negative":
                    improvements.append("Popraw obsługę negatywnych emocji")
                
                if len(profile["preferred_topics"]) < 3:
                    improvements.append("Rozszerz zakres tematów")
            
            # Get pattern-based improvements
            if user_id in self.patterns:
                for pattern_type, patterns in self.patterns.items():
                    if len(patterns) > 5:
                        improvements.append(f"Zoptymalizuj obsługę {pattern_type}")
            
            return improvements
            
        except Exception as e:
            logger.error(f"Improvements generation failed: {e}")
            return []
    
    def get_next_actions(self, user_id: str) -> List[str]:
        """Get next actions based on learning"""
        try:
            actions = []
            
            # Get user profile
            if user_id in self.user_profiles:
                profile = self.user_profiles[user_id]
                
                if profile["interaction_count"] > 10:
                    actions.append("Przeanalizuj wzorce użytkownika")
                
                if profile["response_style"] == "positive":
                    actions.append("Wykorzystaj pozytywne nastawienie")
                
                if len(profile["preferred_topics"]) > 5:
                    actions.append("Personalizuj odpowiedzi na podstawie zainteresowań")
            
            return actions
            
        except Exception as e:
            logger.error(f"Next actions generation failed: {e}")
            return []

# Initialize learning system
autonauka = AutonaukaPro()

# API Endpoints
@app.post("/api/autonauka/learn", response_model=LearningResponse)
async def learn_from_interaction(learning_data: LearningData, background_tasks: BackgroundTasks):
    """Learn from user interaction in real-time"""
    try:
        # Add to learning queue
        await autonauka.add_learning_data(learning_data)
        
        # Get insights
        insights = autonauka.get_learning_insights(learning_data.user_id)
        
        # Get improvements
        improvements = autonauka.get_improvements(learning_data.user_id)
        
        # Get next actions
        next_actions = autonauka.get_next_actions(learning_data.user_id)
        
        return LearningResponse(
            learned=True,
            insights=insights,
            improvements=improvements,
            next_actions=next_actions
        )
        
    except Exception as e:
        logger.error(f"Learning failed: {e}")
        raise HTTPException(status_code=500, detail="Learning failed")

@app.get("/api/autonauka/insights/{user_id}")
async def get_user_insights(user_id: str):
    """Get learning insights for user"""
    try:
        insights = autonauka.get_learning_insights(user_id)
        improvements = autonauka.get_improvements(user_id)
        next_actions = autonauka.get_next_actions(user_id)
        
        return {
            "user_id": user_id,
            "insights": insights,
            "improvements": improvements,
            "next_actions": next_actions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Insights retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Insights retrieval failed")

@app.get("/api/autonauka/patterns")
async def get_patterns():
    """Get all learned patterns"""
    try:
        return {
            "patterns": autonauka.patterns,
            "total_patterns": sum(len(patterns) for patterns in autonauka.patterns.values()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Patterns retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Patterns retrieval failed")

@app.get("/api/autonauka/health")
async def autonauka_health():
    """Health check for autonauka service"""
    return {
        "status": "healthy",
        "service": "autonauka_pro",
        "version": "2.0.0",
        "learning_active": autonauka.is_learning,
        "queue_size": autonauka.learning_queue.qsize(),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run("autonauka_pro:app", host="0.0.0.0", port=8002, reload=True)