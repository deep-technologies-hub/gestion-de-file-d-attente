from datetime import timedelta
from rest_framework import serializers
from .models import Client, Service, Issue, Subscription, Ticket, Availability, VerificationCode
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Effectuer la validation standard d'abord
        data = super().validate(attrs)

        # Vérifier si le profil client de l'utilisateur est validé
        user = self.user
        if hasattr(user, 'client') and not user.client.validated:
            raise AuthenticationFailed('Le compte client n’est pas validé.')

        return data


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
    formatted_duration = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = ('id', 'service', 'name', 'duration', 'formatted_duration')

    def get_formatted_duration(self, obj):
        # Convertir timedelta en total de minutes
        total_minutes = obj.duration.total_seconds() // 60
        minutes = int(total_minutes)
        return f"{minutes}min"


class AvailabilitySerializer(serializers.ModelSerializer):
    formatted_duration = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = Availability
        fields = ['id', 'issue', 'start_time', 'formatted_start_time', 'is_available', 'is_free']

    def get_formatted_start_time(self, obj):
        # Liste des mois en français
        mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

        # Calculer l'heure de fin
        duration_in_minutes = obj.issue.duration.total_seconds() / 60
        end_time = obj.start_time + timedelta(minutes=duration_in_minutes)

        # Format start_time en utilisant la liste des mois
        start_month = mois[obj.start_time.month - 1]
        formatted_start_time = f"{obj.start_time.day} {start_month} de {obj.start_time.strftime('%H:%M')} à {end_time.strftime('%H:%M')}"

        return formatted_start_time


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'client', 'start_date', 'end_date', 'active')


class TicketSerializer(serializers.ModelSerializer):
    # Here we'll use `StringRelatedField` to show the string representation of the related model
    # client = serializers.StringRelatedField(read_only=True)
    # availability = AvailabilitySerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ('id', 'client', 'availability', 'status')

    # def create(self, validated_data):
    #     # We need to get the issue object based on the passed issue ID
    #     availability_id = self.context['request'].data.get('availability')
    #     availability = Availability.objects.get(id=availability_id)

    # We retrieve the client from the context (this should be set in the view)
    # client = self.client

    # client_id = self.context['request'].data.get('client')
    # client = Client.objects.get(id=client_id)
    # # client = self.context['request'].user.client
    #
    # # Now we create the Ticket instance
    # ticket = Ticket.objects.create(
    #     client=client,
    #     availability=availability,
    #     scheduled_time=validated_data.get('scheduled_time'),
    #     status=validated_data.get('status', 'pending')
    # )

    # return ticket
