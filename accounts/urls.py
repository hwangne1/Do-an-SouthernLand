from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('favorite/<int:listing_id>', views.toggle_favorite, name='toggle_favorite'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),

    # ── Password reset flow ─────────────────────────────
    path(
        'password-reset',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset_form.html',
            email_template_name='accounts/password_reset_email.txt',
            subject_template_name='accounts/password_reset_subject.txt',
            success_url='/accounts/password-reset/done',
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url='/accounts/reset/done',
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
    
]