from django.db import models

# Create your models here.


class Form(models.Model):
    name = models.CharField(max_length=255)

class FormField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('password', 'Password'),
        ('Email','Email')
    ]

    label = models.CharField(max_length=255)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)
    order = models.PositiveIntegerField(default=0)
    form = models.ForeignKey(Form, related_name='fields', on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['order']


class FormSubmission(models.Model):
    form = models.ForeignKey(Form, related_name='submissions', on_delete=models.CASCADE)
    submitted_data = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)
