from datetime import timedelta
from rest_framework import serializers
from .models import Client, Service, Issue, Subscription, Ticket, Availability, VerificationCode
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'user', 'phone_number', 'email', 'activated')

class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = ('code', 'client', 'created_at')
        read_only_fields = ('created_at',)

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'description', 'address')


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ('id', 'service', 'name', 'duration')


class AvailabilitySerializer(serializers.ModelSerializer):
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = Availability
        fields = ['id', 'issue', 'start_time', 'end_time', 'is_available', 'is_free']

    def get_end_time(self, obj):
        # Assurez-vous que l'objet issue a une durée définie
        if obj.issue.duration:
            return obj.start_time + timedelta(minutes=obj.issue.duration)
        return None

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'client', 'start_date', 'end_date', 'active')


class TicketSerializer(serializers.ModelSerializer):
    # Here we'll use `StringRelatedField` to show the string representation of the related model
    client = serializers.StringRelatedField(read_only=True)
    issue = IssueSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ('id', 'client', 'availability', 'scheduled_time', 'status')

    def create(self, validated_data):
        # We need to get the issue object based on the passed issue ID
        availability_id = self.context['request'].data.get('availability')
        availability = Issue.objects.get(id=availability_id)

        # We retrieve the client from the context (this should be set in the view)
        client = self.context['request'].user.client

        # Now we create the Ticket instance
        ticket = Ticket.objects.create(
            client=client,
            availability=availability,
            scheduled_time=validated_data.get('scheduled_time'),
            status=validated_data.get('status', 'pending')
        )

        return ticket
