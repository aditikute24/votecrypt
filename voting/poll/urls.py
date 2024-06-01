from django.urls import path, include
from .views import *

app_name = 'poll'

urlpatterns = [
    path('new_poll/', CreatePoll.as_view(), name = "new_question"),
    path('add_option/', AddOption.as_view(), name = "add_option"),
    path('home/', PollHome.as_view(), name = "poll_home"),
    path('mine/', MineBlock.as_view(), name = 'mine'), 
    path('<poll_id>/', PollDetailView.as_view(), name = "poll_detail"),
    path('<poll_id>/end_poll/', EndPoll.as_view(), name = "end_poll"),  
]