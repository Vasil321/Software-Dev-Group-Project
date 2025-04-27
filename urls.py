from .views import vote_analysis_view, team_progress_view

path('vote-analysis/',vote_analysis_view, name='vote_analysis'),
path('team-progress/',team_progress_view,name='team_progress'),