from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import UserProfile, Team, Question, Response, HealthCheckSession
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserSettingsForm, ChangePasswordForm, ResponseForm, QuestionForm, HealthCheckSessionForm
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required

'''
register view is used to register a new user.
It renders the register.html template.
'''
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
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
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')

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
    if request.user.userprofile.role == 'Team Leader':
        teams = Team.objects.filter(leader=request.user)
        # sessions = QuestionSession.objects.filter(team__in=teams)
        # answers = Answer.objects.filter(session__in=sessions)
        # return render(request, 'dashboard.html', {'teams' : teams, 'sessions' : sessions, 'answers' : answers})
        return render(request, 'dashboard.html', {'teams' : teams})
    
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
    if not request.user.userprofile.role == 'Team Leader':
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
    if not request.user.userprofile.role == 'Team Leader':
        messages.error(request, 'Access Denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        engineers = request.POST.getlist('engineers')
        team = Team.objects.create(name=name, leader=request.user)
        messages.success(request, f"Team {name} created successfully.")
        return redirect('manage_teams')
    
    return render(request, 'create_team.html')

'''
edit_team view is used to edit a team.
It renders the edit_team.html template.
'''
@login_required
def edit_team(request, team_id):
    if not request.user.userprofile.role == 'Team Leader':
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
        return redirect('manage_teams')
    
    return render(request, 'edit_team.html', {'team': team, 'engineers': engineers})

'''
delete_team view is used to delete a team.
It redirects the user to the manage_teams page.
'''
@login_required
def delete_team(request, team_id):
    if not request.user.userprofile.role == 'Team Leader':
        messages.error(request, 'Access Denied.')
        return redirect('dashboard')
    
    team = get_object_or_404(Team, id=team_id)
    team.delete()
    messages.success(request, f"Team {team.name} deleted successfully.")
    return redirect('manage_teams')


@login_required
def uservoting(request, session_id):
    questions = Question.objects.all()
    session = HealthCheckSession.objects.get(id=session_id)
    questions = session.questions.all().order_by('id')
    

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
            return redirect('uservoting', session_id=session.id)
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