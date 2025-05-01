from django.db import models
from django.contrib.auth.models import User

'''
UserProfile model is used to store the role of the user.
It has a one-to-one relationship with the User model.
'''
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Senior Manager', 'Senior Manager'),
        ('Department Leader', 'Department Leader'),
        ('Team Leader', 'Team Leader'),
        ('Engineer', 'Engineer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Engineer')

    def _str_(self):
        return f"{self.user.username} - {self.role}"



'''
Team model is used to store the team details.
'''
class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')
    engineers = models.ManyToManyField(User, related_name='teams', blank=True)

    def _str_(self):
        return self.name

'''
Department model is used to store department details.
'''
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_departments')
    teams = models.ManyToManyField(Team, blank=True)

    def _str_(self):
        return self.name
    

'''
Question model is used to store the questions for the health check.
It has a text field to store the question.
'''
class Question(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text


'''
Response model is used to store the responses for an user to a specific question for the health check.
It has a foreign key to the User model to store the user.
It has a foreign key to the Question model to store the question.
It has a char field to store the answer.
It has a timestamp field to store the timestamp of when the response was created.
'''
class Response(models.Model):
    TRAFFIC_LIGHT_CHOICES = [
        ('green', 'Very Good'),
        ('yellow', 'Not That Good'),
        ('red', 'Very Bad'),
    ]
    answer_choices = {
        1:'green',
        2:'yellow',
        3:'red'
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=10, choices=TRAFFIC_LIGHT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question.text[:30]} - {self.answer}"


'''
HealthCheckSession model is used to store the health check session details.
It has a name field to store the name of the session.
It has a many-to-many relationship with the Question model.
It has a foreign key to the User model to store the team leader.
It has a created_at field to store the timestamp of when the session was created.
'''
class HealthCheckSession(models.Model):
    name = models.CharField(max_length=100)
    team_leader = models.ForeignKey(User, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Who voted
    session = models.ForeignKey('HealthCheckSession', on_delete=models.CASCADE)  # Which session
    team = models.ForeignKey('Team', on_delete=models.CASCADE)  # Which team
    vote_value = models.IntegerField()  # The actual vote (e.g. 1–10 scale)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"{self.user.username} voted {self.vote_value} for {self.team.name} in {self.session.name}"