# Importing necessary modules 
from django.db.models import Avg
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Vote, team

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# View 1 : Visualizing the Vote Analysis
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
@login_required ## ensuring that only the logged-in user can access this feature
def vote_analysis_view(request):
    ## querying the database to get the average vote grouped by team and session 
    vote_data = (
        Vote.objects
        .values('team_name','session_name') ## group by team name and seession
        .annotate(avg_vote=Avg('vote_value')) ## calculatng the average of the vote values
    )

    #Render the vote_analysis.html page and passing the vote data
    return render(request,'vote_analysis.html',{'vote_data':vote_data})

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# View 2: Collating Votes/Progress for Team Manager
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

@login_required ## ensuring that only the logged-in user can access this feature
def team_progress_view(request):
    user = request.user # getting the current logged-in user details

    # only allowing the team leaders to view this page
    if user.userprofile.role != 'Team Leader':
        return redirect('dashboard') ## redirecting unauthorized users
    
    ## filtering all teams that lead by th current user
    teams = Team.objects.filter(leader=user)

    ## checking if the user has selected a specific team via GET request
    selected_team = request.GET.get('team')

    ## filtering votes that are only for the selected leader's team
    votes = Vote.objects.filter(team_in=teams)

    ## if a team is selected further filter by the selected team
    if selected_team:
        votes=votes.filter(team_name=selected_team)

    ## aggregating the votes by session and calculating average votes
    session_summary = votes.values('session_name').annotate(avg_vote=Avg('vote_value'))

    ## Rendering the team_porogress.html page with all required context
    return render(request,'team_progress.html'{
        'teams':teams,
        'selected_team':selected_team,
        'session_summary':session_summary,
    })
      
