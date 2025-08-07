from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
import uuid
import logging
import json

from .models import Conversation, Message, SupportTicket
from .serializers import (
    ChatRequestSerializer, 
    ConversationSerializer, 
    MessageSerializer,
    SupportTicketSerializer
)
from .gemini_service import GeminiService

logger = logging.getLogger(__name__)


class ChatView(APIView):
    def __init__(self):
        super().__init__()
        try:
            self.gemini_service = GeminiService()
        except ValueError as e:
            logger.error(f"Failed to initialize Gemini service: {str(e)}")
            self.gemini_service = None

    def post(self, request):
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.data

            # Clean the data - remove null/empty session_id
            if 'session_id' in data and (data['session_id'] is None or data['session_id'] == ''):
                data.pop('session_id')

            logger.info(f"Received data: {data}")

            serializer = ChatRequestSerializer(data=data)
            if not serializer.is_valid():
                logger.error(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            user_message = serializer.validated_data['message']
            session_id = serializer.validated_data.get('session_id')
            
            logger.info(f"Received message: {user_message[:50]}...")
            logger.info(f"Session ID: {session_id}")
            
            # Create or get conversation
            if not session_id:
                session_id = str(uuid.uuid4())
                logger.info(f"Generated new session ID: {session_id}")
            
            conversation, created = Conversation.objects.get_or_create(
                session_id=session_id,
                defaults={'session_id': session_id}
            )
            
            logger.info(f"Conversation {'created' if created else 'found'}: {conversation.session_id}")
            
            # Save user message
            user_msg = Message.objects.create(
                conversation=conversation,
                content=user_message,
                sender='user'
            )
            
            # Generate bot response
            if self.gemini_service:
                # Get conversation history for context
                recent_messages = Message.objects.filter(
                    conversation=conversation
                ).order_by('-timestamp')[:10]
                
                conversation_history = [
                    {
                        'content': msg.content,
                        'sender': msg.sender
                    }
                    for msg in reversed(recent_messages)
                ]
                
                bot_response = self.gemini_service.generate_response(
                    user_message, 
                    conversation_history
                )
                
                # Analyze intent for potential escalation
                intent_analysis = self.gemini_service.analyze_intent(user_message)
                
            else:
                bot_response = "I apologize, but our AI assistant is currently unavailable. Please contact our support team directly for assistance."
                intent_analysis = {"requires_human": True}
            
            # Save bot response
            bot_msg = Message.objects.create(
                conversation=conversation,
                content=bot_response,
                sender='bot'
            )
            
            response_data = {
                'response': bot_response,
                'session_id': session_id,
                'message_id': bot_msg.id,
                'requires_human': intent_analysis.get('requires_human', False)
            }
            
            logger.info(f"Sending response: {bot_response[:50]}...")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in ChatView: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationView(APIView):
    def get(self, request, session_id):
        try:
            conversation = Conversation.objects.get(session_id=session_id)
            serializer = ConversationSerializer(conversation)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class CreateTicketView(APIView):
    def post(self, request):
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.data
                
            session_id = data.get('session_id')
            subject = data.get('subject', 'Support Request')
            description = data.get('description', '')
            
            # Generate unique ticket ID
            ticket_id = f"CS-{uuid.uuid4().hex[:8].upper()}"
            
            # Get conversation if exists
            conversation = None
            if session_id:
                try:
                    conversation = Conversation.objects.get(session_id=session_id)
                except Conversation.DoesNotExist:
                    pass
            
            # Create support ticket
            ticket = SupportTicket.objects.create(
                conversation=conversation,
                ticket_id=ticket_id,
                subject=subject,
                description=description,
                priority='medium'
            )
            
            serializer = SupportTicketSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TicketStatusView(APIView):
    def get(self, request, ticket_id):
        try:
            ticket = SupportTicket.objects.get(ticket_id=ticket_id)
            serializer = SupportTicketSerializer(ticket)
            return Response(serializer.data)
        except SupportTicket.DoesNotExist:
            return Response(
                {'error': 'Ticket not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )