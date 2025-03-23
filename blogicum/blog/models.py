"""Файл для создания таблиц базы данных."""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


from core.models import PublishedModel

User = get_user_model()

LENGTH_TITLE = LENGTH_NAME = 256


class Category(PublishedModel):
    """Класс, создающий таблицу Категория."""

    title = models.CharField('Заголовок', max_length=LENGTH_TITLE, blank=False)
    description = models.TextField('Описание', blank=False)
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=(
            "Идентификатор страницы для URL; разрешены символы латиницы, "
            "цифры, дефис и подчёркивание."
        ),

    )

    class Meta:
        """Абстрактный класс Meta."""

        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """Магический метод str."""
        return self.title


class Location(PublishedModel):
    """Класс, создающий таблицу Локация."""

    name = models.CharField(
        'Название места', max_length=LENGTH_NAME, blank=False
    )

    class Meta:
        """Абстрактный класс Meta."""

        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        """Магический метод str."""
        return self.name


class Post(PublishedModel):
    """Класс, создающий таблицу Пост."""

    title = models.CharField('Заголовок', max_length=LENGTH_TITLE, blank=False)
    text = models.TextField('Текст', blank=False)
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        blank=False,
        default=timezone.now,
        help_text=(
            "Если установить дату и время в будущем — "
            "можно делать отложенные публикации."
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )
    image = models.ImageField('Фото', upload_to='posts_images', blank=True)

    class Meta:
        """Абстрактный класс Meta."""

        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        """Магический метод str."""
        return self.title

class Comment(models.Model):
    text = models.TextField('Комментарий к посту')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True,)
    created_at = models.DateTimeField(auto_now_add=True)