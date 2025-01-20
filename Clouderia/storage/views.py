from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import File
from django.http import JsonResponse
import zipfile
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.base import ContentFile
from accounts.models import UserProfile
from io import BytesIO
from .utils import get_file_type
from main.forms import UploadFileForm

@login_required
def upload_file(request):
    profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')  # Получаем список файлов

        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            upload_type = request.POST.get('upload_type')

            # Создаем объект File (ранее Work)
            file_instance = File.objects.create(
                user=profile,
                title=title,
                description=description,
            )

            if upload_type == 'file':
                # Сохраняем каждый файл
                for file in files:
                    file_instance.file.save(file.name, file)

            elif upload_type == 'folder':
                # Создаем ZIP-файл
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    for file in files:
                        file_content = file.read()
                        zip_file.writestr(file.name, file_content)
                zip_buffer.seek(0)

                # Сохраняем ZIP-файл в File
                file_instance.file.save(f"{title}.zip", ContentFile(zip_buffer.read()))

            file_instance.save()

            messages.success(request, 'Файлы успешно загружены.')
            return redirect('storage:storage_view')  # Возвращаемся на страницу хранилища

        else:
            messages.error(request, 'Ошибка в форме. Проверьте введенные данные.')

    else:
        form = UploadFileForm()

    return render(request, 'storage/upload_file.html', {'form': form})

@login_required
def download_file(request, file_id):
    file_instance = get_object_or_404(File, id=file_id)

    if not file_instance.file:
        messages.error(request, 'File not found.')
        return redirect('storage:upload_file')

    # Принудительное скачивание файла, устанавливаем нужный тип контента
    response = HttpResponse(file_instance.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_instance.file.name}"'

    return response

@login_required
def download_zip(request, file_id):
    file_instance = get_object_or_404(File, id=file_id)

    if not file_instance.file or not file_instance.file.name.endswith('.zip'):
        messages.error(request, 'ZIP-файл не найден.')
        return redirect('storage:storage_view')

    response = HttpResponse(file_instance.file, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{file_instance.file.name}"'
    return response


def storage_view(request):
    try:
        profile = request.user.accounts_profile  # Use the correct related name
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('some_error_page')  # Replace with an appropriate page

    # Получаем сортировку из запроса, если она есть
    sort_by = request.GET.get('sort', 'created_at')  # Сортировка по умолчанию: по дате загрузки
    order = request.GET.get('order', 'asc')  # Сортировка по возрастанию или убыванию

    # Получаем файлы пользователя
    files = File.objects.filter(user=profile)

    # Определяем, как будет выполняться сортировка
    if sort_by == 'name':
        files = files.order_by('title' if order == 'asc' else '-title')
    elif sort_by == 'uploaded_at':
        files = files.order_by('created_at' if order == 'asc' else '-created_at')
    elif sort_by == 'file_type':
        # Для сортировки по типу файла сортируем вручную ниже
        files = sorted(files, key=lambda file: get_file_type(file.file), reverse=(order == 'desc'))
    elif sort_by == 'size':
        # Сортируем файлы по размеру файла вручную
        files = sorted(files, key=lambda file: file.file.size if file.file else 0, reverse=(order == 'desc'))

    total_space = 10 * 1024 * 1024 * 1024  # 10 GB in bytes

    # Проверяем размер каждого файла и суммируем
    used_space = 0
    for file in files:
        if file.file:  # Убедимся, что файл существует
            try:
                used_space += file.file.size
            except AttributeError:
                used_space += 0

    # Вычисляем оставшееся пространство
    remaining_space = max(total_space - used_space, 0)  # Не допускаем отрицательных значений

    # Аннотируем файлы их типом и URL для превью
    for file in files:
        file.file_type = get_file_type(file.file)
        if file.file_type == "image":
            file.preview_url = file.file.url  # Для изображений используем URL для превью
        else:
            file.preview_url = None

    return render(request, 'storage/storage.html', {
        'files': files,
        'remaining_space': remaining_space,
        'sort_by': sort_by,
        'order': order,
    })

def delete_file(request, file_id):
    file_instance = get_object_or_404(File, id=file_id)

    # Check ownership
    if file_instance.user != request.user.accounts_profile:
        return HttpResponseForbidden("You do not have permission to delete this file.")

    # Delete file
    file_instance.file.delete(save=False)  # Delete the actual file
    file_instance.delete()  # Delete the database record

    messages.success(request, "Файл успешно удалён.")
    return redirect('storage:storage_view')


def file_details(request, file_id):
    file_instance = get_object_or_404(File, id=file_id)

    # Получаем тип файла
    file_type = get_file_type(file_instance.file)

    # Для изображений получаем URL превью
    preview_url = None
    if file_type == "image":
        preview_url = file_instance.file.url  # Для изображений используем URL для превью

    # Передаем в контекст
    return render(request, 'storage/file_details.html', {
        'file': file_instance,
        'file_type': file_type,
        'preview_url': preview_url  # Передаем preview_url
    })
