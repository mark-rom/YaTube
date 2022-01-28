from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.fields import (
    CharField, DateTimeField, SlugField, TextField
)
from django.db.models.fields.related import ForeignKey

User = get_user_model()


class Group(models.Model):
    """The Group class describes the structure of Yatube groups.
    It has the next attributes: title, slug, description.
    """
    title = CharField('Название группы', max_length=200)
    slug = SlugField('Уникальный урл', unique=True)
    description = TextField('Описание группы', max_length=300)

    class Meta:
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        """This function returns title attribute of Group.
        """
        return self.title


class Post(models.Model):
    """The Post class describes the structure of posts on Yatube.
    It has the next attributes: text, pub_date, author, group.
    """
    text = TextField(
        'Текст поста',
        help_text='Текст нового поста',
    )
    pub_date = DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )
    author = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    post = ForeignKey(
        Post,
        related_name='comments',
        verbose_name='Публикация',
        on_delete=models.CASCADE,
    )
    author = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = TextField(
        'Текст комментария',
        help_text='Текст комментария',
    )
    created = DateTimeField(
        'Дата публикации комментария',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text


class Follow(models.Model):
    user = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Контентмейкер'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='Уникальная подписка'
            )
        ]
