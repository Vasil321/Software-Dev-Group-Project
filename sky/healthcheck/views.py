from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import UserProfile, Team, Department, Question, Response, HealthCheckSession, Vote
from .forms import HealthCheckSessionForm, QuestionForm
from django.http import HttpResponse
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserSettingsForm, ChangePasswordForm, UserUpdateForm
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required

from django.db.models import Avg



'''
register view is used to register a new user.
It renders the register.html template.
'''
def register(request):
    error_message = None
    if request.method == 'POST':
        
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            if len(request.POST["username"]) < 5 or len(request.POST["username"]) > 30:
                error_message = "Username must be 5 to 30 characters long."
                return render(request, 'register.html', {'form': form, 'error': error_message})

            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password1'])
            user.save()
            UserProfile.objects.create(user=user, role=form.cleaned_data['role'])
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

'''
user_login view is used to log in the user.
It renders the login.html template.
'''
def user_login(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            error_message = "Invalid username or password."
    print(error_message)
    return render(request, 'login.html', { 'error': error_message })


'''
user_logout view is used to log out the user.
It redirects the user to the login page.
'''
def user_logout(request):
    logout(request)
    return redirect('login')


'''
dashboard view is used to render the dashboard.html template.
It displays the user's role.
'''
@login_required
def dashboard(request):
    if request.user.userprofile.role == 'Admin':
        teams = Team.objects.all()
        departments = Department.objects.all()
        users = User.objects.all()
        return render(request, 'dashboard.html', {'users' : users, 'teams' : teams, 'departments': departments})

    if request.user.userprofile.role == 'Senior Manager':
        departments = Department.objects.all()
        teams = Team.objects.all()
        return render(request, 'dashboard.html', {'departments' : departments, 'teams': teams})

    if request.user.userprofile.role == 'Team Leader':
        teams = Team.objects.filter(leader=request.user)
        sessions = HealthCheckSession.objects.filter(team_leader=request.user)
        return render(request, 'dashboard.html', {'teams' : teams, 'sessions': sessions})
    
    if request.user.userprofile.role == 'Department Leader':
        departments = Department.objects.filter(leader=request.user)
        teams = Team.objects.filter(department__in=departments)
        return render(request, 'dashboard.html', {'departments' : departments, 'teams': teams})
    
    if request.user.userprofile.role == 'Engineer':
        teams = Team.objects.filter(engineers=request.user)
        team_leaders = teams.values_list('leader', flat=True).distinct()
        sessions = HealthCheckSession.objects.filter(team_leader__in=team_leaders)
        return render(request, 'dashboard.html', {'teams' : teams, 'sessions': sessions})

    return render(request, 'dashboard.html')


'''
user_settings view is used to update the user's first name, last name and email.
It renders the settings.html template.
'''
@login_required
def user_settings(request):

    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        
    else:
        form = UserSettingsForm(instance=request.user)
        
    return render(request, 'settings.html', {'form': form})


'''
user_update view is used to update the user's first name, last name and email.
It is only accessible by the app admin.
It renders the user_update.html template.
'''
@login_required
def user_update(request, username):
    if not request.user.userprofile.role == 'Admin':
        messages.error(request, 'Access Denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        user = get_object_or_404(User, username=username)
        form = UserUpdateForm(request.POST, instance=user, role_initial=request.POST.get('role'))
        if form.is_valid():
            form.save()
            user_profile = user.userprofile
            user_profile.role = form.cleaned_data['role']
            user_profile.save()
            return redirect('dashboard')
    else:
        user = get_object_or_404(User, username=username)
        form = UserUpdateForm(instance=user, role_initial=user.userprofile.role)

    return render(request, 'user_update.html', {'form': form})


'''
delete_team view is used to delete a team.
It redirects the user to the manage_teams page.
'''
@login_required
def delete_user(request, username):
    if not request.user.userprofile.role == 'Admin':
        messages.error(request, 'Access Denied.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, username=username)
    user.delete()
    return redirect('dashboard')



'''
change_password view is used to change the user's password.
It renders the change_password.html template.
'''
@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevents logout after password change
            messages.success(request, "Your password has been updated successfully!")
            return redirect("dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ChangePasswordForm(user=request.user)

    return render(request, "change_password.html", {"form": form})


'''
manage_teams view is used to manage the teams.
It renders the manage_teams.html template.
'''
@login_required
def manage_teams(request):
    if not request.user.userprofile.role == 'Team Leader' and not request.user.userprofile.role == 'Department Leader':
        messages.error(request, 'Access Denied.')
        return redirect('dashboard')
    
    teams = Team.objects.filter(leader=request.user)
    return render(request, 'manage_teams.html', {'teams': teams})


'''
create_team view is used to create a team.
It renders the create_team.html template.
'''
@login_required
def create_team(request):
    if not request.user.userprofile.role == 'Team Leader' and not request.user.userprofile.role == 'Admin':
        messages.error(request, 'Access Denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        engineers = request.POST.getlist('engineers')

        team_leader = request.user
        if request.user.userprofile.role == 'Admin':
            team_leader = User.objects.get(id=request.POST.get('leader'))
        team = Team.objects.create(name=name, leader=team_leader)
        
        messages.success(request, f"Team {name} created successfully.")
        return redirect('dashboard')
    
    users = User.objects.all()
    if request.user.userprofile.role == 'Admin':
        users = User.objects.filter(userprofile__role='Team Leader')

    return render(request, 'create_team.html', {'users': users})


'''
edit_team view is used to edit a team.
It renders the edit_team.html template.
'''
@login_required
def edit_team(request, team_id):
    if not request.user.userprofile.role == 'Team Leader' and not request.user.userprofile.role == 'Admin':
        messages.error(request, 'Access Denied.')
        return redirect('dashboard')
    
    team = get_object_or_404(Team, id=team_id)
    engineers = User.objects.filter(userprofile__role='Engineer')

    if request.method == 'POST':
        team.name = request.POST.get('name')
        selected_engineers = request.POST.getlist('engineers')
        team.engineers.set(User.objects.filter(id__in=selected_engineers))
        team.save()
        messages.success(request, f"Team {team.name} updated successfully.")
        return redirect('dashboard')
    
    return render(request, 'edit_team.html', {'team': team, 'engineers': engineers})


'''
delete_team view is used to delete a team.
It redirects the user to the manage_teams page.
'''
@login_required
def delete_team(request, team_id):
    if not request.user.userprofile.role == 'Team Leader' and not request.user.userprofile.role == 'Admin':
        messages.error(request, 'Access Denied.')
        return redirect('dashboard')
    
    team = get_object_or_404(Team, id=team_id)
    team.delete()
    messages.success(request, f"Team {team.name} deleted successfully.")
    return redirect('dashboard')


'''
manage_departments view is used to manage the departments.
It renders the manage_departments.html template.
'''
@login_required
def manage_departments(request):
    if not request.user.userprofile.role == 'Department Leader':
        messages.error(request, 'Access Denied.')
        return redirect('dashboard')
    
    departments = Department.objects.filter(leader=request.user)

    return render(request, 'manage_departments.html', {'departments': departments})


'''
create_department view is used to create a department.
It renders the create_department.html template.
'''
@login_required
def create_department(request):
    if not request.user.userprofile.role == 'Department Leader' and not request.user.userprofile.role == 'Admin':
        messages.error(request, 'Access Denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')

        department_leader = request.user
        if request.user.userprofile.role == 'Admin':
            department_leader = User.objects.get(id=request.POST.get('leader'))

        
        department = Department.objects.create(name=name, leader=department_leader)
        messages.success(request, f"Department {name} created successfully.")
        return redirect('dashboard')
        
    

    users = User.objects.all()
    if request.user.userprofile.role == 'Admin':
        users = User.objects.filter(userprofile__role='Department Leader')

    return render(request, 'create_department.html', {'users': users})


'''
edit_department view is used to edit a department.
It renders the edit_department.html template.
'''
@login_required
def edit_department(request, department_id):
    if not request.user.userprofile.role == 'Department Leader' and not request.user.userprofile.role == 'Admin':
        messages.error(request, 'Access Denied.')
        return redirect('dashboard')
    
    department = get_object_or_404(Department, id=department_id)
    teams = Team.objects.all()

    if request.method == 'POST':
        department.name = request.POST.get('name')
        selected_teams = request.POST.getlist('teams')
        department.teams.set(Team.objects.filter(id__in=selected_teams))
        department.save()
        messages.success(request, f"Department {department.name} updated successfully.")
        return redirect('dashboard')
    
    return render(request, 'edit_department.html', {'department': department, 'teams': teams})


'''
delete_department view is used to delete a department.
It redirects the user to the manage_departments page.
'''
@login_required
def delete_department(request, department_id):
    if not request.user.userprofile.role == 'Department Leader' and not request.user.userprofile.role == 'Admin':
        messages.error(request, 'Access Denied.')
        return redirect('dashboard')
    
    department = get_object_or_404(Department, id=department_id)
    department.delete()
    messages.success(request, f"Department {department.name} deleted successfully.")
    return redirect('dashboard')


'''
Views for creating healthcheck session, adding questions and user voting
'''
@login_required
def uservoting(request, session_id):
    questions = Question.objects.all()
    session = HealthCheckSession.objects.get(id=session_id)
    questions = session.questions.all().order_by('id')
    for question in questions:
        print(question.text)
    

    if request.method == 'POST':
        for question in questions:
            answer = request.POST.get(f'question_{question.id}')
            if answer:
                Response.objects.update_or_create(
                    user=request.user,
                    question=question,
                    defaults={'answer': answer}
                )
        return redirect('uservoting',  session_id=session.id)  # or wherever

    return render(request, 'uservoting.html', {'session': session, 'questions': questions})



@login_required
def create_health_check_session(request):
    if not request.user.userprofile.role == 'Team Leader':
        return redirect('unauthorized')  # or use PermissionDenied

    if request.method == 'POST':
        form = HealthCheckSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.team_leader = request.user
            session.save()
            form.save_m2m()
            # return redirect('uservoting', session_id=session.id)
            return redirect('dashboard')  # or another page
    else:
        form = HealthCheckSessionForm()

    return render(request, 'create_session.html', {'form': form})



@login_required
def add_question(request):
    if not request.user.userprofile.role == 'Team Leader':
        return redirect('unauthorized')

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.created_by = request.user
            question.save()
            return redirect('create_session')  # or another page
    else:
        form = QuestionForm()

    return render(request, 'add_question.html', {'form': form})



#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# View 1 : Visualizing the Vote Analysis
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
@login_required ## ensuring that only the logged-in user can access this feature
def vote_analysis_view(request):
    ## querying the database to get the average vote grouped by team and session 
    vote_data = (
        Vote.objects
        .values('team','session') ## group by team name and seession
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
    #votes = Vote.objects.filter(team_in=teams)
    votes = Vote.objects.filter(team__in=teams)

    ## if a team is selected further filter by the selected team
    if selected_team:
        selected_team_obj = Team.objects.filter(name=selected_team)
        votes=votes.filter(team__in=selected_team_obj)

    ## aggregating the votes by session and calculating average votes
    session_summary = votes.values('session').annotate(avg_vote=Avg('vote_value'))

    ## Rendering the team_porogress.html page with all required context
    return render(request,'team_progress.html', {
        'teams':teams,
        'selected_team':selected_team,
        'session_summary':session_summary,
    })