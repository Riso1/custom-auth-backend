from django.db import models

class Role(models.Model):
    """Роль пользователя в системе."""

    name = models.CharField('Название роли', max_length=50, unique=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self) -> str:
        return self.name


class User(models.Model):
    """Пользователь приложения."""

    last_name = models.CharField('Фамилия', max_length=100)
    first_name = models.CharField('Имя', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100, blank=True)

    email = models.EmailField('Email', unique=True)
    password_hash = models.CharField('Хеш пароля', max_length=255)

    role = models.ForeignKey(
        Role,
        verbose_name='Роль',
        on_delete=models.PROTECT,
        related_name='users',
        null=True,
        blank=True,
    )

    is_active = models.BooleanField('Активен', default=True)

    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return f'{self.last_name} {self.first_name} — {self.email}'


class BusinessElement(models.Model):
    """Ресурс приложения, к которому можно выдать доступ."""

    code = models.CharField('Код ресурса', max_length=100, unique=True)
    name = models.CharField('Название ресурса', max_length=150)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Ресурс приложения'
        verbose_name_plural = 'Ресурсы приложения'

    def __str__(self) -> str:
        return f'{self.name} ({self.code})'


class AccessRule(models.Model):
    """Правило доступа роли к конкретному ресурсу."""

    role = models.ForeignKey(
        Role,
        verbose_name='Роль',
        on_delete=models.CASCADE,
        related_name='access_rules',
    )
    element = models.ForeignKey(
        BusinessElement,
        verbose_name='Ресурс',
        on_delete=models.CASCADE,
        related_name='access_rules',
    )

    read_permission = models.BooleanField('Просмотр своих объектов', default=False)
    read_all_permission = models.BooleanField('Просмотр всех объектов', default=False)

    create_permission = models.BooleanField('Создание объектов', default=False)

    update_permission = models.BooleanField('Изменение своих объектов', default=False)
    update_all_permission = models.BooleanField('Изменение всех объектов', default=False)

    delete_permission = models.BooleanField('Удаление своих объектов', default=False)
    delete_all_permission = models.BooleanField('Удаление всех объектов', default=False)

    class Meta:
        verbose_name = 'Правило доступа'
        verbose_name_plural = 'Правила доступа'
        unique_together = ('role', 'element')

    def __str__(self) -> str:
        return f'{self.role.name}: {self.element.code}'


class AuthToken(models.Model):
    """Активный токен авторизации пользователя."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='tokens',
    )
    token = models.TextField('Токен', unique=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Токен авторизации'
        verbose_name_plural = 'Токены авторизации'

    def __str__(self) -> str:
        return f'Токен пользователя {self.user.email}'
    