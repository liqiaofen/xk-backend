from django import forms

from authentication.models import User


class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', error_messages={"required": "请填写用户名"})
    password = forms.CharField(label='密码', error_messages={"required": "请填写密码"})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.validate_username(username):
            raise forms.ValidationError("用户名{}不存在".format(username))
        return username


class SignUpForm(forms.ModelForm):
    username = forms.CharField(help_text='用户名', error_messages={"required": "请填写用户名"})
    password1 = forms.CharField(help_text='密码', error_messages={"required": "请填写密码"})
    password2 = forms.CharField(help_text='重复密码', error_messages={"required": "请填写密码"})
    nickname = forms.CharField(help_text='昵称', error_messages={"required": "请填写昵称"})
    gender = forms.CharField(help_text='性别')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.validate_username(username):
            raise forms.ValidationError("邮箱{}已经存在".format(username))
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('二次密码不一致')
        return password2

    def save(self, commit=True):
        username = self.cleaned_data.get('username')
        user = User.objects.create_user(username=username, email=username)
        user.set_password(self.cleaned_data['password1'])
        # Profile.objects.create(user=user, nickname=self.cleaned_data.get('nickname'),
        #                        gender=self.cleaned_data.get('gender'))

        return user

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'nickname', 'gender')
