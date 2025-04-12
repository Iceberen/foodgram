from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.settings import MAX_LENTGHT_EMAIL, MAX_LENTHG_NAME


class User(AbstractUser):
    """Кастомная модель пользователя"""

    email = models.EmailField(
        verbose_name='Email',
        max_length=MAX_LENTGHT_EMAIL,
        unique=True
    )
    username = models.CharField(
        verbose_name='Никнейм',
        max_length=MAX_LENTHG_NAME,
        unique=True,
        validators=(UnicodeUsernameValidator(),),
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LENTHG_NAME,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LENTHG_NAME,
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='avatars/',
        null=True,
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
