from django.db import models
from django.dispatch import Signal
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

from .utilities import send_activation_notification, get_timestamp_path,\
    send_new_comment_notification

# Объявляем сигнал регистрации для отправки письма.
user_registrated = Signal(providing_args=['instance'])


# Объявляем обработчик сигнала регистраци пользователя.
def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


# Подключем к сигналу обработчик.
user_registrated.connect(user_registrated_dispatcher)


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True,
                                       verbose_name='Прошел активацию?')
    send_messages = \
        models.BooleanField(default=True, verbose_name='Уведомлять о комментариях?')

    def delete(self, *args, **kwargs):
        """Удаление всех объявлений пользователя,
         при удалиении самого пользователя."""
        for bb in self.bb_set.all():
            bb.delete()
        super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass


class Rubric(models.Model):
    """Модель рублики."""
    name = models.CharField(max_length=20, db_index=True, unique=True,
                            verbose_name='Название')
    order = models.SmallIntegerField(default=0, db_index=True,
                                     verbose_name='Порядок')
    super_rubric = models.ForeignKey('SuperRubric',
                                     on_delete=models.PROTECT, null=True,
                                     blank=True, verbose_name='Надрубрика')


class SuperRubricManager(models.Manager):
    """Диспечер записей для модели SuperRubric.Фильтрует записи из модели
     Rubric. Отбирает из них те, у которых поле super_rubric пустое."""
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)


class SuperRubric(Rubric):
    objects = SuperRubricManager()

    def __str__(self):
        """Генерирует строковое представление - название рубрики."""
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = 'Надрубрика'
        verbose_name_plural ='Надрубрики'


class SubRubricManager(models.Manager):
    """Диспечер записей для модели SubRubric.Фильтрует записи из модели
     Rubric. Отбирает из них те, у которых поле super_rubric не пустое."""
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)


class SubRubric(Rubric):
    objects = SubRubricManager()

    def __str__(self):
        """Генерирует строковое представление - название подрубрики
        в формате <название надрубрики> - <название подрубрики>"""
        return '%s - %s' % (self.super_rubric.name, self.name)

    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name',
                    'order', 'name')
        verbose_name = 'Подрубрика'
        verbose_name_plural = 'Подрубрики'


class Bb(models.Model):
    """Модель обявлений."""
    rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT,
                               verbose_name='Рубрика')
    title = models.CharField(max_length=60, verbose_name='Товар')
    content = models.TextField(verbose_name='Описание')
    price = models.FloatField(default=0, verbose_name='Цена')
    contacts = models.TextField(verbose_name='Контакты')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path,
                              verbose_name='Изображение')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                               verbose_name='Автор объявления')
    is_active = models.BooleanField(default=True, db_index=True,
                                    verbose_name='Выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,
                                      verbose_name='Опубликовано')

    # В переопределнном методе delete, перед удалением записи
    # перебираем и удаляем все дополнительные изображения,
    # чтобы django_cleanup удалил соотвесвующие файлы с сервера.
    def delete(self, *args, **kwargs):
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Объявления'
        verbose_name = 'Объявление'
        ordering = ['-created_at']


class AdditionalImage(models.Model):
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE,
                           verbose_name='Объявление')
    image = models.ImageField(upload_to=get_timestamp_path,
                              verbose_name='Изображение')

    class Meta:
        verbose_name_plural = 'Дополнительные иллюстраци'
        verbose_name = 'Дополнительное изображение'


class Comment(models.Model):
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE,
                           verbose_name='Объявление')
    author = models.CharField(max_length=30, verbose_name='Автор')
    content = models.TextField(verbose_name='Содержание')
    is_active = models.BooleanField(default=True, db_index=True,
                                    verbose_name='Показывать комментарий?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,
                                      verbose_name='Опубликован')

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
        ordering = ['created_at']


# Объявляем обработчик сигнала сохранения нового комментария.
def post_save_dispatcher(sender, **kwargs):
    author = kwargs['instance'].bb.author
    comment_author = kwargs['instance'].author
    # Дополнительно проверяем, не является-ли автор кромментария и
    # автор объявления одним и темже пользователем.
    if kwargs['created'] and author.send_messages and \
            author.username != comment_author:
        send_new_comment_notification(kwargs['instance'])


# Подключем к сигналу обработчик.
post_save.connect(post_save_dispatcher, sender=Comment)
