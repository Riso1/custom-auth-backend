from django.contrib import admin
from .models import AccessRule, AuthToken, BusinessElement, Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'last_name',
        'first_name',
        'middle_name',
        'role',
        'is_active',
        'created_at',
    )
    list_filter = ('is_active', 'role')
    search_fields = ('email', 'last_name', 'first_name')


@admin.register(BusinessElement)
class BusinessElementAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name')
    search_fields = ('code', 'name')


@admin.register(AccessRule)
class AccessRuleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'role',
        'element',
        'read_permission',
        'read_all_permission',
        'create_permission',
        'update_permission',
        'update_all_permission',
        'delete_permission',
        'delete_all_permission',
    )
    list_filter = ('role', 'element')

@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__email',)
