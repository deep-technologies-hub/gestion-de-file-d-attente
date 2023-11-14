from django.contrib import admin
from .models import Client, Service, Issue, Subscription, Ticket, Availability

admin.site.register(Client)
admin.site.register(Service)
admin.site.register(Issue)
admin.site.register(Availability)
admin.site.register(Subscription)
admin.site.register(Ticket)