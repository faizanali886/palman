from rest_framework import generics, status
from rest_framework.response import Response
from .models import User, Bot, Moderator
from .serializers import UserSerializer, BotSerializer, ModeratorSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate


class AdminRegistrationAPIView(generics.CreateAPIView):
    queryset = Moderator.objects.all()
    serializer_class = ModeratorSerializer

class AdminLoginAPIView(generics.CreateAPIView):
    serializer_class = ModeratorSerializer

    def create(self, request, *args, **kwargs):
        userName = request.data.get('username')
        password = request.data.get('password')

        admin = authenticate(username=userName, password=password)
        if admin:
            token, created = Token.objects.get_or_create(user=admin)
            return Response({'token': token.key, 'email': admin.email, 'userName': admin.username})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class AdminDetailAPIView(generics.RetrieveAPIView):
    queryset =  Moderator.objects.all()
    serializer_class = ModeratorSerializer

    def get_object(self):
        return self.request.user


class BotListCreateAPIView(generics.ListCreateAPIView):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer

class BotDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer
    lookup_field = 'botid'

class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CheckUserExistsAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        number = self.kwargs['number']
        try:
            user = User.objects.get(number=number)
            serializer = self.serializer_class(user)
            return Response({'exists': 'yes', 'user_data': serializer.data})
        except User.DoesNotExist:
            return Response({'exists': 'no'})
        


class AssignBotToUserAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        bot_id = self.kwargs['bot_id']

        try:
            bot = Bot.objects.get(botid=bot_id)
        except Bot.DoesNotExist:
            return Response({'error': 'Bot does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if bot.maxUser >= 50:
            return Response({'error': 'Bot cannot be assigned to more users.'}, status=status.HTTP_400_BAD_REQUEST)

        
        if instance.botid:
            return Response({'error': 'User already has a bot assigned.'}, status=status.HTTP_400_BAD_REQUEST)

        
        instance.botid = bot.id
        instance.save()

       
        bot.maxUser += 1
        bot.save()

        return Response({'message': f'Bot {bot.botNumber} assigned to user {instance.name}.', 'bot_id': bot.id})
