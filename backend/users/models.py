from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from rest_framework.exceptions import ValidationError


class User(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'
    ROLES = [
        (ADMIN, 'Administrator'),
        (USER, 'User'),
    ]
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=60
    )
    username = models.CharField(
        verbose_name='Логин',
        max_length=30,
        null=False,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='В имени пользователя недопустимые символы'
        )]

    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=50
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=50
    )
    role = models.CharField(
        max_length=50,
        choices=ROLES,
        default=USER,
        verbose_name='Роль')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        ordering = ['id']
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
        null=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        null=True,
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
