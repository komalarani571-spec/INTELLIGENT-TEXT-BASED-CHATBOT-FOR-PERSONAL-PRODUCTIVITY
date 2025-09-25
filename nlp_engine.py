import re
import json
import random
from datetime import datetime, timedelta
from textblob import TextBlob
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

class NLPEngine:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        # Initialize intent patterns and responses
        self.intents = self._load_intents()
    
    def _load_intents(self):
        """Load predefined intents, patterns, and responses"""
        return {
            'greeting': {
                'patterns': [
                    'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
                    'greetings', 'what\'s up', 'howdy', 'hola'
                ],
                'responses': [
                    'Hello! I\'m your personal productivity assistant. How can I help you today?',
                    'Hi there! I\'m here to help you stay productive. What would you like to do?',
                    'Greetings! I\'m ready to assist you with your tasks and productivity needs.',
                    'Hello! Welcome to your personal productivity chatbot. How may I assist you?'
                ]
            },
            'task_creation': {
                'patterns': [
                    'create task', 'add task', 'new task', 'make task', 'task for',
                    'remind me to', 'i need to', 'todo', 'to do', 'schedule task'
                ],
                'responses': [
                    'I\'d be happy to help you create a new task! What would you like to be reminded about?',
                    'Great! Let\'s add a new task to your list. Please tell me what you need to do.',
                    'Perfect! I\'ll help you create a task. What\'s the task description?',
                    'Sure thing! What task would you like me to add to your productivity list?'
                ]
            },
            'schedule_meeting': {
                'patterns': [
                    'schedule meeting', 'book meeting', 'arrange meeting', 'set up meeting',
                    'meeting with', 'calendar appointment', 'schedule call', 'book appointment'
                ],
                'responses': [
                    'I can help you schedule a meeting! When would you like to meet and with whom?',
                    'Let\'s get that meeting scheduled. Please provide the date, time, and participants.',
                    'I\'ll help you arrange the meeting. What are the meeting details?',
                    'Perfect! I can assist with scheduling. What are the meeting requirements?'
                ]
            },
            'time_management': {
                'patterns': [
                    'what time', 'current time', 'what day', 'today\'s date', 'schedule today',
                    'my calendar', 'free time', 'available time', 'busy schedule'
                ],
                'responses': [
                    f'The current time is {datetime.now().strftime("%I:%M %p")} on {datetime.now().strftime("%B %d, %Y")}.',
                    f'Today is {datetime.now().strftime("%A, %B %d, %Y")} and it\'s currently {datetime.now().strftime("%I:%M %p")}.',
                    'Let me help you with time management. What specific information do you need?',
                    'I can assist with your schedule and time management needs. What would you like to know?'
                ]
            },
            'productivity_tips': {
                'patterns': [
                    'productivity tips', 'be more productive', 'improve productivity',
                    'work better', 'efficiency tips', 'time management tips', 'focus better'
                ],
                'responses': [
                    'Here are some productivity tips: 1) Use the Pomodoro Technique (25min work, 5min break), 2) Prioritize tasks using the Eisenhower Matrix, 3) Eliminate distractions during focused work time.',
                    'To boost productivity: Break large tasks into smaller ones, set specific deadlines, use time-blocking for your calendar, and take regular breaks to maintain focus.',
                    'Great productivity strategies include: batching similar tasks together, using the 2-minute rule (do it now if it takes less than 2 minutes), and reviewing your goals weekly.',
                    'For better productivity: Start with your most important task, minimize multitasking, use productivity apps for tracking, and maintain a consistent daily routine.'
                ]
            },
            'reminder': {
                'patterns': [
                    'remind me', 'set reminder', 'don\'t forget', 'remember to',
                    'notification for', 'alert me', 'ping me about'
                ],
                'responses': [
                    'I\'ll set up a reminder for you! What should I remind you about and when?',
                    'Perfect! I can create a reminder. Please specify what and when you\'d like to be reminded.',
                    'I\'d be happy to set a reminder. What\'s the reminder details and timing?',
                    'Sure! Let me set that reminder. What should I remind you about?'
                ]
            },
            'status_check': {
                'patterns': [
                    'how are you', 'how\'s it going', 'status', 'are you working',
                    'system status', 'how do you feel', 'what\'s your status'
                ],
                'responses': [
                    'I\'m functioning perfectly and ready to help you be more productive!',
                    'All systems are running smoothly! I\'m here and ready to assist with your tasks.',
                    'I\'m doing great and excited to help you achieve your productivity goals!',
                    'Everything\'s working well on my end. How can I help you stay productive today?'
                ]
            },
            'help': {
                'patterns': [
                    'help', 'what can you do', 'commands', 'features', 'capabilities',
                    'how to use', 'instructions', 'guide', 'what are your functions'
                ],
                'responses': [
                    'I can help you with: ✓ Creating and managing tasks ✓ Scheduling meetings ✓ Setting reminders ✓ Providing productivity tips ✓ Time management ✓ General productivity assistance. Just ask me naturally!',
                    'Here\'s what I can do for you: Create tasks, schedule meetings, set reminders, provide productivity advice, help with time management, and answer questions about your schedule.',
                    'My capabilities include: Task management, meeting scheduling, reminder setting, productivity coaching, time tracking assistance, and general productivity support. How can I help?',
                    'I\'m your productivity assistant! I can create tasks, schedule meetings, set reminders, give productivity tips, help with time management, and much more. What would you like to do?'
                ]
            },
            'goodbye': {
                'patterns': [
                    'bye', 'goodbye', 'see you later', 'farewell', 'talk to you later',
                    'exit', 'quit', 'end chat', 'that\'s all', 'thanks bye'
                ],
                'responses': [
                    'Goodbye! Stay productive and have a great day!',
                    'See you later! Remember to stay focused on your goals.',
                    'Farewell! I\'m here whenever you need productivity assistance.',
                    'Bye! Keep up the great work on your productivity journey!'
                ]
            },
            'unknown': {
                'patterns': [],
                'responses': [
                    'I\'m not sure I understand that. Could you please rephrase or ask me about tasks, meetings, reminders, or productivity tips?',
                    'I didn\'t quite catch that. I can help with task management, scheduling, reminders, and productivity advice. What would you like to do?',
                    'I\'m still learning! Could you try asking about creating tasks, scheduling meetings, setting reminders, or getting productivity tips?',
                    'I\'m not sure how to help with that. I specialize in productivity assistance - tasks, meetings, reminders, and time management. What can I help you with?'
                ]
            }
        }
    
    def preprocess_text(self, text):
        """Preprocess input text for better matching"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove punctuation and extra spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stop words and stem
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words:
                stemmed = self.stemmer.stem(token)
                processed_tokens.append(stemmed)
        
        return ' '.join(processed_tokens), tokens
    
    def classify_intent(self, user_input):
        """Classify the intent of user input"""
        processed_input, original_tokens = self.preprocess_text(user_input)
        
        best_intent = 'unknown'
        best_confidence = 0.0
        
        for intent_name, intent_data in self.intents.items():
            if intent_name == 'unknown':
                continue
                
            confidence = 0.0
            pattern_matches = 0
            
            for pattern in intent_data['patterns']:
                processed_pattern, _ = self.preprocess_text(pattern)
                
                # Exact match gets highest score
                if processed_pattern in processed_input:
                    confidence += 1.0
                    pattern_matches += 1
                
                # Partial word matches
                pattern_words = processed_pattern.split()
                input_words = processed_input.split()
                
                for pattern_word in pattern_words:
                    if pattern_word in input_words:
                        confidence += 0.5
                        pattern_matches += 1
            
            # Normalize confidence by number of patterns
            if len(intent_data['patterns']) > 0:
                confidence = confidence / len(intent_data['patterns'])
            
            # Boost confidence if multiple patterns match
            if pattern_matches > 1:
                confidence *= 1.2
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_intent = intent_name
        
        # Set minimum confidence threshold
        if best_confidence < 0.3:
            best_intent = 'unknown'
            best_confidence = 0.1
        
        return best_intent, best_confidence
    
    def extract_entities(self, user_input, intent):
        """Extract entities from user input based on intent"""
        entities = {}
        
        # Time extraction for scheduling and reminders
        time_patterns = {
            'time': r'(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)?',
            'date': r'(today|tomorrow|yesterday|\d{1,2}/\d{1,2}|\d{1,2}-\d{1,2})',
            'day': r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            'duration': r'(\d+)\s*(minute|minutes|hour|hours|day|days|week|weeks)'
        }
        
        for entity_type, pattern in time_patterns.items():
            matches = re.findall(pattern, user_input.lower())
            if matches:
                entities[entity_type] = matches
        
        # Task/meeting content extraction
        if intent in ['task_creation', 'reminder']:
            # Extract task description after keywords
            task_keywords = ['create task', 'add task', 'remind me to', 'i need to', 'todo']
            for keyword in task_keywords:
                if keyword in user_input.lower():
                    task_start = user_input.lower().find(keyword) + len(keyword)
                    task_description = user_input[task_start:].strip()
                    if task_description:
                        entities['task_description'] = task_description
                    break
        
        # Meeting participants extraction
        if intent == 'schedule_meeting':
            # Look for names or "with" patterns
            with_pattern = r'with\s+([A-Za-z\s]+?)(?:\s+at|\s+on|\s+for|$)'
            matches = re.findall(with_pattern, user_input, re.IGNORECASE)
            if matches:
                entities['participants'] = [match.strip() for match in matches]
        
        return entities
    
    def generate_response(self, intent, entities=None, context=None):
        """Generate appropriate response based on intent and entities"""
        if intent not in self.intents:
            intent = 'unknown'
        
        responses = self.intents[intent]['responses']
        base_response = random.choice(responses)
        
        # Enhance response with entity information
        if entities and intent in ['task_creation', 'reminder']:
            if 'task_description' in entities:
                base_response += f' Task: "{entities["task_description"]}"'
            if 'time' in entities:
                base_response += f' Time: {entities["time"][0]}'
            if 'date' in entities:
                base_response += f' Date: {entities["date"][0]}'
        
        if entities and intent == 'schedule_meeting':
            if 'participants' in entities:
                participants = ', '.join(entities['participants'])
                base_response += f' Participants: {participants}'
            if 'time' in entities:
                base_response += f' Time: {entities["time"][0]}'
        
        return base_response
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of user input"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'polarity': polarity,
            'subjectivity': subjectivity
        }
    
    def process_message(self, user_input, context=None):
        """Main method to process user message and generate response"""
        # Classify intent
        intent, confidence = self.classify_intent(user_input)
        
        # Extract entities
        entities = self.extract_entities(user_input, intent)
        
        # Analyze sentiment
        sentiment = self.analyze_sentiment(user_input)
        
        # Generate response
        response = self.generate_response(intent, entities, context)
        
        return {
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'sentiment': sentiment,
            'response': response,
            'processed_input': user_input.strip()
        }

