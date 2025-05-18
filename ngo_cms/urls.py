from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from NGO.views import user_login  # Import your custom login view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('NGO.urls')),
    # Override /accounts/login/ with custom view
    path('accounts/login/', user_login, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),  # For logout, password reset, etc.
    # Password reset URLs (already set up)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='NGO/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='NGO/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='NGO/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='NGO/password_reset_complete.html'), name='password_reset_complete'),
]