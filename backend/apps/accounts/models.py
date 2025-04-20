from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from foodgram.settings import MAX_LENTGHT_EMAIL, MAX_LENTHG_NAME


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
    REQUIRED_FIELDS = ['username', ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписок."""
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    target = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'target'],
                name='unique_subscription')]

    def __str__(self):
        return f'{self.subscriber.username} подписан на {self.target.username}'

    def clean(self):
        if self.subscriber == self.target:
            raise ValidationError('Нельзя подписаться на самого себя')
