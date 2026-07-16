from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Tag, Task

# Create your views here.


def index(request):
    if request.method == 'POST':
        task = Task(title=request.POST['title'],
                    due_at=make_aware(parse_datetime(request.POST['due_at'])))
        task.save()
        tag_names = {
            name.strip() for name in request.POST.getlist('tags') if name.strip()
        }
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name)
            task.tags.add(tag)

    tasks = Task.objects.filter(is_deleted=False).prefetch_related('tags')
    if request.GET.get('order') == 'due':
        tasks = tasks.order_by('due_at')
    else:
        tasks = tasks.order_by('-posted_at')

    context = {
        'tasks': tasks
    }
    return render(request, 'todo/index.html', context)


def detail(request, task_id):
    try:
        task = Task.objects.prefetch_related('tags').get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    context = {
        'task': task,
    }
    return render(request, 'todo/detail.html', context)


def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    if request.method == 'POST':
        task.title = request.POST['title']
        task.due_at = make_aware(parse_datetime(request.POST['due_at']))
        task.save()
        return redirect(detail, task_id)

    context = {
        'task': task
    }

    return render(request, "todo/edit.html", context)


def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.is_deleted = True
    task.save()
    return redirect(index)


def deleted_list(request):
    tasks = Task.objects.filter(is_deleted=True).order_by('-posted_at')
    context = {
        'tasks': tasks
    }
    return render(request, 'todo/deleted_list.html', context)
