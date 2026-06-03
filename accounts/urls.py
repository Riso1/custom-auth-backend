from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    ProfileView,
    RegistrationView,
    ProductsView,
    OrdersView,
    AccessRulesView,
    AccessRuleDetailView,
)


urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('products/', ProductsView.as_view(), name='products'),
    path('orders/', OrdersView.as_view(), name='orders'),
    path('access-rules/', AccessRulesView.as_view(), name='access_rules'),
    path('access-rules/<int:rule_id>/', AccessRuleDetailView.as_view(), name='access_rules_detail'),
]