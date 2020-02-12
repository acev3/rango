from django.shortcuts import render
from rango.models import Category, Page
from django.http import HttpResponse
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime

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
    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...прибавляем единицу к предыдущему значению cookie...
            visits = visits + 1
            # ...и обновляем cookie last visit cookie.
            reset_last_visit_time = True
    else:
        # Cookie last_visit не существует, поэтому создаём его для текущей даты/времени.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits

    response = render(request, 'rango/index.html', context_dict)

    return response


def about(request):
    # Если существует переменная сессии visits, то считать и использовать её.
    # Если нет, то пользователь не посещало сайт, поэтому присваиваем ей нулевое значение.
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    return render(request, 'rango/about.html', {'visits': count})



def category(request, category_name_slug):
    # Создаем словарь контекста, который мы можем передать механизму обработки шаблонов.
    context_dict = {}

    try:
        # Можем ли мы найти название категории с дефисами для заданного названия?
        # Если нет, метод .get() вызывает исключение DoesNotExist.
        # Итак метод .get() возвращает экземпляр модели или вызывает исключение.
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        context_dict['category_name_slug'] = category.slug
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

@login_required
def add_category(request):
    # HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Все поля формы были заполнены правильно?
        if form.is_valid():
            # Сохранить новую категорию в базе данных.
            form.save(commit=True)

            # Теперь вызвать предсталвение index().
            # Пользователю будет показана главная страница.
            return index(request)
        else:
            # Обрабатываемая форма содержит ошибки - вывести их в терминал.
            print(form.errors)
    else:
        # Если запрос был не POST, вывести форму, чтобы можно было ввести в неё данные.
        form = CategoryForm()

    # Форма с ошибкой (или ошибка с данных), форма не была получена...
    # Вывести форму с сообщениями об ошибках (если они были).
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
                cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # вероятно здесь лучше использовать redirect.
                return category(request, category_name_slug)
        else:
            print(form.errors)
    else:
        form = PageForm()

    context_dict = {'form': form, 'category': cat,  'category_name_slug': category_name_slug}

    return render(request, 'rango/add_page.html', context_dict)

def register(request):
    # Логическое значение указывающее шаблону прошла ли регистрация успешно.
    # В начале ему присвоено значение False. Код изменяет значение на True, если регистрация прошла успешно.
    registered = False

    # Если это HTTP POST, мы заинтересованы в обработке данных формы.
    if request.method == 'POST':
        # Попытка извлечь необработанную информацию из формы.
        # Заметьте, что мы используем UserForm и UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # Если в две формы введены правильные данные...
        if user_form.is_valid() and profile_form.is_valid():
            # Сохранение данных формы с информацией о пользователе в базу данных.
            user = user_form.save()

            # Теперь мы хэшируем пароль с помощью метода set_password.
            # После хэширования мы можем обновить объект "пользователь".
            user.set_password(user.password)
            user.save()

            # Теперь разберемся с экземпляром UserProfile.
            # Поскольку мы должны сами назначить атрибут пользователя, необходимо приравнять commit=False.
            # Это отложит сохранение модели, чтобы избежать проблем целостности.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Предоставил ли пользователь изображение для профиля?
            # Если да, необходимо извлечь его из формы и поместить в модель UserProfile.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Теперь мы сохраним экземпляр модели UserProfile.
            profile.save()

            # Обновляем нашу переменную, чтобы указать, что регистрация прошла успешно.
            registered = True

        # Неправильная формы или формы - ошибки или ещё какая-нибудь проблема?
        # Вывести проблемы в терминал.
        # Они будут также показаны пользователю.
        else:
            print(user_form.errors, profile_form.errors)

    # Не HTTP POST запрос, следователь мы выводим нашу форму, используя два экземпляра ModelForm.
    # Эти формы будут не заполненными и готовы к вводу данных от пользователя.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Выводим шаблон в зависимости от контекста.
    return render(request,
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered} )


def user_login(request):

    # Если запрос HTTP POST, пытаемся извлечь нужную информацию.
    if request.method == 'POST':
        # Получаем имя пользователя и пароль, вводимые пользователем.
        # Эта информация извлекается из формы входа в систему.
                # Мы используем request.POST.get('<имя переменной>') вместо request.POST['<имя переменной>'],
                # потому что request.POST.get('<имя переменной>') вернет None, если значения не существует,
                # тогда как request.POST['<variable>'] создаст исключение, связанное с отсутствем значения с таким ключом
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Используйте Django, чтобы проверить является ли правильным
        # сочетание имя пользователя/пароль - если да, то возвращается объект User.
        user = authenticate(username=username, password=password)

        # Если мы получили объект User, то данные верны.
        # Если получено None (так Python представляет отсутствие значения), то пользователь
        # с такими учетными данными не был найден.
        if user:
            # Аккаунт активен? Он может быть отключен.
            if user.is_active:
                # Если учетные данные верны и аккаунт активен, мы можем позволить пользователю войти в систему.
                # Мы возвращаем его обратно на главную страницу.
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # Использовался не активный аккуант - запретить вход!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Были введены неверные данные для входа. Из-за этого вход в систему не возможен.
            print ("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    # Запрос не HTTP POST, поэтому выводим форму для входа в систему.
    # В этом случае скорее всего использовался HTTP GET запрос.
    else:
        # Ни одна переменная контекста не передается в систему шаблонов, следовательно, используется
        # объект пустого словаря...
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
    # Поскольку мы знаем, что только вошедшие в систему пользователи имеют доступ к этому представлению, можно осуществить выход из системы
    logout(request)

    # Перенаправляем пользователя обратно на главную страницу.
    return HttpResponseRedirect('/rango/')