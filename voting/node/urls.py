from django.urls import path
from .views import *

app_name = 'node'

urlpatterns = [
    #path('validate/', BlindToValidate.as_view(), name = 'blind_to_validate'),
    path('login/', Login.as_view(), name = 'login'),
    #path('', Home.as_view(), name = 'home'),
    path('', AuthHome.as_view(), name = 'auth_home'),
    path('new_validations/', NewValidation.as_view(), name = 'new_validations'),
    path('sign-blinded/<hashed_blinded_secret>/', SignBlinded.as_view(), name = 'sign_blinded'),
    path('view-blockchain/', AuthHome.as_view(), name = 'view_blockchain'),
    
]