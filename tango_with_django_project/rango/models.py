from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(default=None)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):  # For Python 2, use __unicode__ too
        return self.name


class Page(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, )
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __str__(self):  # For Python 2, use __unicode__ too
        return self.title


class UserProfile(models.Model):
    # Эта строка обязательна. Она связывает UserProfile с экземпляром модели User.
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Дополнительные атрибуты, которые мы хотим добавить.
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Переопределяем метод __unicode__(), чтобы вернуть что-либо значимое! Используйте __str__() в Python 3.*
    def __str__(self):
        return self.user.username