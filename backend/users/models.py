from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import F, Q, UniqueConstraint

from utils.constants import EMAIL_LENGHT, NAME_MAX_LENGHT


class User(AbstractUser):
    """ Модель пользователя. """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', )
    first_name = models.CharField(verbose_name='Имя',
                                  max_length=NAME_MAX_LENGHT)
    last_name = models.CharField(max_length=NAME_MAX_LENGHT,
                                 verbose_name='Фамилия')
    email = models.EmailField(
        max_length=EMAIL_LENGHT,
        verbose_name='email',
        unique=True)
    username = models.CharField(
        verbose_name='username',
        max_length=NAME_MAX_LENGHT,
        unique=True,
        validators=(UnicodeUsernameValidator(), )
    )

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.username}'


class Follow(models.Model):
    """ Модель подписки на автора. """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='following'
    )

    class Meta:
        ordering = ('-id', )
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='no_self_follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
