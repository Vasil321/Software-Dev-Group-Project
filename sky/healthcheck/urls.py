from django.urls import path
from .views import change_password, create_team, delete_team, edit_team, manage_teams
from .views import register, user_login, dashboard, user_logout, user_settings, user_update, delete_user
from .views import manage_departments, create_department, edit_department, delete_department
from .views import uservoting, create_health_check_session, add_question, vote_analysis_view, team_progress_view

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('settings/', user_settings, name='settings'),
    path('change_password/', change_password, name='change_password'),
    path('logout/', user_logout, name='logout'),
    path('user/<str:username>/', user_update, name='user_update'),
    path('delete_user/<str:username>/', delete_user, name='delete_user'),
    path('teams/', manage_teams, name='manage_teams'),
    path('teams/create/', create_team, name='create_team'),
    path('teams/edit/<int:team_id>/', edit_team, name='edit_team'),
    path('teams/delete/<int:team_id>/', delete_team, name='delete_team'),
    path('departments/', manage_departments, name='manage_departments'),
    path('departments/create/', create_department, name='create_department'),
    path('departments/edit/<int:department_id>/', edit_department, name='edit_department'),
    path('departments/delete/<int:department_id>/', delete_department, name='delete_department'),
    path('uservoting/<int:session_id>/', uservoting, name='uservoting'),
    path('create-session/',create_health_check_session, name='create_session'),
    path('add_question/', add_question, name='add_question'),
    path('vote-analysis/',vote_analysis_view, name='vote_analysis'),
    path('team-progress/',team_progress_view,name='team_progress'),
]