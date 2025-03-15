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
