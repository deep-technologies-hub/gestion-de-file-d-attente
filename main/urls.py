# Exemple pour urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AvailabilityViewSet, ClientViewSet, ServiceViewSet, IssueViewSet, SubscriptionViewSet, TicketViewSet, \
    LogoutView, RegisterView, VerifyCodeView, ResendCodeView, SendEmailView, CustomAuthToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'issues', IssueViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'tickets', TicketViewSet)
router.register(r'availabilities', AvailabilityViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('resend-code/', ResendCodeView.as_view(), name='resend-code'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('send-email/', SendEmailView.as_view(), name='send-email'),
]