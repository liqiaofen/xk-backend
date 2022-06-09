from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import FormView
from django.views.generic.base import View

from authentication import forms
from core.drf.renderers import JsonBaseResponse


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse("login"))


class BackendLoginView(View):

    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, "backend/login.html")
        else:
            return redirect(reverse('backend-index'))

    def post(self, request):
        form = forms.LoginForm(request.POST)

        if not form.is_valid():
            return JsonBaseResponse({'status': False, 'errors': form.errors})

        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if user is None:
            return JsonBaseResponse({'status': False, 'errors': {'username': ['账号或者密码错误']}})
        if not user.is_active:
            return JsonBaseResponse({'status': False, 'errors': {'username': ['用户已被禁用']}})

        login(request, user)

        request.session["is_login"] = True
        if not request.POST.get("remember"):
            request.session.set_expiry(0)  # 如果没选记住我，关闭浏览器就清空session

        return JsonBaseResponse({'status': True, 'data': {'access': user.token}})


class LoginView(View):
    def get(self, request):

        if not request.user.is_authenticated:
            return render(request, "frontend/login.html")
        else:
            return redirect(reverse('home'))

    def post(self, request):
        form = forms.LoginForm(request.POST)

        if not form.is_valid():
            return JsonBaseResponse({'status': False, 'errors': form.errors})

        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if user is None:
            return JsonBaseResponse({'status': False, 'errors': {'username': ['账号或者密码错误']}})
        if not user.is_active:
            return JsonBaseResponse({'status': False, 'errors': {'username': ['用户已被禁用']}})

        login(request, user)

        request.session["is_login"] = True
        if not request.POST.get("remember"):
            request.session.set_expiry(0)  # 如果没选记住我，关闭浏览器就清空session
        redirect_to = request.GET.get("next", reverse('home'))
        return JsonBaseResponse({'status': True, 'data': {'redirect_to': redirect_to}})


class SignUpView(FormView):
    form_class = forms.SignUpForm
    template_name = 'frontend/signup.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)

        self.request.session["is_login"] = True
        return JsonBaseResponse({'status': True, 'data': {'redirect_to': reverse('home')}})

    def form_invalid(self, form):
        return JsonBaseResponse({'status': False, 'errors': form.errors})
