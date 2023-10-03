from django.db import models
from django.utils import timezone
import phonenumbers
from .function import get_country_name_from_country_code
from django.contrib.auth.models import AbstractUser


class Moderator(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.username


class Bot(models.Model):
    apiSecret = models.CharField(max_length=255)
    botid = models.PositiveIntegerField(unique=True)
    botNumber = models.CharField(max_length=15)
    botLanguage = models.CharField(max_length=255, blank=True)
    botSpeaker = models.CharField(max_length=255)
    maxUser = models.PositiveIntegerField(default=0)
    phone = models.CharField(max_length=15)
    id = models.AutoField(primary_key=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        
        bot_choices = [(bot.botid, bot.botid) for bot in Bot.objects.filter(maxUser__lt=50)]
        User.BOT_CHOICES = bot_choices
        User._meta.get_field('botid').choices = bot_choices
    


    def __str__(self):
        return 'BotID: '+ str(self.botid)

class User(models.Model):

    STATUS_CHOICES = [
        ('freetrial', 'Free Trial'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blocked', 'Blocked'),
    ]

    #BOT_CHOICES = [(bot.id, bot.botid, bot.botNumber) for bot in Bot.objects.all()]
    BOT_CHOICES = [(bot.botid, bot.botid) for bot in Bot.objects.all()]

    
    number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    consumed_credits = models.DurationField(default=timezone.timedelta(seconds=0))
    initial_credits = models.DurationField(default=timezone.timedelta(seconds=0))
    remaining_credits = models.DurationField(default=timezone.timedelta(seconds=0))
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='inactive')
    location = models.CharField(max_length=100, blank=True)
    botid = models.PositiveIntegerField(choices=BOT_CHOICES, null=True, blank=True)
    """ botid = models.PositiveIntegerField( null=True, blank=True) """
    
    #botid = models.PositiveIntegerField(null=True, blank=True)

    def find_country(self):
        try:
            parsed_number = phonenumbers.parse(self.number, None)
            country_code = phonenumbers.region_code_for_number(parsed_number)
        except phonenumbers.phonenumberutil.NumberFormatException:
            country_code = None

        if country_code:
            
            country_info = get_country_name_from_country_code(country_code)
        else:
            country_info = "Can't Identify"
        return country_info

    def save(self, *args, **kwargs):

        if self.botid:
            try:
                bot = Bot.objects.get(botid=self.botid)
                bot.maxUser += 1
                bot.save()
            except Bot.DoesNotExist:
                pass



        if not self.pk:
            
            self.remaining_credits = self.initial_credits
        else:
            
            self.remaining_credits = self.initial_credits - self.consumed_credits
        
        if self.remaining_credits <= timezone.timedelta(seconds=0):
            self.status = 'inactive'
        else:
            self.status = 'freetrial'

        if not self.location:
            self.location = self.find_country()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Registered User"
        verbose_name_plural = "Registered Users"