from rest_framework import serializers
from .models import User, Bot, Moderator
import phonenumbers
from .function import get_country_name_from_country_code
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


class ModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moderator
        fields = ('id', 'email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        admin = Moderator(
            email=validated_data['email'],
            username=validated_data['username']
        )
        admin.set_password(validated_data['password'])
        admin.save()
        Token.objects.create(user=admin)
        return admin

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance

class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = '__all__'

    def validate_botid(self, value):
        """
        Custom validation to ensure uniqueness of botid when updating an existing bot.
        """
        instance = self.instance
        if instance and Bot.objects.filter(botid=value).exclude(id=instance.id).exists():
            raise serializers.ValidationError("Bot with this botid already exists.")
        return value




class UserSerializer(serializers.ModelSerializer):

    bot = BotSerializer(read_only=True)
    class Meta:
        model = User
        fields = '__all__'

    def validate(self, data):
        existing_user_by_number = User.objects.filter(number=data.get('number')).exclude(pk=self.instance.pk if self.instance else None).first()
        #existing_user_by_name = User.objects.filter(name=data.get('name')).exclude(pk=self.instance.pk if self.instance else None).first()

        if existing_user_by_number:
            if self.instance and self.instance.number == data.get('number'):
                
                pass
            else:
                raise serializers.ValidationError({'number': 'A user with this number already exists.'})

        """ if existing_user_by_name:
            if self.instance and self.instance.name == data.get('name'):
                
                pass
            else:
                raise serializers.ValidationError({'name': 'A user with this name already exists.'}) """

        return data
    
    def save(self, **kwargs):
        number = self.validated_data.get('number')
        
        
        if 'number' in self.validated_data:
            try:
                parsed_number = phonenumbers.parse(number, None)
                country_code = phonenumbers.region_code_for_number(parsed_number)
            except Exception as e:
                country_code = None

            if country_code:
                country_info = get_country_name_from_country_code(country_code)
            else:
                country_info = "Can't Identify"  
        else:
            
            country_info = self.instance.location if self.instance else None

        self.validated_data['location'] = country_info

        return super().save(**kwargs)

    """ def save(self, **kwargs):
        number = self.validated_data.get('number')

        
        try:
            parsed_number = phonenumbers.parse(number, None)
            country_code = phonenumbers.region_code_for_number(parsed_number)
        except Exception as e:
            country_code = None

        if country_code:
            
            country_info = get_country_name_from_country_code(country_code)
        else:
            country_info = "Can't Identify"  # Set country to "Can't Identify" if the code cannot be extracted

        self.validated_data['location'] = country_info

        return super().save(**kwargs) """