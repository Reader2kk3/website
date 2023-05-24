import email
import profile
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField("Имя", max_length=200, blank=True, null=True)
    email = models.EmailField("Почта", max_length=500, blank=True, null=True)
    username = models.CharField("Никнейм", max_length=200, blank=True, null=True)
    location = models.CharField("Страна", max_length=200, blank=True, null=True)
    short_intro = models.CharField("Короткая информация", max_length=200, blank=True, null=True)
    bio = models.TextField("Биография", blank=True, null=True)
    profile_image = models.ImageField("Изображение", null=True, blank=True, upload_to='profiles/', default="profiles/user-default.jpg")
    social_github = models.CharField("Github", max_length=200, blank=True, null=True)
    social_twitter = models.CharField("Twitter", max_length=200, blank=True, null=True)
    social_linkedin = models.CharField("Linkedin", max_length=200, blank=True, null=True)
    social_youtube = models.CharField("Youtube", max_length=200, blank=True, null=True)
    social_website = models.CharField("Website", max_length=200, blank=True, null=True)
    creared = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4,unique=True,
                        primary_key=True,editable=False)

    def __str__(self):
        return str(self.username)

    class Meta:
        ordering = ['creared']

    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''
        return url


class Skill(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField("Название", max_length=200, blank=True, null=True)
    description = models.TextField("Описание", null=True, blank=True)
    creared = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4,unique=True,
                        primary_key=True,editable=False)

    def __str__(self):
        return str(self.name)



class Message(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    recipient = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="messages")
    name = models.CharField("Пользователь", max_length=200, null=True, blank=True)
    email = models.EmailField("Почта", max_length=200, null=True, blank=True)
    subject = models.CharField("Заголовок", max_length=200, null=True, blank=True)
    body = models.TextField("Текст")
    is_read = models.BooleanField("Прочитал", default=False, null=True)
    creared = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4,unique=True,
                        primary_key=True,editable=False)

    def __str__(self):
        return self.subject

    class Meta:
        ordering = ['is_read', '-creared']






