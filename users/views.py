from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from.utils import searchProfiles, paginateProfiles

# Вход в систему
def loginUser(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == 'POST':
        username = request.POST['username'].lower()         # lower() - переводит сроку в нижний регистр
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)      # get(): получает один объект модели
        except:
            messages.error(request, 'Имя пользователя не существует!')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'account')
        else:
            messages.error(request,'Вы ввели неправильно логин или пароль!')

    return render(request, 'users/login_register.html')

# Выход с ситемы
def logoutUser(request):
    logout(request)
    messages.info(request, 'Пользователь вышел из системы!')
    return redirect('login')

# Регистрация
def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)      # commit=False - вернет объект, который еще не был сохранен в БД.
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'Учетная запись пользователя создана!')

            login(request, user)
            return redirect('edit-account')
        else:
            messages.success(request, 'При регистрации произошла ошибка!')

    context = {'page': page, 'form': form}
    return render(request, 'users/login_register.html', context)

# Поиск профиля и пагинатор
def profiles(request):
    profiles, search_query = searchProfiles(request)

    custom_range, profiles = paginateProfiles(request, profiles, 12)

    context = {'profiles': profiles, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'users/profiles.html', context)


def userProfile(request, pk):
    profile = Profile.objects.get(id=pk)

    topSkills = profile.skill_set.exclude(description__exact="")
    otherSkills = profile.skill_set.filter(description="")

    # _set - чтобы получить ссылку на объект записи первичной модели. А, затем, 
    # используя механизм обратного связывания, прочитаем все связанные с данной категорией посты.

    # exclude(): получает набор объектов модели, которые НЕ соответствуют условию.
    # exact выбирает все объекты моделей, в которых свойство равно определенному значению
    # description__exact="" - обязательный параметр

    # filter(): получает набор объектов модели, которые соответствуют условию.

    context = {'profile': profile,'topSkills': topSkills,'otherSkills': otherSkills }
    return render(request, 'users/user-profile.html', context)

# Старица аккаунта
@login_required(login_url='login')
def userAccount(request):
    profile = request.user.profile

    skills = profile.skill_set.all()
    projects = profile.project_set.all()

    context = {'profile': profile, 'skills': skills, 'projects': projects}
    return render(request, 'users/account.html', context)

# Редактирование аккаунта
@login_required(login_url='login')
def editAccount(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)   # Из запроса берется файл (request.FILES)
        if form.is_valid():
            form.save()

            return redirect('account')

    context = {'form': form}
    return render(request, 'users/profile_form.html', context)

# Создание навыков/скиллов
@login_required(login_url='login')
def createSkill(request):
    profile = request.user.profile
    form = SkillForm()

    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, 'Навык успешно добавлен!')
            return redirect('account')

    context = {'form': form}
    return render(request, 'users/skill_form.html', context)

# Обновление навыков/скиллов
@login_required(login_url='login')
def updateSkill(request, pk):
    profile = request.user.profile                      # Проверка авторизации
    skill = profile.skill_set.get(id=pk)                # берем все элементы модели Skill, и вытаскиваем 1 элемент
    form = SkillForm(instance=skill)

    if request.method == 'POST':                        # Метод отправки - Post
        form = SkillForm(request.POST, instance=skill)  # instance - передает информацию в форму
        if form.is_valid():                             # Проверка на валидность
            form.save()                                 # Сохраняем 
            messages.success(request, 'Навык успешно обновлен!')
            return redirect('account')

    context = {'form': form}
    return render(request, 'users/skill_form.html', context)


# Удаление навыков/скиллов
def deleteSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    if request.method == 'POST':
            skill.delete()
            messages.success(request, 'Навык успешно удален!')
            return redirect('account')
    context = {'object': skill}
    return render(request, 'users/delete_template.html', context)


# Количество непрочитанных сообщений
@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()         # count() – получение числа записей
    context = {'messageRequests': messageRequests, 'unreadCount': unreadCount}
    return render(request, 'users/inbox.html', context)

# Чтение сообщений
@login_required(login_url='login')
def viewMessage(request, pk):
    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read == False:
        message.is_read = True
        message.save()
    context = {'message': message}
    return render(request, 'users/message.html', context) 


# Создание сообщений
def createMessage(request,pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm()

    # Проверяем на авторизацию
    try:
        sender = request.user.profile
    except:
        sender = None

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():                         # если форма валидна, то....
            message = form.save(commit=False)       # Отправляем сообщение в непрочитанном виде
            message.sender = sender                 # Отправитель {username}
            message.recipient = recipient           # Получатель {username}

            if sender:                              # Данные отправителя
                message.name = sender.name
                message.email = sender.email
            message.save()

            messages.success(request, 'Ваше сообщение было успешно отправлено!')
            return redirect('user-profile', pk=recipient.id)

    context = {'recipient': recipient, 'form': form}
    return render(request, 'users/message_form.html', context) 

