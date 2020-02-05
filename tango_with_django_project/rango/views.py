from django.shortcuts import render

from django.http import HttpResponse


def index(request):
    # Создаем словарь, чтобы передать шаблону в качестве содержимого.
    # Заметьте, что ключ boldmessage называется так же как и переменная {{ boldmessage }} в шаблоне!
    context_dict = {'boldmessage': "I am bold font from the context"}

    # Возвращает ответ, полученный с помощью шаблона, который посылается клиенту.
    # Для упрощения нашей работы мы используем следующую функцию.
    # Заметьте, что первый параметр - это шаблон, который мы хотим использовать.

    return render(request, 'rango/index.html', context_dict)


def about(request):
    return HttpResponse("Rango says here is the about page. <br/> <a href='/rango/'>Index</a> ")
