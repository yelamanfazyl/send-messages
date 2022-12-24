from django.db import models

# Create your models here.
class Message(models.Model):
    message = models.TextField()
    send_date = models.DateTimeField('date published')
    is_sent = models.BooleanField(default=False) 

    def __str__(self):
        return self.message
        