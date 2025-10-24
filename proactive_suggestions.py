#!/usr/bin/env python3
"""
Proactive Suggestions - Intelligent Suggestions System
System proaktywnych sugestii - przewiduje potrzeby użytkownika
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
app = FastAPI(title="Proactive Suggestions", description="Intelligent Suggestions System", version="1.0.0")

# Add CORS middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Pydantic models
class SuggestionRequest(BaseModel):
    user_id: str
    context: Dict[str, Any]
    current_activity: str
    time_of_day: Optional[str] = None
    location: Optional[str] = None

class SuggestionResponse(BaseModel):
    suggestions: List[Dict[str, Any]]
    confidence: float
    reasoning: List[str]
    personalized: bool
    timestamp: str

class SuggestionFeedback(BaseModel):
    user_id: str
    suggestion_id: str
    feedback: str  # "accepted", "rejected", "ignored"
    context: Optional[Dict[str, Any]] = None

# Proactive Suggestions System
class ProactiveSuggestions:
    def __init__(self):
        self.db_path = "suggestions.db"
        self.user_patterns = {}
        self.suggestion_templates = {}
        self.feedback_history = {}
        
        # Initialize database
        self.init_database()
        
        # Load suggestion templates
        self.load_suggestion_templates()
    
    def init_database(self):
        """Initialize suggestions database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create suggestions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    suggestion_type TEXT NOT NULL,
                    suggestion_data TEXT NOT NULL,
                    context TEXT,
                    confidence REAL DEFAULT 0.5,
                    feedback TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create user patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_patterns (
                    user_id TEXT PRIMARY KEY,
                    patterns TEXT NOT NULL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Suggestions database initialized")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    def load_suggestion_templates(self):
        """Load suggestion templates"""
        try:
            self.suggestion_templates = {
                "morning": {
                    "work": [
                        "Sprawdź kalendarz na dziś",
                        "Przygotuj listę zadań",
                        "Sprawdź e-maile",
                        "Zaplanuj przerwy"
                    ],
                    "personal": [
                        "Sprawdź pogodę",
                        "Zaplanuj posiłki",
                        "Sprawdź wiadomości",
                        "Zrób listę zakupów"
                    ]
                },
                "afternoon": {
                    "work": [
                        "Sprawdź postęp zadań",
                        "Zaplanuj jutro",
                        "Odpowiedz na e-maile",
                        "Przygotuj raport"
                    ],
                    "personal": [
                        "Sprawdź wiadomości",
                        "Zaplanuj wieczór",
                        "Sprawdź finanse",
                        "Zrób zakupy"
                    ]
                },
                "evening": {
                    "work": [
                        "Podsumuj dzień",
                        "Zaplanuj jutro",
                        "Zapisz notatki",
                        "Sprawdź e-maile"
                    ],
                    "personal": [
                        "Sprawdź wiadomości",
                        "Zaplanuj jutro",
                        "Sprawdź finanse",
                        "Przygotuj się do snu"
                    ]
                }
            }
            
            logger.info("Suggestion templates loaded")
            
        except Exception as e:
            logger.error(f"Template loading failed: {e}")
    
    def analyze_user_patterns(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user patterns for suggestions"""
        try:
            patterns = {
                "preferred_times": [],
                "common_activities": [],
                "frequent_locations": [],
                "interaction_style": "neutral",
                "suggestion_preferences": []
            }
            
            # Get user data from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT suggestion_type, context, feedback, created_at
                FROM suggestions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 50
            ''', (user_id,))
            
            user_data = cursor.fetchall()
            
            # Analyze patterns
            for suggestion_type, context_data, feedback, created_at in user_data:
                if context_data:
                    context_obj = json.loads(context_data)
                    
                    # Time patterns
                    if "time_of_day" in context_obj:
                        patterns["preferred_times"].append(context_obj["time_of_day"])
                    
                    # Activity patterns
                    if "current_activity" in context_obj:
                        patterns["common_activities"].append(context_obj["current_activity"])
                    
                    # Location patterns
                    if "location" in context_obj:
                        patterns["frequent_locations"].append(context_obj["location"])
                    
                    # Feedback patterns
                    if feedback:
                        if feedback == "accepted":
                            patterns["suggestion_preferences"].append(suggestion_type)
                        elif feedback == "rejected":
                            patterns["suggestion_preferences"].remove(suggestion_type) if suggestion_type in patterns["suggestion_preferences"] else None
            
            conn.close()
            
            # Calculate most common patterns
            if patterns["preferred_times"]:
                patterns["preferred_times"] = max(set(patterns["preferred_times"]), key=patterns["preferred_times"].count)
            
            if patterns["common_activities"]:
                patterns["common_activities"] = max(set(patterns["common_activities"]), key=patterns["common_activities"].count)
            
            if patterns["frequent_locations"]:
                patterns["frequent_locations"] = max(set(patterns["frequent_locations"]), key=patterns["frequent_locations"].count)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return {}
    
    def generate_suggestions(self, user_id: str, context: Dict[str, Any], 
                           current_activity: str, time_of_day: str = None) -> List[Dict[str, Any]]:
        """Generate proactive suggestions"""
        try:
            suggestions = []
            
            # Analyze user patterns
            patterns = self.analyze_user_patterns(user_id, context)
            
            # Determine time of day
            if not time_of_day:
                current_hour = datetime.now().hour
                if 6 <= current_hour < 12:
                    time_of_day = "morning"
                elif 12 <= current_hour < 18:
                    time_of_day = "afternoon"
                else:
                    time_of_day = "evening"
            
            # Get base suggestions from templates
            base_suggestions = []
            if time_of_day in self.suggestion_templates:
                if current_activity in self.suggestion_templates[time_of_day]:
                    base_suggestions = self.suggestion_templates[time_of_day][current_activity]
                else:
                    # Use general suggestions for the time of day
                    all_activities = self.suggestion_templates[time_of_day]
                    base_suggestions = []
                    for activity_suggestions in all_activities.values():
                        base_suggestions.extend(activity_suggestions)
            
            # Generate personalized suggestions
            for i, suggestion_text in enumerate(base_suggestions[:5]):  # Limit to 5 suggestions
                suggestion = {
                    "id": f"suggestion_{user_id}_{int(time.time())}_{i}",
                    "text": suggestion_text,
                    "type": current_activity,
                    "time_relevant": time_of_day,
                    "confidence": self.calculate_confidence(suggestion_text, patterns),
                    "reasoning": self.generate_reasoning(suggestion_text, patterns, context),
                    "priority": self.calculate_priority(suggestion_text, patterns),
                    "personalized": self.is_personalized(suggestion_text, patterns)
                }
                suggestions.append(suggestion)
            
            # Sort by confidence and priority
            suggestions.sort(key=lambda x: (x["confidence"], x["priority"]), reverse=True)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")
            return []
    
    def calculate_confidence(self, suggestion_text: str, patterns: Dict[str, Any]) -> float:
        """Calculate confidence for suggestion"""
        try:
            confidence = 0.5  # Base confidence
            
            # Increase confidence based on patterns
            if patterns.get("common_activities"):
                if patterns["common_activities"] in suggestion_text.lower():
                    confidence += 0.2
            
            if patterns.get("preferred_times"):
                if patterns["preferred_times"] in suggestion_text.lower():
                    confidence += 0.1
            
            if patterns.get("suggestion_preferences"):
                for pref in patterns["suggestion_preferences"]:
                    if pref in suggestion_text.lower():
                        confidence += 0.15
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5
    
    def generate_reasoning(self, suggestion_text: str, patterns: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate reasoning for suggestion"""
        try:
            reasoning = []
            
            # Time-based reasoning
            current_hour = datetime.now().hour
            if 6 <= current_hour < 12:
                reasoning.append("Rano - czas na planowanie dnia")
            elif 12 <= current_hour < 18:
                reasoning.append("Popołudnie - czas na realizację zadań")
            else:
                reasoning.append("Wieczór - czas na podsumowanie")
            
            # Pattern-based reasoning
            if patterns.get("common_activities"):
                reasoning.append(f"Bazuje na Twoich częstych aktywnościach: {patterns['common_activities']}")
            
            if patterns.get("suggestion_preferences"):
                reasoning.append("Dostosowane do Twoich preferencji")
            
            # Context-based reasoning
            if context.get("work_mode"):
                reasoning.append("Tryb pracy - sugestie zawodowe")
            elif context.get("personal_mode"):
                reasoning.append("Tryb osobisty - sugestie prywatne")
            
            return reasoning
            
        except Exception as e:
            logger.error(f"Reasoning generation failed: {e}")
            return ["Sugestia na podstawie analizy wzorców"]
    
    def calculate_priority(self, suggestion_text: str, patterns: Dict[str, Any]) -> int:
        """Calculate priority for suggestion (1-5, 5 being highest)"""
        try:
            priority = 3  # Base priority
            
            # High priority keywords
            high_priority_keywords = ["ważne", "pilne", "krytyczne", "deadline", "termin"]
            if any(keyword in suggestion_text.lower() for keyword in high_priority_keywords):
                priority = 5
            
            # Medium priority keywords
            medium_priority_keywords = ["sprawdź", "zaplanuj", "przygotuj", "zrób"]
            if any(keyword in suggestion_text.lower() for keyword in medium_priority_keywords):
                priority = 4
            
            # Low priority keywords
            low_priority_keywords = ["może", "rozważ", "sprawdź", "opcjonalnie"]
            if any(keyword in suggestion_text.lower() for keyword in low_priority_keywords):
                priority = 2
            
            return priority
            
        except Exception as e:
            logger.error(f"Priority calculation failed: {e}")
            return 3
    
    def is_personalized(self, suggestion_text: str, patterns: Dict[str, Any]) -> bool:
        """Check if suggestion is personalized"""
        try:
            # Check if suggestion matches user patterns
            if patterns.get("common_activities"):
                if patterns["common_activities"] in suggestion_text.lower():
                    return True
            
            if patterns.get("suggestion_preferences"):
                for pref in patterns["suggestion_preferences"]:
                    if pref in suggestion_text.lower():
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Personalization check failed: {e}")
            return False
    
    def store_suggestion(self, user_id: str, suggestion: Dict[str, Any], context: Dict[str, Any]):
        """Store suggestion in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO suggestions 
                (user_id, suggestion_type, suggestion_data, context, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                suggestion["type"],
                json.dumps(suggestion),
                json.dumps(context),
                suggestion["confidence"]
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Suggestion storage failed: {e}")
    
    def record_feedback(self, user_id: str, suggestion_id: str, feedback: str, context: Dict[str, Any] = None):
        """Record user feedback on suggestion"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE suggestions 
                SET feedback = ?
                WHERE user_id = ? AND suggestion_data LIKE ?
            ''', (feedback, user_id, f'%{suggestion_id}%'))
            
            conn.commit()
            conn.close()
            
            # Update user patterns based on feedback
            self.update_user_patterns(user_id, suggestion_id, feedback)
            
        except Exception as e:
            logger.error(f"Feedback recording failed: {e}")
    
    def update_user_patterns(self, user_id: str, suggestion_id: str, feedback: str):
        """Update user patterns based on feedback"""
        try:
            if user_id not in self.user_patterns:
                self.user_patterns[user_id] = {
                    "accepted_suggestions": [],
                    "rejected_suggestions": [],
                    "preferred_types": [],
                    "feedback_history": []
                }
            
            patterns = self.user_patterns[user_id]
            patterns["feedback_history"].append({
                "suggestion_id": suggestion_id,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            })
            
            if feedback == "accepted":
                patterns["accepted_suggestions"].append(suggestion_id)
            elif feedback == "rejected":
                patterns["rejected_suggestions"].append(suggestion_id)
            
            # Store updated patterns
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_patterns (user_id, patterns, last_updated)
                VALUES (?, ?, ?)
            ''', (user_id, json.dumps(patterns), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Pattern update failed: {e}")

# Initialize suggestions system
suggestions_system = ProactiveSuggestions()

# API Endpoints
@app.post("/api/suggestions/generate", response_model=SuggestionResponse)
async def generate_suggestions(request: SuggestionRequest):
    """Generate proactive suggestions for user"""
    try:
        # Generate suggestions
        suggestions = suggestions_system.generate_suggestions(
            request.user_id,
            request.context,
            request.current_activity,
            request.time_of_day
        )
        
        # Store suggestions
        for suggestion in suggestions:
            suggestions_system.store_suggestion(request.user_id, suggestion, request.context)
        
        # Calculate overall confidence
        overall_confidence = sum(s["confidence"] for s in suggestions) / len(suggestions) if suggestions else 0.0
        
        # Generate reasoning
        reasoning = []
        if suggestions:
            reasoning.extend(suggestions[0]["reasoning"])
        
        # Check if personalized
        personalized = any(s["personalized"] for s in suggestions)
        
        return SuggestionResponse(
            suggestions=suggestions,
            confidence=overall_confidence,
            reasoning=reasoning,
            personalized=personalized,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Suggestion generation failed: {e}")
        raise HTTPException(status_code=500, detail="Suggestion generation failed")

@app.post("/api/suggestions/feedback")
async def record_feedback(feedback: SuggestionFeedback):
    """Record user feedback on suggestion"""
    try:
        suggestions_system.record_feedback(
            feedback.user_id,
            feedback.suggestion_id,
            feedback.feedback,
            feedback.context
        )
        
        return {
            "status": "success",
            "message": "Feedback recorded",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Feedback recording failed: {e}")
        raise HTTPException(status_code=500, detail="Feedback recording failed")

@app.get("/api/suggestions/patterns/{user_id}")
async def get_user_patterns(user_id: str):
    """Get user suggestion patterns"""
    try:
        patterns = suggestions_system.analyze_user_patterns(user_id, {})
        
        return {
            "user_id": user_id,
            "patterns": patterns,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Pattern retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Pattern retrieval failed")

@app.get("/api/suggestions/health")
async def suggestions_health():
    """Health check for suggestions service"""
    return {
        "status": "healthy",
        "service": "proactive_suggestions",
        "version": "1.0.0",
        "templates_loaded": len(suggestions_system.suggestion_templates),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run("proactive_suggestions:app", host="0.0.0.0", port=8003, reload=True)