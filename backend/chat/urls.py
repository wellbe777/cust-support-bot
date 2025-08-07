from django.urls import path
from .views import ChatView, ConversationView, CreateTicketView, TicketStatusView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('conversation/<str:session_id>/', ConversationView.as_view(), name='conversation'),
    path('ticket/create/', CreateTicketView.as_view(), name='create_ticket'),
    path('ticket/<str:ticket_id>/', TicketStatusView.as_view(), name='ticket_status'),
]