# Create your models here.
from denorm import CountField, denormalized, depend_on_related
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeFramedModel


class Machine(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class History(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)

    def __str__(self):
        return str(self.id)


class User(AbstractBaseUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        # abstract = True


class Gallery(models.Model):
    name = models.TextField()
    # user = models.ForeignKey(User, related_name='gallery', on_delete=models.CASCADE)
    picture_count = CountField('picture_set', default=0)
    total = models.IntegerField(default=0)


class Picture(models.Model):
    name = models.TextField()
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)

    @denormalized(models.CharField, max_length=100)
    @depend_on_related(Gallery)
    def gallery_name(self):
        # your code
        return self.name + self.gallery.name


from django_lifecycle import LifecycleModel, hook, AFTER_UPDATE, LifecycleModelMixin


class Article(LifecycleModel):
    contents = models.TextField()
    updated_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=20, choices=[('draft', '草稿'), ('published', '发布')])


class Post(TimeFramedModel):
    pass


class Employees(LifecycleModelMixin, models.Model):
    name = models.CharField('名称', max_length=15)
    department = models.ForeignKey('Departments', verbose_name='部门', on_delete=models.CASCADE)
    # department_name = models.CharField('部门名称', max_length=15)
    ...

    # @hook(AFTER_SAVE, when="department")
    # def change_department(self):
    #     print('Employees-change_department')
    #     Employees.objects.filter(id=self.id).update(department_name=self.department.name)

    @denormalized(models.CharField, max_length=100)
    def department_name(self):
        print('department_name')
        return self.department.name


class Departments(LifecycleModelMixin, models.Model):
    name = models.CharField('部门名称', max_length=15)

    @hook(AFTER_UPDATE, when='name')
    # @hook(AFTER_SAVE, when='name', has_changed=True)
    def change_name(self):
        print('222Departments-change_name')
        Employees.objects.filter(department=self).update(department_name=self.name)
