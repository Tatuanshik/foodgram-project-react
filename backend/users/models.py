from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import ValidationError


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True, max_length=60
    )
    username = models.CharField(
        verbose_name='Логин',
        max_length=30
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=50
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=50
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=50
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'username'],
                name='unique_user'
            )
        ]

    def __str__(self):
        return self.username


class Followers(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписчика'
        verbose_name_plural = 'Подписчиков'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follower')
        ]

    def clean(self):
        if self.user.id == self.author.id:
            raise ValidationError('Нельзя подписаться на самого себя!')

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
