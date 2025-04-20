from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.forms import AdminPasswordChangeForm, UserChangeForm
from django.utils.translation import gettext_lazy as _

from .models import Subscription

User = get_user_model()

admin.site.unregister(Group)


class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    change_password_form = AdminPasswordChangeForm
    model = User

    list_display = ('id', 'username', 'first_name', 'last_name', 'email',)
    list_filter = ('username',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': (
            'username', 'first_name', 'last_name')}),
        (_('Permissions'), {'fields': (
            'is_active', 'is_staff', 'is_superuser',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

    search_fields = ('email', 'username')
    ordering = ('email',)

    readonly_fields = ()


admin.site.register(User, CustomUserAdmin)


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscriber', 'target',)
    search_fields = ('subscriber__username',)
    empty_value_display = '-пусто-'
