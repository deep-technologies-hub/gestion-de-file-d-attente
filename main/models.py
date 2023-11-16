from django.db import models
from datetime import timedelta
from django.utils import timezone
import datetime

class Service(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    description = models.TextField()

    def __str__(self):
        return self.name

class Client(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=100)
    activated = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class VerificationCode(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        # Le code expire après 1 heure (ou le délai que vous souhaitez)
        return self.created_at + datetime.timedelta(minutes=5) < timezone.now()


class Issue(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='issues')
    name = models.CharField(max_length=255)
    duration = models.DurationField(default=timedelta(minutes=30))

    def __str__(self):
        return f"{self.service.name} - {self.name}"

class Availability(models.Model):
    issue = models.ForeignKey('Issue', on_delete=models.CASCADE, related_name='availabilities')
    start_time = models.DateTimeField('start time')
    end_time = models.DateTimeField('end time', blank=True, null=True)
    is_available = models.BooleanField('is available', default=True)
    is_free = models.BooleanField('is free', default=True)

    class Meta:
        verbose_name = 'availability'
        verbose_name_plural = 'availabilities'

    def save(self, *args, **kwargs):
        # Vérifiez si la durée est définie sur l'objet `Issue` lié
        if self.issue.duration:
            # Calculez l'heure de fin en ajoutant la durée à l'heure de début
            self.end_time = self.start_time + timedelta(minutes=self.issue.duration)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.issue.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

class Ticket(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='tickets')
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, related_name='tickets')
    status = models.CharField(max_length=100, default='pending')  # Exemples: pending, confirmed, completed

    def __str__(self):
        return f"{self.client.user.username} - {self.availability.service.name}"

class Subscription(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.client.user.username} Subscription"
