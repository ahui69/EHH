#!/usr/bin/env python3
"""
Psyche Endpoint - Advanced Psychological Analysis
Zaawansowana analiza psychologiczna użytkownika
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Psyche Analysis", description="Advanced Psychological Analysis System", version="1.0.0")

# Add CORS middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Pydantic models
class PsycheAnalysisRequest(BaseModel):
    text: str
    context: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class PsycheAnalysisResponse(BaseModel):
    personality_traits: Dict[str, float]
    emotional_state: Dict[str, float]
    cognitive_patterns: Dict[str, Any]
    psychological_insights: List[str]
    recommendations: List[str]
    confidence: float
    timestamp: str

class PsycheProfileRequest(BaseModel):
    user_id: str
    analysis_data: List[Dict[str, Any]]

class PsycheProfileResponse(BaseModel):
    profile: Dict[str, Any]
    evolution: List[Dict[str, Any]]
    insights: List[str]
    timestamp: str

class PsycheTherapyRequest(BaseModel):
    user_id: str
    issue: str
    context: Optional[str] = None

class PsycheTherapyResponse(BaseModel):
    therapy_approach: str
    techniques: List[str]
    exercises: List[str]
    timeline: str
    progress_tracking: Dict[str, Any]
    timestamp: str

# Psychological analysis functions
class PsycheAnalyzer:
    def __init__(self):
        self.personality_models = {
            "big_five": ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"],
            "mbti": ["introversion", "extroversion", "sensing", "intuition", "thinking", "feeling", "judging", "perceiving"],
            "emotional_intelligence": ["self_awareness", "self_regulation", "motivation", "empathy", "social_skills"]
        }
        
        self.emotional_indicators = {
            "joy": ["szczęśliwy", "wesoły", "radość", "świetnie", "super", "fajnie"],
            "sadness": ["smutny", "żal", "depresja", "przygnębiony", "smutek"],
            "anger": ["zły", "wściekły", "irytacja", "frustracja", "wkurzony"],
            "fear": ["strach", "lęk", "niepokój", "panika", "przerażenie"],
            "surprise": ["zaskoczony", "niespodzianka", "wow", "ojej"],
            "disgust": ["obrzydliwy", "wstrętny", "ohydny", "paskudny"],
            "love": ["kocham", "miłość", "kochany", "ukochany", "kochanie"],
            "hate": ["nienawidzę", "nienawiść", "wstręt", "obrzydzenie"]
        }
        
        self.cognitive_patterns = {
            "analytical": ["analiza", "logika", "rozumowanie", "systematyczny"],
            "creative": ["kreatywny", "twórczy", "pomysłowy", "innowacyjny"],
            "practical": ["praktyczny", "realistyczny", "konkretny", "wykonalny"],
            "intuitive": ["intuicja", "przeczucie", "instynkt", "wyczucie"]
        }

    async def analyze_personality(self, text: str, context: Optional[str] = None) -> Dict[str, float]:
        """Analyze personality traits from text"""
        try:
            traits = {}
            text_lower = text.lower()
            
            # Big Five analysis
            for trait in self.personality_models["big_five"]:
                score = 0.5  # Base score
                
                # Analyze based on keywords and patterns
                if trait == "openness":
                    open_keywords = ["nowy", "ciekawy", "eksperyment", "kreatywny", "oryginalny"]
                    score += sum(0.1 for word in open_keywords if word in text_lower)
                elif trait == "conscientiousness":
                    cons_keywords = ["plan", "organizacja", "dyscyplina", "odpowiedzialny", "systematyczny"]
                    score += sum(0.1 for word in cons_keywords if word in text_lower)
                elif trait == "extraversion":
                    extra_keywords = ["ludzie", "spotkanie", "towarzystwo", "socjalny", "energiczny"]
                    score += sum(0.1 for word in extra_keywords if word in text_lower)
                elif trait == "agreeableness":
                    agree_keywords = ["pomoc", "współpraca", "zrozumienie", "empatia", "życzliwy"]
                    score += sum(0.1 for word in agree_keywords if word in text_lower)
                elif trait == "neuroticism":
                    neuro_keywords = ["stres", "niepokój", "zmartwiony", "napięty", "nerwowy"]
                    score += sum(0.1 for word in neuro_keywords if word in text_lower)
                
                traits[trait] = min(score, 1.0)
            
            return traits
            
        except Exception as e:
            logger.error(f"Personality analysis failed: {e}")
            return {trait: 0.5 for trait in self.personality_models["big_five"]}

    async def analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotional state from text"""
        try:
            emotions = {}
            text_lower = text.lower()
            
            for emotion, keywords in self.emotional_indicators.items():
                count = sum(1 for keyword in keywords if keyword in text_lower)
                emotions[emotion] = min(count / len(keywords), 1.0)
            
            # Normalize emotions
            total_emotion = sum(emotions.values())
            if total_emotion > 0:
                for emotion in emotions:
                    emotions[emotion] = emotions[emotion] / total_emotion
            
            return emotions
            
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return {emotion: 0.0 for emotion in self.emotional_indicators.keys()}

    async def analyze_cognitive_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze cognitive patterns from text"""
        try:
            patterns = {}
            text_lower = text.lower()
            
            for pattern, keywords in self.cognitive_patterns.items():
                count = sum(1 for keyword in keywords if keyword in text_lower)
                patterns[pattern] = {
                    "strength": min(count / len(keywords), 1.0),
                    "indicators": [kw for kw in keywords if kw in text_lower]
                }
            
            # Determine dominant pattern
            dominant = max(patterns.items(), key=lambda x: x[1]["strength"])
            patterns["dominant"] = dominant[0]
            
            return patterns
            
        except Exception as e:
            logger.error(f"Cognitive pattern analysis failed: {e}")
            return {}

    async def generate_insights(self, personality: Dict[str, float], emotions: Dict[str, float], 
                              cognitive: Dict[str, Any]) -> List[str]:
        """Generate psychological insights"""
        try:
            insights = []
            
            # Personality insights
            high_traits = [trait for trait, score in personality.items() if score > 0.7]
            if high_traits:
                insights.append(f"Wysokie cechy osobowości: {', '.join(high_traits)}")
            
            # Emotional insights
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])
            if dominant_emotion[1] > 0.3:
                insights.append(f"Dominująca emocja: {dominant_emotion[0]} ({dominant_emotion[1]:.1%})")
            
            # Cognitive insights
            if "dominant" in cognitive:
                insights.append(f"Dominujący wzorzec myślenia: {cognitive['dominant']}")
            
            # General insights
            if personality.get("neuroticism", 0) > 0.6:
                insights.append("Możliwe oznaki stresu lub niepokoju - rozważ techniki relaksacyjne")
            
            if personality.get("extraversion", 0) > 0.7:
                insights.append("Wysoka ekstrawersja - możesz czerpać energię z kontaktów społecznych")
            
            if personality.get("openness", 0) > 0.7:
                insights.append("Wysoka otwartość - jesteś skłonny do eksperymentów i nowych doświadczeń")
            
            return insights
            
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            return []

    async def generate_recommendations(self, personality: Dict[str, float], emotions: Dict[str, float],
                                     cognitive: Dict[str, Any]) -> List[str]:
        """Generate psychological recommendations"""
        try:
            recommendations = []
            
            # Stress management
            if personality.get("neuroticism", 0) > 0.6:
                recommendations.extend([
                    "Rozważ techniki mindfulness i medytację",
                    "Regularne ćwiczenia fizyczne mogą pomóc w redukcji stresu",
                    "Zadbaj o odpowiednią ilość snu i odpoczynku"
                ])
            
            # Social recommendations
            if personality.get("extraversion", 0) > 0.7:
                recommendations.append("Korzystaj z kontaktów społecznych - to Twoje źródło energii")
            elif personality.get("extraversion", 0) < 0.3:
                recommendations.append("Rozważ stopniowe zwiększanie kontaktów społecznych")
            
            # Creativity recommendations
            if personality.get("openness", 0) > 0.7:
                recommendations.append("Eksploruj nowe hobby i zainteresowania")
            
            # Emotional recommendations
            if emotions.get("sadness", 0) > 0.4:
                recommendations.extend([
                    "Rozważ rozmowę z bliską osobą lub specjalistą",
                    "Pamiętaj, że trudne emocje są tymczasowe"
                ])
            
            if emotions.get("anger", 0) > 0.4:
                recommendations.extend([
                    "Spróbuj technik głębokiego oddychania",
                    "Rozważ aktywność fizyczną jako sposób na rozładowanie napięcia"
                ])
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            logger.error(f"Recommendations generation failed: {e}")
            return []

# Initialize analyzer
psyche_analyzer = PsycheAnalyzer()

# API Endpoints
@app.post("/api/psyche/analyze", response_model=PsycheAnalysisResponse)
async def analyze_psyche(request: PsycheAnalysisRequest):
    """Analyze psychological state from text"""
    try:
        # Analyze personality
        personality = await psyche_analyzer.analyze_personality(request.text, request.context)
        
        # Analyze emotions
        emotions = await psyche_analyzer.analyze_emotions(request.text)
        
        # Analyze cognitive patterns
        cognitive = await psyche_analyzer.analyze_cognitive_patterns(request.text)
        
        # Generate insights
        insights = await psyche_analyzer.generate_insights(personality, emotions, cognitive)
        
        # Generate recommendations
        recommendations = await psyche_analyzer.generate_recommendations(personality, emotions, cognitive)
        
        # Calculate confidence
        confidence = min(
            (max(personality.values()) + max(emotions.values()) + len(insights) / 10),
            1.0
        )
        
        return PsycheAnalysisResponse(
            personality_traits=personality,
            emotional_state=emotions,
            cognitive_patterns=cognitive,
            psychological_insights=insights,
            recommendations=recommendations,
            confidence=confidence,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Psyche analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Psychological analysis failed")

@app.post("/api/psyche/profile", response_model=PsycheProfileResponse)
async def get_psyche_profile(request: PsycheProfileRequest):
    """Get comprehensive psychological profile"""
    try:
        # Analyze all data points
        all_personality = {}
        all_emotions = {}
        all_insights = []
        
        for data in request.analysis_data:
            if "personality" in data:
                for trait, score in data["personality"].items():
                    if trait not in all_personality:
                        all_personality[trait] = []
                    all_personality[trait].append(score)
            
            if "emotions" in data:
                for emotion, score in data["emotions"].items():
                    if emotion not in all_emotions:
                        all_emotions[emotion] = []
                    all_emotions[emotion].append(score)
            
            if "insights" in data:
                all_insights.extend(data["insights"])
        
        # Calculate averages
        avg_personality = {trait: sum(scores) / len(scores) for trait, scores in all_personality.items()}
        avg_emotions = {emotion: sum(scores) / len(scores) for emotion, scores in all_emotions.items()}
        
        # Generate profile
        profile = {
            "personality_profile": avg_personality,
            "emotional_profile": avg_emotions,
            "cognitive_style": "analytical",  # Simplified
            "psychological_type": "balanced",  # Simplified
            "strengths": [trait for trait, score in avg_personality.items() if score > 0.7],
            "areas_for_growth": [trait for trait, score in avg_personality.items() if score < 0.3]
        }
        
        # Generate evolution insights
        evolution = []
        if len(request.analysis_data) > 1:
            evolution.append({
                "period": "recent",
                "changes": "Stabilny rozwój psychologiczny",
                "trends": "Pozytywne zmiany w samopoczuciu"
            })
        
        return PsycheProfileResponse(
            profile=profile,
            evolution=evolution,
            insights=all_insights[:10],  # Top 10 insights
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Psyche profile generation failed: {e}")
        raise HTTPException(status_code=500, detail="Profile generation failed")

@app.post("/api/psyche/therapy", response_model=PsycheTherapyResponse)
async def get_therapy_recommendations(request: PsycheTherapyRequest):
    """Get therapy recommendations based on psychological analysis"""
    try:
        # Analyze the issue
        issue_lower = request.issue.lower()
        
        # Determine therapy approach
        if "stres" in issue_lower or "niepokój" in issue_lower:
            approach = "Cognitive Behavioral Therapy (CBT)"
            techniques = ["Mindfulness", "Deep Breathing", "Progressive Muscle Relaxation"]
            exercises = ["5-4-3-2-1 Grounding", "Box Breathing", "Body Scan Meditation"]
        elif "depresja" in issue_lower or "smutek" in issue_lower:
            approach = "Behavioral Activation"
            techniques = ["Activity Scheduling", "Graded Task Assignment", "Pleasant Event Scheduling"]
            exercises = ["Daily Mood Tracking", "Gratitude Journal", "Social Connection"]
        elif "gniew" in issue_lower or "złość" in issue_lower:
            approach = "Anger Management"
            techniques = ["Cognitive Restructuring", "Relaxation Training", "Communication Skills"]
            exercises = ["Anger Log", "Time-out Technique", "Assertive Communication"]
        else:
            approach = "General Counseling"
            techniques = ["Active Listening", "Reflective Questioning", "Goal Setting"]
            exercises = ["Self-reflection", "Journaling", "Mindfulness Practice"]
        
        # Generate timeline
        timeline = "4-6 tygodni regularnej pracy"
        
        # Progress tracking
        progress_tracking = {
            "weekly_sessions": 1,
            "homework_exercises": 3,
            "progress_metrics": ["mood", "stress_level", "coping_skills"],
            "milestones": ["Week 1: Assessment", "Week 2: Skill Building", "Week 4: Integration"]
        }
        
        return PsycheTherapyResponse(
            therapy_approach=approach,
            techniques=techniques,
            exercises=exercises,
            timeline=timeline,
            progress_tracking=progress_tracking,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Therapy recommendations failed: {e}")
        raise HTTPException(status_code=500, detail="Therapy recommendations failed")

@app.get("/api/psyche/health")
async def psyche_health():
    """Health check for psyche service"""
    return {
        "status": "healthy",
        "service": "psyche_analysis",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run("psyche_endpoint:app", host="0.0.0.0", port=8001, reload=True)