#!/usr/bin/env python3
"""
AI Mood Manager
Wykrywanie nastroju użytkownika, analiza emocji, sugestie
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import openai

logger = logging.getLogger(__name__)

class AIMoodManager:
    """Manager for AI mood detection and emotion analysis"""
    
    def __init__(self):
        self.openai_client = None
        self.mood_history = {}
        self.emotion_models = {
            "primary": ["szczęście", "smutek", "złość", "strach", "zaskoczenie", "wstręt", "neutralny"],
            "secondary": ["niepokój", "ekscytacja", "frustracja", "spokój", "irytacja", "radość", "zmęczenie"]
        }
        
    async def initialize(self):
        """Initialize the AI mood manager"""
        try:
            logger.info("Initializing AI Mood Manager...")
            
            # Initialize OpenAI client
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            self.openai_client = openai.AsyncOpenAI(api_key=api_key)
            
            logger.info("AI Mood Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Mood Manager: {e}")
            raise
    
    async def detect_mood(self, text: str, context: Optional[str] = None, 
                         user_id: Optional[str] = None) -> Dict[str, Any]:
        """Detect user mood from text"""
        try:
            # Analyze text for mood indicators
            mood_analysis = await self._analyze_text_mood(text, context)
            
            # Detect emotions
            emotions = await self._detect_emotions(text, mood_analysis)
            
            # Generate suggestions
            suggestions = await self._generate_mood_suggestions(mood_analysis, emotions)
            
            # Store mood data
            await self._store_mood_data(user_id, text, mood_analysis, emotions)
            
            return {
                "mood": mood_analysis["primary_mood"],
                "confidence": mood_analysis["confidence"],
                "emotions": emotions,
                "suggestions": suggestions,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mood detection failed: {e}")
            raise
    
    async def _analyze_text_mood(self, text: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Analyze text for mood indicators"""
        try:
            # Mood indicators (simplified)
            positive_words = ["dobry", "świetny", "wspaniały", "super", "fajny", "miły", "piękny", "wesoły"]
            negative_words = ["zły", "gorszy", "okropny", "brzydki", "smutny", "zły", "frustrujący", "irytujący"]
            neutral_words = ["ok", "normalny", "standardowy", "typowy", "zwykły"]
            
            # Count mood indicators
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            neutral_count = sum(1 for word in neutral_words if word in text_lower)
            
            # Determine primary mood
            total_indicators = positive_count + negative_count + neutral_count
            if total_indicators == 0:
                primary_mood = "neutralny"
                confidence = 0.5
            elif positive_count > negative_count and positive_count > neutral_count:
                primary_mood = "pozytywny"
                confidence = min(positive_count / total_indicators, 1.0)
            elif negative_count > positive_count and negative_count > neutral_count:
                primary_mood = "negatywny"
                confidence = min(negative_count / total_indicators, 1.0)
            else:
                primary_mood = "neutralny"
                confidence = min(neutral_count / total_indicators, 1.0)
            
            # Context analysis
            context_boost = 0.0
            if context:
                if "praca" in context.lower() or "zawód" in context.lower():
                    context_boost = 0.1
                elif "dom" in context.lower() or "rodzina" in context.lower():
                    context_boost = 0.15
                elif "zdrowie" in context.lower() or "lekarz" in context.lower():
                    context_boost = 0.2
            
            confidence = min(confidence + context_boost, 1.0)
            
            return {
                "primary_mood": primary_mood,
                "confidence": confidence,
                "positive_indicators": positive_count,
                "negative_indicators": negative_count,
                "neutral_indicators": neutral_count,
                "context_boost": context_boost
            }
            
        except Exception as e:
            logger.error(f"Text mood analysis failed: {e}")
            return {"primary_mood": "neutralny", "confidence": 0.5}
    
    async def _detect_emotions(self, text: str, mood_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Detect specific emotions in text"""
        try:
            emotions = {}
            
            # Emotion keywords
            emotion_keywords = {
                "szczęście": ["szczęśliwy", "radość", "wesoły", "uśmiech", "śmiech"],
                "smutek": ["smutny", "żal", "płacz", "depresja", "przygnębienie"],
                "złość": ["zły", "wściekły", "irytacja", "frustracja", "wkurzony"],
                "strach": ["strach", "lęk", "niepokój", "panika", "przerażenie"],
                "zaskoczenie": ["zaskoczony", "niespodzianka", "wow", "ojej", "nie wierzę"],
                "wstręt": ["obrzydliwy", "wstrętny", "ohydny", "brzydki", "paskudny"],
                "ekscytacja": ["ekscytacja", "podniecenie", "entuzjazm", "emocje", "adrenalina"],
                "spokój": ["spokojny", "zrelaksowany", "odprężony", "cisza", "harmonia"],
                "zmęczenie": ["zmęczony", "wyczerpany", "senny", "słaby", "bez energii"]
            }
            
            text_lower = text.lower()
            
            for emotion, keywords in emotion_keywords.items():
                count = sum(1 for keyword in keywords if keyword in text_lower)
                if count > 0:
                    emotions[emotion] = min(count / len(keywords), 1.0)
                else:
                    emotions[emotion] = 0.0
            
            # Normalize emotions
            total_emotion_score = sum(emotions.values())
            if total_emotion_score > 0:
                for emotion in emotions:
                    emotions[emotion] = emotions[emotion] / total_emotion_score
            
            return emotions
            
        except Exception as e:
            logger.error(f"Emotion detection failed: {e}")
            return {}
    
    async def _generate_mood_suggestions(self, mood_analysis: Dict[str, Any], 
                                       emotions: Dict[str, float]) -> List[str]:
        """Generate suggestions based on mood and emotions"""
        try:
            suggestions = []
            primary_mood = mood_analysis["primary_mood"]
            confidence = mood_analysis["confidence"]
            
            # Mood-based suggestions
            if primary_mood == "pozytywny":
                suggestions.extend([
                    "Świetnie! Kontynuuj to, co robisz",
                    "Możesz podzielić się tym pozytywnym nastawieniem z innymi",
                    "Rozważ zapisanie tego momentu w dzienniku"
                ])
            elif primary_mood == "negatywny":
                suggestions.extend([
                    "Rozważ głębokie oddychanie lub krótką przerwę",
                    "Możesz porozmawiać z kimś bliskim o swoich uczuciach",
                    "Spróbuj zrobić coś, co sprawia Ci przyjemność"
                ])
            else:  # neutralny
                suggestions.extend([
                    "Możesz spróbować czegoś nowego",
                    "Rozważ refleksję nad swoimi celami",
                    "Sprawdź, czy nie potrzebujesz odpoczynku"
                ])
            
            # Emotion-specific suggestions
            if emotions.get("strach", 0) > 0.3:
                suggestions.append("Jeśli czujesz lęk, rozważ techniki relaksacyjne")
            
            if emotions.get("złość", 0) > 0.3:
                suggestions.append("Gdy czujesz złość, spróbuj liczyć do dziesięciu")
            
            if emotions.get("smutek", 0) > 0.3:
                suggestions.append("W przypadku smutku, pamiętaj, że to uczucie jest tymczasowe")
            
            if emotions.get("zmęczenie", 0) > 0.3:
                suggestions.append("Jeśli jesteś zmęczony, rozważ krótką drzemkę")
            
            # Confidence-based suggestions
            if confidence < 0.3:
                suggestions.append("Twoje emocje mogą być złożone - to normalne")
            
            return suggestions[:5]  # Limit to 5 suggestions
            
        except Exception as e:
            logger.error(f"Mood suggestions generation failed: {e}")
            return []
    
    async def _store_mood_data(self, user_id: Optional[str], text: str, 
                             mood_analysis: Dict[str, Any], emotions: Dict[str, float]):
        """Store mood data for tracking"""
        try:
            mood_data = {
                "user_id": user_id,
                "text": text,
                "mood_analysis": mood_analysis,
                "emotions": emotions,
                "timestamp": datetime.now().isoformat()
            }
            
            if user_id:
                if user_id not in self.mood_history:
                    self.mood_history[user_id] = []
                
                self.mood_history[user_id].append(mood_data)
                
                # Keep only last 100 entries per user
                if len(self.mood_history[user_id]) > 100:
                    self.mood_history[user_id] = self.mood_history[user_id][-100:]
            
            logger.info(f"Mood data stored for user {user_id}")
            
        except Exception as e:
            logger.error(f"Mood data storage failed: {e}")
    
    async def get_mood_history(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get mood history for user"""
        try:
            if user_id not in self.mood_history:
                return []
            
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_moods = []
            
            for mood_data in self.mood_history[user_id]:
                mood_date = datetime.fromisoformat(mood_data["timestamp"])
                if mood_date >= cutoff_date:
                    recent_moods.append(mood_data)
            
            return recent_moods
            
        except Exception as e:
            logger.error(f"Get mood history failed: {e}")
            return []
    
    async def cleanup(self):
        """Cleanup AI mood manager"""
        try:
            logger.info("AI Mood Manager cleaned up successfully")
        except Exception as e:
            logger.error(f"AI Mood Manager cleanup failed: {e}")