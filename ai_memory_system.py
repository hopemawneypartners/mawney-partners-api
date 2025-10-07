#!/usr/bin/env python3
"""
AI Memory System for Mawney Partners
Stores and learns from user interactions to improve responses over time
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)

class AIMemorySystem:
    def __init__(self, memory_file: str = "ai_memory.json"):
        self.memory_file = memory_file
        self.memory = self._load_memory()
        
    def _load_memory(self) -> Dict:
        """Load existing memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    memory = json.load(f)
                    # Ensure all required keys exist
                    return self._ensure_memory_structure(memory)
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
        
        # Return default memory structure
        return self._get_default_memory()
    
    def _ensure_memory_structure(self, memory: Dict) -> Dict:
        """Ensure memory has all required keys"""
        default_memory = self._get_default_memory()
        
        # Add missing keys with default values
        for key, default_value in default_memory.items():
            if key not in memory:
                memory[key] = default_value
                logger.info(f"Added missing key '{key}' to memory")
        
        return memory
    
    def _get_default_memory(self) -> Dict:
        """Get default memory structure"""
        return {
            "user_preferences": {},
            "conversation_history": [],
            "learned_patterns": {},
            "custom_responses": {},
            "user_feedback": [],
            "chat_sessions": {
                "default": {
                    "name": "General Chat",
                    "topic": "general",
                    "created_at": datetime.now().isoformat(),
                    "last_used": datetime.now().isoformat(),
                    "conversations": []
                }
            },
            "current_chat_id": "default",
            "shared_knowledge": {
                "user_info": {},
                "preferences": {},
                "learned_facts": {},
                "interests": []
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            self.memory["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
            logger.info("💾 Memory saved successfully")
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def store_conversation(self, user_query: str, ai_response: str, response_type: str, confidence: float, chat_id: str = None):
        """Store a conversation interaction in specific chat session"""
        if chat_id is None:
            chat_id = self.memory.get("current_chat_id", "default")
        
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "ai_response": ai_response,
            "response_type": response_type,
            "confidence": confidence,
            "user_feedback": None  # Will be updated if user provides feedback
        }
        
        # Store in specific chat session
        if chat_id not in self.memory["chat_sessions"]:
            self.create_chat_session(chat_id, f"Chat {len(self.memory['chat_sessions']) + 1}")
        
        self.memory["chat_sessions"][chat_id]["conversations"].append(conversation)
        self.memory["chat_sessions"][chat_id]["last_used"] = datetime.now().isoformat()
        
        # Also store in global conversation history
        self.memory["conversation_history"].append(conversation)
        
        # Update shared knowledge
        self._update_shared_knowledge(user_query, ai_response)
        
        # Keep only last 100 conversations per chat to prevent memory bloat
        if len(self.memory["chat_sessions"][chat_id]["conversations"]) > 100:
            self.memory["chat_sessions"][chat_id]["conversations"] = self.memory["chat_sessions"][chat_id]["conversations"][-100:]
        
        # Keep only last 200 global conversations
        if len(self.memory["conversation_history"]) > 200:
            self.memory["conversation_history"] = self.memory["conversation_history"][-200:]
        
        self._save_memory()
        logger.info(f"💬 Conversation stored in chat {chat_id}: {response_type}")
    
    def create_chat_session(self, chat_id: str, name: str, topic: str = "general"):
        """Create a new chat session"""
        self.memory["chat_sessions"][chat_id] = {
            "name": name,
            "topic": topic,
            "created_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
            "conversations": []
        }
        self._save_memory()
        logger.info(f"💬 Created new chat session: {name} ({chat_id})")
    
    def get_chat_sessions(self) -> Dict:
        """Get all chat sessions"""
        return self.memory["chat_sessions"]
    
    def get_current_chat_id(self) -> str:
        """Get current active chat ID"""
        return self.memory.get("current_chat_id", "default")
    
    def set_current_chat(self, chat_id: str):
        """Set current active chat"""
        if chat_id in self.memory["chat_sessions"]:
            self.memory["current_chat_id"] = chat_id
            self.memory["chat_sessions"][chat_id]["last_used"] = datetime.now().isoformat()
            self._save_memory()
            logger.info(f"💬 Switched to chat: {chat_id}")
    
    def get_chat_conversations(self, chat_id: str = None) -> List[Dict]:
        """Get conversations for specific chat"""
        if chat_id is None:
            chat_id = self.get_current_chat_id()
        
        if chat_id in self.memory["chat_sessions"]:
            return self.memory["chat_sessions"][chat_id]["conversations"]
        return []
    
    def delete_chat_session(self, chat_id: str):
        """Delete a chat session (cannot delete default)"""
        if chat_id != "default" and chat_id in self.memory["chat_sessions"]:
            del self.memory["chat_sessions"][chat_id]
            
            # If we deleted the current chat, switch to default
            if self.memory.get("current_chat_id") == chat_id:
                self.memory["current_chat_id"] = "default"
            
            self._save_memory()
            logger.info(f"💬 Deleted chat session: {chat_id}")
    
    def rename_chat_session(self, chat_id: str, new_name: str):
        """Rename a chat session"""
        if chat_id in self.memory["chat_sessions"]:
            self.memory["chat_sessions"][chat_id]["name"] = new_name
            self._save_memory()
            logger.info(f"💬 Renamed chat {chat_id} to: {new_name}")
    
    def _update_shared_knowledge(self, user_query: str, ai_response: str):
        """Update shared knowledge that applies across all chats"""
        # Extract user information
        if "my name is" in user_query.lower():
            name = user_query.lower().split("my name is")[-1].strip()
            self.memory["shared_knowledge"]["user_info"]["name"] = name
        
        # Extract preferences
        if "i prefer" in user_query.lower() or "i like" in user_query.lower():
            preference = user_query.lower()
            if "preferences" not in self.memory["shared_knowledge"]:
                self.memory["shared_knowledge"]["preferences"] = []
            self.memory["shared_knowledge"]["preferences"].append(preference)
        
        # Extract interests
        interest_keywords = ["interested in", "i'm interested", "i like", "i enjoy"]
        for keyword in interest_keywords:
            if keyword in user_query.lower():
                interest = user_query.lower().split(keyword)[-1].strip()
                if "interests" not in self.memory["shared_knowledge"]:
                    self.memory["shared_knowledge"]["interests"] = []
                if interest not in self.memory["shared_knowledge"]["interests"]:
                    self.memory["shared_knowledge"]["interests"].append(interest)
    
    def get_shared_knowledge(self) -> Dict:
        """Get shared knowledge that applies across all chats"""
        return self.memory["shared_knowledge"]
    
    def learn_from_patterns(self, user_query: str, successful_response: str):
        """Learn from successful interactions"""
        # Extract key terms from query
        key_terms = self._extract_key_terms(user_query)
        
        for term in key_terms:
            if term not in self.memory["learned_patterns"]:
                self.memory["learned_patterns"][term] = {
                    "successful_responses": [],
                    "frequency": 0
                }
            
            self.memory["learned_patterns"][term]["successful_responses"].append(successful_response)
            self.memory["learned_patterns"][term]["frequency"] += 1
            
            # Keep only top 5 responses per term
            if len(self.memory["learned_patterns"][term]["successful_responses"]) > 5:
                self.memory["learned_patterns"][term]["successful_responses"] = \
                    self.memory["learned_patterns"][term]["successful_responses"][-5:]
        
        self._save_memory()
        logger.info(f"🧠 Learned patterns for terms: {key_terms}")
    
    def get_user_preferences(self, user_id: str = "default") -> Dict:
        """Get user-specific preferences"""
        return self.memory["user_preferences"].get(user_id, {})
    
    def update_user_preferences(self, user_id: str, preferences: Dict):
        """Update user-specific preferences"""
        if user_id not in self.memory["user_preferences"]:
            self.memory["user_preferences"][user_id] = {}
        
        self.memory["user_preferences"][user_id].update(preferences)
        self._save_memory()
        logger.info(f"👤 Updated preferences for user: {user_id}")
    
    def add_custom_response(self, trigger_phrase: str, custom_response: str):
        """Add a custom response for specific phrases"""
        self.memory["custom_responses"][trigger_phrase.lower()] = {
            "response": custom_response,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        self._save_memory()
        logger.info(f"📝 Added custom response for: {trigger_phrase}")
    
    def get_custom_response(self, user_query: str) -> Optional[str]:
        """Check if there's a custom response for this query"""
        query_lower = user_query.lower()
        
        for trigger, data in self.memory["custom_responses"].items():
            if trigger in query_lower:
                # Increment usage count
                data["usage_count"] += 1
                self._save_memory()
                return data["response"]
        
        return None
    
    def record_feedback(self, conversation_id: int, feedback: str, rating: int):
        """Record user feedback on a response"""
        if 0 <= conversation_id < len(self.memory["conversation_history"]):
            self.memory["conversation_history"][conversation_id]["user_feedback"] = {
                "feedback": feedback,
                "rating": rating,
                "timestamp": datetime.now().isoformat()
            }
            
            # If positive feedback, learn from this interaction
            if rating >= 4:
                conversation = self.memory["conversation_history"][conversation_id]
                self.learn_from_patterns(
                    conversation["user_query"],
                    conversation["ai_response"]
                )
            
            self._save_memory()
            logger.info(f"📊 Feedback recorded: {rating}/5")
    
    def get_learned_suggestions(self, user_query: str) -> List[str]:
        """Get suggestions based on learned patterns"""
        suggestions = []
        key_terms = self._extract_key_terms(user_query)
        
        for term in key_terms:
            if term in self.memory["learned_patterns"]:
                pattern_data = self.memory["learned_patterns"][term]
                if pattern_data["frequency"] >= 2:  # Only suggest if used multiple times
                    suggestions.extend(pattern_data["successful_responses"])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def get_conversation_summary(self, days: int = 7) -> Dict:
        """Get summary of recent conversations"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_conversations = [
            conv for conv in self.memory["conversation_history"]
            if datetime.fromisoformat(conv["timestamp"]) > cutoff_date
        ]
        
        # Analyze patterns
        response_types = {}
        avg_confidence = 0
        feedback_count = 0
        
        for conv in recent_conversations:
            response_type = conv["response_type"]
            response_types[response_type] = response_types.get(response_type, 0) + 1
            avg_confidence += conv["confidence"]
            
            if conv["user_feedback"]:
                feedback_count += 1
        
        if recent_conversations:
            avg_confidence /= len(recent_conversations)
        
        return {
            "total_conversations": len(recent_conversations),
            "response_types": response_types,
            "average_confidence": round(avg_confidence, 2),
            "feedback_count": feedback_count,
            "most_common_queries": self._get_most_common_queries(recent_conversations)
        }
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text"""
        # Simple keyword extraction
        words = text.lower().split()
        
        # Filter out common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "what", "how", "when", "where", "why", "who"}
        
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        return key_terms[:5]  # Return top 5 terms
    
    def _get_most_common_queries(self, conversations: List[Dict]) -> List[str]:
        """Get most common query patterns"""
        query_counts = {}
        
        for conv in conversations:
            # Extract first few words as pattern
            words = conv["user_query"].split()[:3]
            pattern = " ".join(words).lower()
            query_counts[pattern] = query_counts.get(pattern, 0) + 1
        
        # Return top 5 patterns
        sorted_patterns = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
        return [pattern for pattern, count in sorted_patterns[:5]]

# Global memory instance
ai_memory = AIMemorySystem()

def store_interaction(user_query: str, ai_response: str, response_type: str, confidence: float):
    """Store an AI interaction"""
    ai_memory.store_conversation(user_query, ai_response, response_type, confidence)

def get_custom_response(user_query: str) -> Optional[str]:
    """Get custom response if available"""
    return ai_memory.get_custom_response(user_query)

def get_learned_suggestions(user_query: str) -> List[str]:
    """Get learned suggestions"""
    return ai_memory.get_learned_suggestions(user_query)

def add_custom_response(trigger_phrase: str, custom_response: str):
    """Add custom response"""
    ai_memory.add_custom_response(trigger_phrase, custom_response)

def get_memory_summary() -> Dict:
    """Get memory summary"""
    return ai_memory.get_conversation_summary()

if __name__ == "__main__":
    # Test the memory system
    print("🧠 Testing AI Memory System...")
    
    # Store some test interactions
    store_interaction("Create a senior credit analyst job ad", "Generated job ad", "job_ad", 0.9)
    store_interaction("What is corporate credit?", "Corporate credit definition", "answer", 0.95)
    
    # Add custom response
    add_custom_response("hello", "Hello! How can I help you with your financial needs today?")
    
    # Get summary
    summary = get_memory_summary()
    print(f"📊 Memory Summary: {summary}")
    
    print("✅ Memory system test completed!")
