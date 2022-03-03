from django.contrib.auth import get_user_model
from django.db import models
# from django.utils import timezone

STRING_LEN = 15

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Название сообщества", max_length=200)
    slug = models.SlugField("Название сообщества для url", unique=True)
    description = models.TextField("Описание сообщества")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField("Текст поста", blank=False)
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    # , default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name="Автор поста")
    group = models.ForeignKey(Group, on_delete=models.CASCADE,
                              related_name="posts", blank=True, null=True,
                              verbose_name="Название сообщества")

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:STRING_LEN]
