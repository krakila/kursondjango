from django.shortcuts import render, get_object_or_404, redirect
from accounts.models import UserProfile
from django.http import JsonResponse
from .forms import UploadFileForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Work, Complaint
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import UserProfileForm
from .models import Work, Comment
from django.db.models import Count
from django.contrib.auth import update_session_auth_hash
from .forms import CustomPasswordChangeForm
import os
from zipfile import ZipFile
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.conf import settings
import tempfile
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .forms import UploadFileForm
from django.contrib.auth.decorators import login_required
from .models import Work, UserProfile
import os
import re
from zipfile import ZipFile
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import tempfile
import zipfile  # Добавьте эту строку
from django.core.files.base import ContentFile
from django.db import models


@login_required
def upload_file(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    uploaded_files = None  # Will store the uploaded work object

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')

        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']

            # Проверяем, какой тип загрузки выбран
            upload_type = request.POST.get('upload_type')

            # Создаем новый объект Work
            work = Work.objects.create(
                user=profile,
                title=title,
                description=description,
            )

            if upload_type == 'folder':
                # Обрабатываем папку: создаем ZIP-архив
                with tempfile.TemporaryDirectory() as tmpdirname:
                    for file in files:
                        # Сохраняем файлы во временную директорию с сохранением структуры
                        file_path = os.path.join(tmpdirname, file.name)
                        with open(file_path, 'wb+') as destination:
                            for chunk in file.chunks():
                                destination.write(chunk)

                    # Создаем ZIP-архив из временной директории
                    zip_buffer = tempfile.NamedTemporaryFile(delete=True)
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for root, _, files_in_dir in os.walk(tmpdirname):
                            for file in files_in_dir:
                                file_path = os.path.join(root, file)
                                zip_file.write(file_path, os.path.relpath(file_path, tmpdirname))

                    zip_buffer.seek(0)  # Возвращаем указатель в начало файла
                    work.file.save(f"{title}.zip", ContentFile(zip_buffer.read()))
                    zip_buffer.close()

            else:
                # Одиночная загрузка файла или изображения
                for file in files:
                    work.file.save(file.name, file)

            work.save()
            uploaded_files = work

            messages.success(request, 'Файлы успешно загружены.')
            return render(request, 'main/upload_file.html', {'form': form, 'uploaded_files': uploaded_files})
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')

    else:
        form = UploadFileForm()

    return render(request, 'main/upload_file.html', {'form': form, 'uploaded_files': uploaded_files})
# View for downloading files
@login_required
def download_file(request, work_id):
    work = get_object_or_404(Work, id=work_id)

    if not work.file:
        messages.error(request, 'File not found.')
        return redirect('main_page')

    # Send the file as a response
    response = HttpResponse(work.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{work.title}.zip"'
    return response

# View for downloading a folder (if folder uploaded)
@login_required
def download_folder(request, work_id):
    work = get_object_or_404(Work, id=work_id)

    base_folder = os.path.join(settings.MEDIA_ROOT, 'uploads', work.user.user.username, work.title)

    if not os.path.exists(base_folder):
        messages.error(request, 'Folder not found.')
        return redirect('main_page')

    # Create a temporary zip file
    with tempfile.TemporaryFile() as tmp:
        with ZipFile(tmp, 'w') as zip_file:
            for root, dirs, files in os.walk(base_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_file.write(file_path, os.path.relpath(file_path, base_folder))

        tmp.seek(0)
        response = HttpResponse(tmp.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{work.title}.zip"'
        return response


@login_required
def like_work(request, work_id):
    work = get_object_or_404(Work, id=work_id)
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if work.likes.filter(id=user_profile.id).exists():
        work.likes.remove(user_profile)
        message = 'like_removed'
    else:
        work.likes.add(user_profile)
        work.dislikes.remove(user_profile)  # Удаляем дизлайк, если он был
        message = 'like_added'

    work.update_author_likes()  # Обновляем общий счётчик лайков автора

    return JsonResponse({
        'likes': work.total_likes(),
        'dislikes': work.total_dislikes(),
        'message': message
    })


@login_required
def dislike_work(request, work_id):
    work = get_object_or_404(Work, id=work_id)
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if work.dislikes.filter(id=user_profile.id).exists():
        work.dislikes.remove(user_profile)
        message = 'dislike_removed'
    else:
        work.dislikes.add(user_profile)
        work.likes.remove(user_profile)  # Удаляем лайк, если он был
        message = 'dislike_added'

    work.update_author_likes()  # Обновляем общий счётчик лайков автора

    return JsonResponse({
        'likes': work.total_likes(),
        'dislikes': work.total_dislikes(),
        'message': message
    })


def logout_view(request):
    logout(request)
    return redirect('login')


def main_page(request):
    # Получаем запрос на сортировку и поиск
    sort_option = request.GET.get('sort', 'date_desc')
    query = request.GET.get('query', '')

    # Фильтруем работы
    works = Work.objects.all()

    if query:  # Если есть поисковый запрос
        works = works.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query)
        )

    # Сортировка
    if sort_option == 'date_asc':
        works = works.order_by('created_at')
    elif sort_option == 'likes':
        works = works.annotate(like_count=Count('likes')).order_by('-like_count')
    elif sort_option == 'user_popularity':
        works = works.order_by('-user__total_likes')
    else:  # По умолчанию сортируем по убыванию даты
        works = works.order_by('-created_at')

    # Избавляемся от дублей
    works = works.distinct()

    # Контекст с аватаром пользователя
    user_profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'main/main_page.html', {
        'works': works,
        'sort_option': sort_option,
        'query': query,
        'user_avatar': user_profile.avatar
    })


@login_required
def delete_work(request, work_id):
    work = get_object_or_404(Work, id=work_id)

    # Проверяем, что работа принадлежит текущему пользователю
    if work.user == request.user.accounts_profile:  # Теперь доступ к профилю через related_name
        work.delete()
        messages.success(request, 'Работа была успешно удалена.')
    else:
        messages.error(request, 'Вы не можете удалить эту работу.')

    return redirect('user_profile', username=request.user.username)
@login_required
def user_profile(request, username):
    # Ensure that the logged-in user is trying to access their own profile
    if request.user.username != username:
        return redirect('view_user_profile', username=username)  # Redirect to the read-only profile view

    profile = get_object_or_404(UserProfile, user__username=username)

    # Get works associated with this profile
    works = Work.objects.filter(user=profile)

    # Count total likes and dislikes
    total_likes = works.aggregate(total_likes=Count('likes'))['total_likes']
    total_dislikes = works.aggregate(total_dislikes=Count('dislikes'))['total_dislikes']

    return render(request, 'main/user_profile.html', {
        'profile': profile,
        'works': works,
        'total_likes': total_likes,
        'total_dislikes': total_dislikes
    })


@login_required
def view_user_profile(request, username):
    # Get the profile of another user
    profile = get_object_or_404(UserProfile, user__username=username)
    works = Work.objects.filter(user=profile)

    # Count total likes and dislikes
    total_likes = works.aggregate(total_likes=Count('likes'))['total_likes']
    total_dislikes = works.aggregate(total_dislikes=Count('dislikes'))['total_dislikes']

    return render(request, 'main/view_user_profile.html', {
        'profile': profile,
        'works': works,
        'total_likes': total_likes,
        'total_dislikes': total_dislikes,
    })

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_profile = get_object_or_404(UserProfile, user=request.user)
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Обновление данных пользователя
        if username:
            request.user.username = username
        if email:
            user_profile.work_email = email

        # Обработка загрузки аватара
        if 'avatar' in request.FILES:
            user_profile.avatar = request.FILES['avatar']

        # Сохранение всех изменений
        request.user.save()
        user_profile.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
def report_work(request, work_id):
    work = get_object_or_404(Work, id=work_id)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        reporter_profile = UserProfile.objects.get(user=request.user)  # Получаем UserProfile

        # Создание жалобы в базе данных
        Complaint.objects.create(
            reporter=reporter_profile,
            reported_work=work,
            reason=reason
        )

        # Получение email администратора
        admin = User.objects.filter(is_superuser=True).first()
        if admin:
            admin_email = admin.email
            # Отправка письма админу
            send_mail(
                'Новая жалоба на работу',
                f'Поступила новая жалоба:\n\n'
                f'Работа: {work.title}\n'
                f'Пожаловался: {reporter_profile.user.username}\n'
                f'Причина: {reason}\n'
                f'Время: {timezone.now()}',
                'noreply@example.com',
                [admin_email],
                fail_silently=False,
            )

        messages.success(request, 'Жалоба успешно отправлена.')
        return redirect('main_page')

    return render(request, 'report_work.html', {'work': work})
@login_required
def view_work(request, work_id):
    work = get_object_or_404(Work, id=work_id)
    comments = work.comments.all().order_by('-created_at')

    if request.method == 'POST':
        content = request.POST.get('content')
        user_profile = get_object_or_404(UserProfile, user=request.user)
        if content:
            Comment.objects.create(
                work=work,
                user=user_profile,
                content=content
            )
            messages.success(request, 'Комментарий добавлен.')
            return redirect('view_work', work_id=work.id)

    return render(request, 'main/view_work.html', {'work': work, 'comments': comments})


@login_required
def profile_settings(request):
    if request.method == 'POST':
        # Используем форму для смены пароля
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            # Сохраняем новый пароль
            form.save()
            update_session_auth_hash(request, form.user)  # Обновляем сессию, чтобы пользователь не разлогинился
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('profile_settings')  # Остаться на той же странице
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'main/profile_settings.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Важно для предотвращения выхода пользователя из системы
            messages.success(request, 'Пароль успешно изменен.')
            return redirect('profile_settings')  # Перенаправление на страницу настроек
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'main/profile_settings.html', {'form': form})