from flask import Blueprint, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from src.models.user import db, User
from src.models.conversation import Conversation, Message, Intent
from src.services.nlp_engine import NLPEngine
import uuid
from datetime import datetime
import json

chatbot_bp = Blueprint('chatbot', __name__)

# Initialize NLP Engine
nlp_engine = NLPEngine()

# WebSocket events will be registered in main.py

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages via REST API"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message'].strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        user_id = data.get('user_id', 1)  # Default user for demo
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get or create conversation
        conversation = Conversation.query.filter_by(session_id=session_id).first()
        if not conversation:
            conversation = Conversation(
                user_id=user_id,
                session_id=session_id,
                status='active'
            )
            db.session.add(conversation)
            db.session.commit()
        
        # Save user message
        user_msg = Message(
            conversation_id=conversation.id,
            sender='user',
            content=user_message
        )
        db.session.add(user_msg)
        
        # Process message with NLP engine
        nlp_result = nlp_engine.process_message(user_message)
        
        # Generate bot response
        bot_response = nlp_result['response']
        
        # Save bot message
        bot_msg = Message(
            conversation_id=conversation.id,
            sender='bot',
            content=bot_response,
            intent=nlp_result['intent'],
            confidence=nlp_result['confidence']
        )
        db.session.add(bot_msg)
        db.session.commit()
        
        return jsonify({
            'session_id': session_id,
            'user_message': user_message,
            'bot_response': bot_response,
            'intent': nlp_result['intent'],
            'confidence': nlp_result['confidence'],
            'entities': nlp_result['entities'],
            'sentiment': nlp_result['sentiment'],
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations for a user"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        conversations = Conversation.query.filter_by(user_id=user_id).order_by(
            Conversation.started_at.desc()
        ).all()
        
        return jsonify({
            'conversations': [conv.to_dict() for conv in conversations]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/conversations/<session_id>/messages', methods=['GET'])
def get_conversation_messages(session_id):
    """Get all messages for a specific conversation"""
    try:
        conversation = Conversation.query.filter_by(session_id=session_id).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        messages = Message.query.filter_by(conversation_id=conversation.id).order_by(
            Message.timestamp.asc()
        ).all()
        
        return jsonify({
            'session_id': session_id,
            'conversation': conversation.to_dict(),
            'messages': [msg.to_dict() for msg in messages]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/conversations/<session_id>', methods=['DELETE'])
def delete_conversation(session_id):
    """Delete a conversation and all its messages"""
    try:
        conversation = Conversation.query.filter_by(session_id=session_id).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Delete all messages (cascade should handle this)
        db.session.delete(conversation)
        db.session.commit()
        
        return jsonify({'message': 'Conversation deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/intents', methods=['GET'])
def get_intents():
    """Get all available intents"""
    try:
        intents = nlp_engine.intents
        return jsonify({
            'intents': {
                name: {
                    'patterns': data['patterns'][:3],  # Show first 3 patterns
                    'sample_response': data['responses'][0]
                }
                for name, data in intents.items()
                if name != 'unknown'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get conversation analytics"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        # Total conversations
        total_conversations = Conversation.query.filter_by(user_id=user_id).count()
        
        # Total messages
        total_messages = db.session.query(Message).join(Conversation).filter(
            Conversation.user_id == user_id
        ).count()
        
        # Intent distribution
        intent_stats = db.session.query(
            Message.intent, 
            db.func.count(Message.id).label('count')
        ).join(Conversation).filter(
            Conversation.user_id == user_id,
            Message.sender == 'user',
            Message.intent.isnot(None)
        ).group_by(Message.intent).all()
        
        # Average confidence
        avg_confidence = db.session.query(
            db.func.avg(Message.confidence)
        ).join(Conversation).filter(
            Conversation.user_id == user_id,
            Message.sender == 'user',
            Message.confidence.isnot(None)
        ).scalar()
        
        return jsonify({
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'intent_distribution': {
                intent: count for intent, count in intent_stats
            },
            'average_confidence': float(avg_confidence) if avg_confidence else 0.0,
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket event handlers (to be registered in main.py)
def handle_connect(auth):
    """Handle client connection"""
    session_id = request.args.get('session_id', str(uuid.uuid4()))
    join_room(session_id)
    emit('connected', {
        'session_id': session_id,
        'message': 'Connected to chatbot successfully!'
    })

def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

def handle_message(data):
    """Handle incoming WebSocket message"""
    try:
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        user_id = data.get('user_id', 1)
        
        if not user_message:
            emit('error', {'message': 'Message cannot be empty'})
            return
        
        # Emit typing indicator
        emit('typing', {'typing': True}, room=session_id)
        
        # Get or create conversation
        conversation = Conversation.query.filter_by(session_id=session_id).first()
        if not conversation:
            conversation = Conversation(
                user_id=user_id,
                session_id=session_id,
                status='active'
            )
            db.session.add(conversation)
            db.session.commit()
        
        # Save user message
        user_msg = Message(
            conversation_id=conversation.id,
            sender='user',
            content=user_message
        )
        db.session.add(user_msg)
        
        # Process message with NLP engine
        nlp_result = nlp_engine.process_message(user_message)
        
        # Generate bot response
        bot_response = nlp_result['response']
        
        # Save bot message
        bot_msg = Message(
            conversation_id=conversation.id,
            sender='bot',
            content=bot_response,
            intent=nlp_result['intent'],
            confidence=nlp_result['confidence']
        )
        db.session.add(bot_msg)
        db.session.commit()
        
        # Stop typing indicator
        emit('typing', {'typing': False}, room=session_id)
        
        # Send response
        emit('message', {
            'session_id': session_id,
            'user_message': user_message,
            'bot_response': bot_response,
            'intent': nlp_result['intent'],
            'confidence': nlp_result['confidence'],
            'entities': nlp_result['entities'],
            'sentiment': nlp_result['sentiment'],
            'timestamp': datetime.utcnow().isoformat()
        }, room=session_id)
        
    except Exception as e:
        emit('error', {'message': str(e)})

def handle_join_room(data):
    """Handle joining a chat room"""
    session_id = data.get('session_id')
    if session_id:
        join_room(session_id)
        emit('joined', {'session_id': session_id})

def handle_leave_room(data):
    """Handle leaving a chat room"""
    session_id = data.get('session_id')
    if session_id:
        leave_room(session_id)
        emit('left', {'session_id': session_id})

