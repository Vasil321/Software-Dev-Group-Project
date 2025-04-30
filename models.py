from django.db import models
from django.contrib.auth.models import User

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Who voted
    session = models.ForeignKey('HealthCheckSession', on_delete=models.CASCADE)  # Which session
    team = models.ForeignKey('Team', on_delete=models.CASCADE)  # Which team
    vote_value = models.IntegerField()  # The actual vote (e.g. 1–10 scale)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"{self.user.username} voted {self.vote_value} for {self.team.name} in {self.session.name}"