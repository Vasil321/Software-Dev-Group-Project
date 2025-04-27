from django.urls import path
from .views import add_question ,create_health_check_session ,uservoting, change_password, create_team, delete_team, edit_team, manage_teams, register, user_login, dashboard, user_logout, user_settings

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('settings/', user_settings, name='settings'),
    path('change_password/', change_password, name='change_password'),
    path('logout/', user_logout, name='logout'),
    path('teams/', manage_teams, name='manage_teams'),
    path('teams/create/', create_team, name='create_team'),
    path('teams/edit/<int:team_id>/', edit_team, name='edit_team'),
    path('teams/delete/<int:team_id>/', delete_team, name='delete_team'),
    path('uservoting/<int:session_id>/', uservoting, name='uservoting'),
    path('create-session/',create_health_check_session, name='create_session'),
    path('add_question/', add_question, name='add_question'),
]