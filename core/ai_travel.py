#!/usr/bin/env python3
"""
AI Travel Manager
Planowanie podróży, analiza preferencji, rekomendacje
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class AITravelManager:
    """Manager for AI travel planning and recommendations"""
    
    def __init__(self):
        self.travel_data = {}
        self.destinations_db = {}
        self.activities_db = {}
        self.accommodations_db = {}
        
    async def initialize(self):
        """Initialize the AI travel manager"""
        try:
            logger.info("Initializing AI Travel Manager...")
            
            # Initialize travel databases
            await self._initialize_travel_databases()
            
            logger.info("AI Travel Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Travel Manager: {e}")
            raise
    
    async def plan_travel(self, destination: str, budget: float, duration_days: int,
                         preferences: Dict[str, Any], travel_style: str = "balanced",
                         user_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate personalized travel plan"""
        try:
            # Analyze destination
            destination_info = await self._analyze_destination(destination)
            
            # Generate itinerary
            itinerary = await self._generate_itinerary(
                destination, duration_days, preferences, travel_style
            )
            
            # Calculate budget breakdown
            budget_breakdown = await self._calculate_budget_breakdown(
                destination, budget, duration_days, preferences
            )
            
            # Generate recommendations
            recommendations = await self._generate_travel_recommendations(
                destination, preferences, travel_style
            )
            
            # Store travel plan
            await self._store_travel_plan(user_id, destination, itinerary, budget_breakdown)
            
            return {
                "plan": {
                    "destination": destination_info,
                    "itinerary": itinerary,
                    "duration_days": duration_days,
                    "travel_style": travel_style
                },
                "budget_breakdown": budget_breakdown,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Travel planning failed: {e}")
            raise
    
    async def _initialize_travel_databases(self):
        """Initialize travel databases with sample data"""
        try:
            # Sample destinations
            self.destinations_db = {
                "warszawa": {
                    "name": "Warszawa",
                    "country": "Polska",
                    "climate": "umiarkowany",
                    "currency": "PLN",
                    "language": "polski",
                    "attractions": ["Stare Miasto", "Łazienki Królewskie", "Pałac Kultury"],
                    "best_time": "maj-wrzesień",
                    "cost_level": "średni"
                },
                "kraków": {
                    "name": "Kraków",
                    "country": "Polska",
                    "climate": "umiarkowany",
                    "currency": "PLN",
                    "language": "polski",
                    "attractions": ["Rynek Główny", "Wawel", "Kazimierz"],
                    "best_time": "maj-wrzesień",
                    "cost_level": "średni"
                },
                "paryż": {
                    "name": "Paryż",
                    "country": "Francja",
                    "climate": "umiarkowany",
                    "currency": "EUR",
                    "language": "francuski",
                    "attractions": ["Wieża Eiffla", "Luwr", "Notre-Dame"],
                    "best_time": "kwiecień-czerwiec",
                    "cost_level": "wysoki"
                }
            }
            
            # Sample activities
            self.activities_db = {
                "kulturalne": ["muzea", "teatry", "galerie", "zabytki"],
                "aktywne": ["hiking", "rower", "pływanie", "wspinaczka"],
                "relaks": ["spa", "plaża", "parki", "ogrody"],
                "kulinarne": ["restauracje", "degustacje", "kuchnia lokalna"],
                "rozrywka": ["kino", "koncerty", "kluby", "bary"]
            }
            
            # Sample accommodations
            self.accommodations_db = {
                "budżetowe": {"price_range": (50, 150), "types": ["hostel", "pensjonat"]},
                "średnie": {"price_range": (150, 300), "types": ["hotel", "apartament"]},
                "luksusowe": {"price_range": (300, 1000), "types": ["hotel 5*", "villa"]}
            }
            
        except Exception as e:
            logger.error(f"Travel databases initialization failed: {e}")
    
    async def _analyze_destination(self, destination: str) -> Dict[str, Any]:
        """Analyze destination for travel planning"""
        try:
            destination_lower = destination.lower()
            
            # Find matching destination
            for key, info in self.destinations_db.items():
                if key in destination_lower or info["name"].lower() in destination_lower:
                    return info
            
            # Default destination info
            return {
                "name": destination,
                "country": "Nieznane",
                "climate": "umiarkowany",
                "currency": "EUR",
                "language": "lokalny",
                "attractions": ["Atrakcje turystyczne"],
                "best_time": "cały rok",
                "cost_level": "średni"
            }
            
        except Exception as e:
            logger.error(f"Destination analysis failed: {e}")
            return {}
    
    async def _generate_itinerary(self, destination: str, duration_days: int,
                                preferences: Dict[str, Any], travel_style: str) -> List[Dict[str, Any]]:
        """Generate daily itinerary"""
        try:
            itinerary = []
            
            for day in range(1, duration_days + 1):
                day_plan = {
                    "day": day,
                    "date": (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d"),
                    "activities": [],
                    "meals": [],
                    "accommodation": None
                }
                
                # Add activities based on preferences
                if "interests" in preferences:
                    for interest in preferences["interests"][:2]:  # Max 2 per day
                        if interest in self.activities_db:
                            activities = self.activities_db[interest]
                            day_plan["activities"].append({
                                "type": interest,
                                "activity": activities[0],
                                "time": "10:00-12:00",
                                "location": f"W {destination}"
                            })
                
                # Add meals
                day_plan["meals"] = [
                    {"type": "śniadanie", "time": "08:00", "suggestion": "Lokalna kawiarnia"},
                    {"type": "obiad", "time": "13:00", "suggestion": "Restauracja z lokalną kuchnią"},
                    {"type": "kolacja", "time": "19:00", "suggestion": "Elegancka restauracja"}
                ]
                
                # Add accommodation
                day_plan["accommodation"] = {
                    "type": "hotel",
                    "location": f"Centrum {destination}",
                    "check_in": "15:00",
                    "check_out": "11:00"
                }
                
                itinerary.append(day_plan)
            
            return itinerary
            
        except Exception as e:
            logger.error(f"Itinerary generation failed: {e}")
            return []
    
    async def _calculate_budget_breakdown(self, destination: str, budget: float,
                                        duration_days: int, preferences: Dict[str, Any]) -> Dict[str, float]:
        """Calculate budget breakdown for travel"""
        try:
            breakdown = {
                "accommodation": 0.0,
                "food": 0.0,
                "transport": 0.0,
                "activities": 0.0,
                "shopping": 0.0,
                "miscellaneous": 0.0
            }
            
            # Accommodation (40% of budget)
            breakdown["accommodation"] = budget * 0.4
            
            # Food (25% of budget)
            breakdown["food"] = budget * 0.25
            
            # Transport (20% of budget)
            breakdown["transport"] = budget * 0.2
            
            # Activities (10% of budget)
            breakdown["activities"] = budget * 0.1
            
            # Shopping (3% of budget)
            breakdown["shopping"] = budget * 0.03
            
            # Miscellaneous (2% of budget)
            breakdown["miscellaneous"] = budget * 0.02
            
            # Add daily breakdown
            breakdown["daily_budget"] = budget / duration_days
            breakdown["total_budget"] = budget
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Budget breakdown calculation failed: {e}")
            return {}
    
    async def _generate_travel_recommendations(self, destination: str, preferences: Dict[str, Any],
                                            travel_style: str) -> List[str]:
        """Generate travel recommendations"""
        try:
            recommendations = []
            
            # General recommendations
            recommendations.extend([
                f"Sprawdź pogodę w {destination} przed wyjazdem",
                "Zabierz ze sobą dokumenty i ubezpieczenie podróżne",
                "Poinformuj bank o planowanej podróży"
            ])
            
            # Style-based recommendations
            if travel_style == "budżetowy":
                recommendations.extend([
                    "Rozważ zakwaterowanie w hostelu lub pensjonacie",
                    "Jedz w lokalnych restauracjach zamiast turystycznych",
                    "Używaj transportu publicznego"
                ])
            elif travel_style == "luksusowy":
                recommendations.extend([
                    "Zarezerwuj stolik w eleganckich restauracjach",
                    "Rozważ prywatnego przewodnika",
                    "Sprawdź opcje spa i wellness"
                ])
            else:  # balanced
                recommendations.extend([
                    "Połącz zwiedzanie z relaksem",
                    "Spróbuj lokalnej kuchni",
                    "Zostaw czas na spontaniczne odkrycia"
                ])
            
            # Preference-based recommendations
            if "interests" in preferences:
                if "kulturalne" in preferences["interests"]:
                    recommendations.append("Sprawdź godziny otwarcia muzeów i galerii")
                if "aktywne" in preferences["interests"]:
                    recommendations.append("Zabierz odpowiedni sprzęt sportowy")
                if "kulinarne" in preferences["interests"]:
                    recommendations.append("Zarezerwuj stoliki w najlepszych restauracjach")
            
            return recommendations[:8]  # Limit to 8 recommendations
            
        except Exception as e:
            logger.error(f"Travel recommendations generation failed: {e}")
            return []
    
    async def _store_travel_plan(self, user_id: Optional[str], destination: str,
                               itinerary: List[Dict[str, Any]], budget_breakdown: Dict[str, float]):
        """Store travel plan for future reference"""
        try:
            travel_plan = {
                "user_id": user_id,
                "destination": destination,
                "itinerary": itinerary,
                "budget_breakdown": budget_breakdown,
                "created_at": datetime.now().isoformat()
            }
            
            if user_id:
                if user_id not in self.travel_data:
                    self.travel_data[user_id] = []
                
                self.travel_data[user_id].append(travel_plan)
                
                # Keep only last 10 plans per user
                if len(self.travel_data[user_id]) > 10:
                    self.travel_data[user_id] = self.travel_data[user_id][-10:]
            
            logger.info(f"Travel plan stored for user {user_id}")
            
        except Exception as e:
            logger.error(f"Travel plan storage failed: {e}")
    
    async def cleanup(self):
        """Cleanup AI travel manager"""
        try:
            logger.info("AI Travel Manager cleaned up successfully")
        except Exception as e:
            logger.error(f"AI Travel Manager cleanup failed: {e}")