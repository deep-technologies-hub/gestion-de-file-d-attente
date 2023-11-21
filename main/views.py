from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status, views
import random
from django.core.mail import send_mail
from .models import Client, Service, Issue, Subscription, Ticket, VerificationCode, Availability
from .serializers import ClientSerializer, ServiceSerializer, IssueSerializer, SubscriptionSerializer, TicketSerializer, UserSerializer, AvailabilitySerializer
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth.models import User

class RegisterView(views.APIView):
    def post(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.is_active = True
            user = user_serializer.save()
            client = Client.objects.create(user=user, phone_number=request.data['phone_number'], email=request.data['email'],activated=False)
            # Générer un code de vérification
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            VerificationCode.objects.create(client=client, code=code)
            # Envoyer le code par email (à implémenter selon votre méthode d'envoi d'email)
            send_mail(
                'Votre code de vérification',
                f'Votre code de vérification est: {code}',
                'msakande21@gmail.com',
                [client.email],
                fail_silently=False,
            )
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeView(views.APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        code = request.data.get('code')

        try:
            user = User.objects.get(username=username)
            verification_query = VerificationCode.objects.filter(client__user=user, code=code, created_at__gte=timezone.now() - timezone.timedelta(minutes=5))

            if verification_query.exists():
                verification = verification_query.first()
                user.client.activated=True
                user.save()
                verification.delete()  # Supprimer le code après utilisation
                return Response({'message': 'Compte activé avec succès.'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'Code invalide ou expiré, ou email incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

class ResendCodeView(views.APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')

        try:
            user = User.objects.get(username=username)
            email = user.client.email
            # Supprimer l'ancien code s'il existe
            VerificationCode.objects.filter(client__user=user).delete()

            # Générer un nouveau code
            new_code = random.randint(100000, 999999)
            VerificationCode.objects.create(client=user.client, code=new_code)

            # Envoyer le code par email
            send_mail(
                'Votre code de vérification',
                f'Voici votre code de vérification : {new_code}',
                'msakande21@gmail.com',  # Remplacer par votre adresse email d'envoi
                [email],
                fail_silently=False,
            )

            return Response({'message': 'Un nouveau code de vérification a été envoyé.'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'Aucun utilisateur avec ce username n’a été trouvé.'}, status=status.HTTP_404_NOT_FOUND)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    #permission_classes = [permissions.IsAuthenticated]

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    #permission_classes = [permissions.IsAuthenticated]

class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    #permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Issue.objects.all()
        service = self.request.query_params.get('service')
        if service is not None:
            queryset = queryset.filter(service=service)
        return queryset

class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer

    def get_queryset(self):
        queryset = Availability.objects.all()
        issue = self.request.query_params.get('issue')
        if issue is not None:
            queryset = queryset.filter(issue=issue)
        return queryset

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    #permission_classes = [permissions.IsAuthenticated]

    # def get_queryset(self):
    #     """
    #     Optionally restricts the returned subscriptions to the logged in user,
    #     by filtering against the user's client profile.
    #     """
    #     user = self.request.user
    #     if user.is_authenticated:
    #         return Subscription.objects.filter(client__user=user)
    #     return Subscription.objects.none()

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    #permission_classes = [permissions.IsAuthenticated]

    # def get_queryset(self):
    #     """
    #     Optionally restricts the returned tickets to the logged in user,
    #     by filtering against the user's client profile.
    #     """
    #     user = self.request.user
    #     if user.is_authenticated:
    #         return Ticket.objects.filter(client__user=user)
    #     return Ticket.objects.none()

    # def perform_create(self, serializer):
    #     """
    #     Create a new ticket, ensuring that the client has an active subscription.
    #     """
    #     client = self.request.user.client
    #     if Subscription.objects.filter(client=client, active=True).exists():
    #         serializer.save(client=client)
    #     else:
    #         return Response(
    #             {"error": "No active subscription found for this user."},
    #             status=status.HTTP_403_FORBIDDEN
    #         )

class SendEmailView(APIView):
    def post(self, request, *args, **kwargs):
        subject = request.data.get('subject', 'test')
        message = request.data.get('message', 'yes')
        from_email = 'msakande21@gmail.com'  # Votre adresse e-mail configurée
        to_email = request.data.get('to_email','shunikiema@gmail.com')

        if not to_email:
            return JsonResponse({'error': 'Adresse e-mail destinataire manquante.'}, status=400)

        try:
            send_mail(subject, message, from_email, [to_email])
            return JsonResponse({'success': 'E-mail envoyé avec succès.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)