from django.db import models

from django.contrib.auth.models import User

class Message(models.Model):
	source = models.ForeignKey(User, on_delete=models.CASCADE, related_name='source')
	target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='target')
	content = models.TextField()
	time = models.DateTimeField(auto_now_add=True)


#python manage.py sqlmigrate polls 0001

