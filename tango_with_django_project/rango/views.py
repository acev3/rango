from django.shortcuts import render
from rango.models import Category, Page
from django.http import HttpResponse

"""
def index(request):
    # Создаем словарь, чтобы передать шаблону в качестве содержимого.
    # Заметьте, что ключ boldmessage называется так же как и переменная {{ boldmessage }} в шаблоне!
    context_dict = {'boldmessage': "I am bold font from the context"}

    # Возвращает ответ, полученный с помощью шаблона, который посылается клиенту.
    # Для упрощения нашей работы мы используем следующую функцию.
    # Заметьте, что первый параметр - это шаблон, который мы хотим использовать.

    return render(request, 'rango/index.html', context_dict)
"""


def index(request):
    # Осуществляем запрос к базе данных для получения списках ВСЕХ категорий, хранящихся в ней на текущий момент.
    # Упорядочиваем категории по количеству лайков в порядке убывания.
    # Извлекаем только первые 5 - или все, если их число меньше 5.
    # Помещаем список в наш словарь контекста, который будет передан механизму шаблонов.
    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list}
    context_dict['pages'] = pages_list
    # Формируем ответ для клиента по шаблону и отправляем обратно!
    return render(request, 'rango/index.html', context_dict)


def about(request):
    return HttpResponse("Rango says here is the about page. <br/> <a href='/rango/'>Index</a> ")


def category(request, category_name_slug):
    # Создаем словарь контекста, который мы можем передать механизму обработки шаблонов.
    context_dict = {}

    try:
        # Можем ли мы найти название категории с дефисами для заданного названия?
        # Если нет, метод .get() вызывает исключение DoesNotExist.
        # Итак метод .get() возвращает экземпляр модели или вызывает исключение.
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        # Получит ьвсе связанные страницы.
        # Заметьте, что фильтр возвращает >= 1 экземпляр модели.
        pages = Page.objects.filter(category=category)

        # Добавить наш список результатов к контексту модели под названием pages ("страницы").
        context_dict['pages'] = pages
        # Мы также добавWe объект категории из базы данных в словарь контекста.
        # Мы будем использовать это информацию в шаблоне, чтобы проверить, что категория существует.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # Мы попадаем сюда, если не нашли указанной категории.
        # Ничего делать не надо - шаблон отобразить сообщение "Нет такой категории" вместо нас.
        pass

    # Возврщаем ответ на запрос клиенту.
    return render(request, 'rango/category.html', context_dict)
