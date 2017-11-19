import json

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Article, Course, User, CourseGroup
from .forms import LoginForm, CreateGroupForm


def index(request):
    return render(request, 'index.html')


def login(request):
    if request.user.is_authenticated():
        messages.warning(request, '用户 {username}, 你已经登陆'.format(username=request.user.username))
        return HttpResponseRedirect('/')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            messages.success(request, '欢迎回来, {username}'.format(username=request.user.username))
            return HttpResponseRedirect('/')
        else:
            messages.error(request, '账号或密码错误')
    return render(request, 'login.html', {'login_form': form})


@login_required
def logout(request):
    messages.success(request, '登出成功, Bye~')
    auth.logout(request)
    return HttpResponseRedirect('/')


def courses(request):
    queryset = Course.objects.all()
    query = request.GET.get('query') or None
    if query:
        queryset = queryset.filter(title__contains=query)
    p = Paginator(queryset, 5)
    page = request.GET.get('page') or 1
    try:
        course_list = p.page(page)
    except PageNotAnInteger:
        course_list = p.page(1)
    except EmptyPage:
        course_list = p.page(p.num_pages)
    return render(request, 'courses.html', {
        'p': course_list,
        'query': query,
    })


def course(request, course_id):
    c = Course.objects.filter(pk=course_id).first()
    current_group = None
    if request.user.is_authenticated():
        request.user: User
        current_group = request.user.added_groups.filter(belong=c).first()
    return render(request, 'course_detail.html', {
        'course': c,
        'articles': c.article_set.all(),
        'group': current_group,
    })


def user_detail(request, username):
    user = User.objects.filter(username=username).first()
    # user: User
    added_courses = [group.belong for group in user.added_groups.all()]
    return render(request, 'user_detail.html', {
        'user': user,
        'courses': added_courses,
    })


@login_required
def create_group(request, course_id):
    form = CreateGroupForm(request.POST or None)
    try:
        c = Course.objects.get(pk=course_id)
        current_group = request.user.added_groups.filter(belong=c).first()
        if current_group:
            raise Http404('别瞎试了, 你已经加入一个团队了')
        if request.POST and form.is_valid():
            name = request.POST.get('name', None)
            if not CourseGroup.objects.filter(name=name).all():
                request.user: User
                new_group = request.user.my_groups.create(name=name, belong=c)
                new_group.members.add(request.user)
                new_group.save()
                return HttpResponseRedirect('/groups/{g_id}/'.format(g_id=new_group.id))
            messages.warning(request, '这个名字已经有人捷足先登了，换一个试试吧')
    except Course.DoesNotExist:
        raise Http404('如果你正在读这行字，请联系管理员me@bllli.cn')
    return render(request, 'group_create.html', {
        'course': c,
    })


def groups(request):
    queryset = CourseGroup.objects.all()
    query = request.GET.get('query') or None
    if query:
        queryset = queryset.filter(name__contains=query)
    p = Paginator(queryset, 5)
    page = request.GET.get('page') or 1
    try:
        group_list = p.page(page)
    except PageNotAnInteger:
        group_list = p.page(1)
    except EmptyPage:
        group_list = p.page(p.num_pages)
    return render(request, 'groups.html', {
        'p': group_list,
        'query': query,
    })


def group_detail(request, group_id):
    group = CourseGroup.objects.filter(pk=group_id).first()
    return render(request, 'group_detail.html', {
        'group': group
    })
