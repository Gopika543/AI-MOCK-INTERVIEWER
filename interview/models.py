from django.db import models

# Create your models here.


class Question(models.Model):
    text = models.TextField()

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
