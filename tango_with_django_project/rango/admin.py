from django.contrib import admin

# Register your models here.
from rango.models import Category, Page


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')


# ДОбавляем этот класс, чтобы изменить интерфейс администратора
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


# Обновляем регистрацию, чтобы она включала этот измененный интерфейс
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
