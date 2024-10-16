import datetime

from django.db import models
from django.db.models import Min, Max, Q, Avg
from django.utils.html import format_html
from django.db.models.signals import post_save
from django.dispatch import receiver
from easy_thumbnails.files import get_thumbnailer
from filer.fields.image import FilerImageField


TARGETS = (
    ('1', 'Работник',),
    ('2', 'Работодатель',),
)


class Text(models.Model):
    slug = models.CharField(verbose_name='Идентификатор', max_length=100, unique=True)
    rus = models.TextField(verbose_name='Текст (русский)', max_length=1024, null=True, blank=True)
    heb = models.TextField(verbose_name='Текст (иврит)', max_length=1024, null=True, blank=True)
    my_order = models.PositiveIntegerField(verbose_name='Порядок', default=0, blank=False, null=False)

    class Meta:
        verbose_name = 'текст'
        verbose_name_plural = 'тексты'
        ordering = ('my_order',)

    def __str__(self):
        if self.rus:    
            return self.rus
        if self.heb:
            return self.heb
        return self.slug


class Button(models.Model):
    slug = models.CharField(verbose_name='Идентификатор', max_length=100, unique=True)
    rus = models.CharField(verbose_name='Кнопка (русский)', max_length=100, null=True, blank=True)
    heb = models.CharField(verbose_name='Кнопка (иврит)', max_length=100, null=True, blank=True)
    my_order = models.PositiveIntegerField(verbose_name='Порядок', default=0, blank=False, null=False)

    class Meta:
        verbose_name = 'кнопка'
        verbose_name_plural = 'кнопки'
        ordering = ('my_order',)

    def __str__(self):
        if self.rus:    
            return self.rus
        if self.heb:
            return self.heb
        return self.slug


class TGUser(models.Model):
    tg_id = models.CharField(verbose_name='Телеграм id', max_length=100, unique=True)
    target = models.CharField(verbose_name='Тип пользователя', choices=TARGETS, max_length=10)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('-created_at',)

    def __str__(self):
        return self.tg_id


class Area(models.Model):
    number = models.PositiveIntegerField(verbose_name='Номер территориальной зоны')

    def __str__(self):
        return str(self.number)


class Worker(models.Model):
    tg_id = models.CharField(verbose_name='Телеграм id', max_length=100, unique=True)
    username = models.CharField(verbose_name='Ник телеграм', max_length=100, null=True, blank=True)
    name = models.CharField(verbose_name='Имя', max_length=100, null=True, blank=True)
    phone = models.CharField(verbose_name='Номер телефона', max_length=25, null=True, blank=True)
    passport_photo = FilerImageField(verbose_name='Фото паспорта', on_delete=models.SET_NULL, null=True, blank=True)
    passport_photo_tg_id = models.CharField(verbose_name='TG id паспорта', max_length=200, null=True, blank=True)
    selfie = models.CharField(verbose_name='TG id селфи', max_length=200, null=True, blank=True)
    areas = models.ManyToManyField(Area, verbose_name='зоны', related_name='workers', blank=True)
    permanent_work = models.BooleanField(default=True)
    about = models.TextField(verbose_name='О себе', blank=True, null=True)
    about_heb = models.TextField(verbose_name='О себе (иврит)', blank=True, null=True, default=None)
    min_salary = models.PositiveIntegerField(verbose_name='Зарплата (от) ₪', default=0)
    notifications = models.BooleanField(verbose_name='Подписан на уведомления?', default=False)
    is_searching = models.BooleanField(verbose_name='В поисках работы?', default=True)
    is_approved = models.BooleanField(verbose_name='Аккаунт подтвержден?', default=None, null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'работник'
        verbose_name_plural = 'работники'
        ordering = ('-created_at',)

    def __str__(self):
        if self.name:
            return f'{self.tg_id} - {self.name}'
        
        return self.tg_id

    def get_thumbnail(self):
        image = '-'
        if self.passport_photo:
            image = format_html('<img src="{0}"/>', get_thumbnailer(self.passport_photo)['passport_thumbnail'].url)
        return image
    get_thumbnail.allow_tags = True
    get_thumbnail.short_description = u'Паспорт'

    @property
    def readable_zones(self):
        zones = []
        for area in self.areas.all():
            zones.append(str(area.number))

        return ', '.join(zones)

    @property
    def readable_approved_status(self):
        if self.is_approved is None:
            return '⏳ на проверке'

        if self.is_approved is False:
            return '❌ не одобрен (попробуйте заполнить заново)'

        if self.is_approved is True:
            return '✅ одобрен'

    @property
    def readable_search_status(self):
        if self.is_searching is True:
            return '🔍 да'

        return '🌴 нет'
    
    @property
    def readable_notifications_status(self):
        if self.notifications is True:
            return 'включены'

        return 'отключены'
    
    @property
    def readable_work_type_rus(self):
        if self.permanent_work is True:
            return 'постоянная'

        return 'временная'

    @property
    def readable_work_type_heb(self):
        if self.permanent_work is True:
            return 'קבועה'

        return 'זמנית'

    @property
    def rating_rus(self):
        reviews = self.received_reviews.all()
        if reviews.exists():
            average = reviews.aggregate(Avg('rate'))['rate__avg']
            return f'{round(average, 1)} ⭐️'
        else:
            return 'нет оценок'
    
    @property
    def rating_heb(self):
        reviews = self.received_reviews.all()
        if reviews.exists():
            average = reviews.aggregate(Avg('rate'))['rate__avg']
            return f'{round(average, 1)} ⭐️'
        else:
            return 'אין דירוגים'


class Employer(models.Model):
    tg_id = models.CharField(verbose_name='Телеграм id', max_length=100, unique=True)
    username = models.CharField(verbose_name='Ник телеграм', max_length=100, null=True, blank=True)
    name = models.CharField(verbose_name='Имя/название компании', default='Company', max_length=150)
    phone = models.CharField(verbose_name='Номер телефона', max_length=25, null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'работодатель'
        verbose_name_plural = 'работодатель'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.tg_id} - {self.name}'

    @property
    def all_offered_zones(self):
        zones = []
        for job in self.jobs.filter(Q(is_approved=True) & Q(is_active=True)).all():
            for zone in job.areas.all():
                if str(zone.number) not in zones:
                    zones.append(str(zone.number))
        
        return ', '.join(zones)

    @property
    def all_work_types(self):
        work_types = []
        if self.jobs.filter(permanent_work=True).first():
            work_types.append('постоянная')
        if self.jobs.filter(permanent_work=True).first():
            work_types.append('временная')
        
        if work_types:
            return ', '.join(work_types)
        
        return 'еще нет размещенных вакансий'

    @property
    def min_min_salary(self):
        min_salary = self.jobs.filter(Q(is_approved=True) & Q(is_active=True)).aggregate(Min('min_salary'))['min_salary__min']
        if min_salary is None:
            return 'не указана'
        else:
            return f'{min_salary} ₪'
    
    @property
    def max_min_salary(self):
        min_salary = self.jobs.filter(Q(is_approved=True) & Q(is_active=True)).aggregate(Max('min_salary'))['min_salary__max']
        if min_salary is None:
            return 'не указана'
        else:
            return f'{min_salary} ₪'
    
    @property
    def rating_rus(self):
        reviews = self.received_reviews.all()
        if reviews.exists():
            average = reviews.aggregate(Avg('rate'))['rate__avg']
            return f'{round(average, 1)} ⭐️'
        else:
            return 'нет оценок'
    
    @property
    def rating_heb(self):
        reviews = self.received_reviews.all()
        if reviews.exists():
            average = reviews.aggregate(Avg('rate'))['rate__avg']
            return f'{round(average, 1)} ⭐️'
        else:
            return 'אין דירוגים'
    

class Job(models.Model):
    employer = models.ForeignKey(Employer, verbose_name='Работодатель', on_delete=models.CASCADE, related_name='jobs')
    min_salary = models.PositiveIntegerField(verbose_name='Зарплата (от) ₪', default=0)
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    areas = models.ManyToManyField(Area, verbose_name='зоны', related_name='jobs', blank=True)
    permanent_work = models.BooleanField(default=True)
    description_rus = models.TextField(verbose_name='Описание (русский)', blank=True, null=True, default=None)
    notifications = models.BooleanField(verbose_name='Подписан на уведомления?', default=False)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=None, null=True)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Дата обновления', auto_now=True, null=True)

    class Meta:
        verbose_name = 'вакансия'
        verbose_name_plural = 'вакансии'
        ordering = ('-created_at',)
        
    def __str__(self):     
        return f'{self.min_salary} ₪: {self.readable_zones}'
    
    @property
    def readable_zones(self):
        zones = []
        for area in self.areas.all():
            zones.append(str(area.number))

        return ', '.join(zones)

    @property
    def readable_work_type_rus(self):
        if self.permanent_work is True:
            return 'постоянная'

        return 'временная'

    @property
    def readable_work_type_heb(self):
        if self.permanent_work is True:
            return 'קבועה'

        return 'זמנית'

    @property
    def readable_notifications_rus_status(self):
        if self.notifications is True:
            return 'включены'

        return 'отключены'
    
    @property
    def readable_notifications_heb_status(self):
        if self.notifications is True:
            return 'מופעל'

        return 'כבוי'

    @property
    def readable_approved_status(self):
        if self.is_approved is None:
            return '⏳ בבדיקה'

        if self.is_approved is False:
            return '❌ לא אושרה'

        if self.is_approved is True:
            return '✅ אושרה'
    
    @property
    def readable_active_status(self):
        if self.is_active is True:
            return 'כן'

        if self.is_active is False:
            return 'לא'


class WorkerReview(models.Model):
    worker = models.ForeignKey(Worker, verbose_name='Сотрудник, оставивший отзыв', related_name='leaved_reviews', on_delete=models.SET_NULL, null=True)
    employer = models.ForeignKey(Employer, verbose_name='Работодатель, получивший отзыв', related_name='received_reviews', on_delete=models.SET_NULL, null=True)
    rate = models.PositiveIntegerField(verbose_name='Оценка', default=5)
    review = models.TextField(verbose_name='Отзыв (русский)', blank=True, null=True)
    review_heb = models.TextField(verbose_name='Отзыв (иврит)', blank=True, null=True)
    is_approved = models.BooleanField(default=None, null=True)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'отзыв работника'
        verbose_name_plural = 'отзывы работников'
        ordering = ('-created_at',)
        
    def __str__(self):
        return str(self.rate)
    
    @property
    def readable_approved_status(self):
        if self.is_approved is None:
            return '⏳ на проверке'

        if self.is_approved is False:
            return '❌ не одобрен'

        if self.is_approved is True:
            return '✅ одобрен'


class EmployerReview(models.Model):
    employer = models.ForeignKey(Employer, verbose_name='Работодатель, оставивший отзыв', related_name='leaved_reviews', on_delete=models.SET_NULL, null=True)
    worker = models.ForeignKey(Worker, verbose_name='Сотрудник, получивший отзыв', related_name='received_reviews', on_delete=models.SET_NULL, null=True)
    rate = models.PositiveIntegerField(verbose_name='Оценка', default=5)
    review = models.TextField(verbose_name='Отзыв (русский)', blank=True, null=True)
    review_rus = models.TextField(verbose_name='Отзыв (иврит)', blank=True, null=True)
    is_approved = models.BooleanField(default=None, null=True)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'отзыв работодателя'
        verbose_name_plural = 'отзывы работодателей'
        ordering = ('-created_at',)
        
    def __str__(self):
        return str(self.rate)

    @property
    def readable_approved_status(self):
        if self.is_approved is None:
            return '⏳ בבדיקה'

        if self.is_approved is False:
            return '❌ לא אושרה'

        if self.is_approved is True:
            return '✅ אושרה'

            
class ChannelForWorkers(models.Model):
    title = models.CharField(verbose_name='Название', max_length=200, unique=True)
    tg_id = models.CharField(verbose_name='Телеграм id', max_length=100, unique=True)
    is_active = models.BooleanField(verbose_name='Участвует в рассылке?', default=True)

    class Meta:
        verbose_name = 'канал для работников'
        verbose_name_plural = 'каналы для работников (с вакансиями)'
        
    def __str__(self):
        return self.title


class ChannelForEmployers(models.Model):
    title = models.CharField(verbose_name='Название', max_length=200, unique=True)
    tg_id = models.CharField(verbose_name='Телеграм id', max_length=100, unique=True)
    is_active = models.BooleanField(verbose_name='Участвует в рассылке?', default=True)

    class Meta:
        verbose_name = 'канал для работодателей'
        verbose_name_plural = 'каналы для работодателей (с сотрудниками)'
        
    def __str__(self):
        return self.title


class WorkerCooperationProposal(models.Model):
    worker = models.ForeignKey(Worker, verbose_name='Работник, запросивший сотрудничество', related_name='outbox_proposals', on_delete=models.CASCADE, null=True)
    employer = models.ForeignKey(Employer, verbose_name='Работодатель, получивший запрос', related_name='inbox_proposals', on_delete=models.CASCADE, null=True)
    job = models.ForeignKey(Job, verbose_name='Вакансия, вызвавшая запрос', related_name='proposals', on_delete=models.CASCADE, null=True)
    is_accepted = models.BooleanField(verbose_name='Принят?', default=None, null=True, blank=True)
    is_proceeded = models.BooleanField(verbose_name='Отправлен в админ чат?', default=False)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Дата создания', auto_now=True)

    class Meta:
        verbose_name = 'предложение о сотрудничестве от работника'
        verbose_name_plural = 'предложения о сотрудничестве от работников'
        ordering = ('-updated_at',)

    @property
    def readable_rus_accepted_status(self):
        if self.is_accepted is None:
            return '⏳ ожидает ответа'

        if self.is_accepted is False:
            return '❌ отклонен'

        if self.is_accepted is True:
            return '✅ принят (администратор свяжется с вами)'
    
    @property
    def readable_heb_accepted_status(self):
        if self.is_accepted is None:
            return '⏳ ממתין לתשובה'

        if self.is_accepted is False:
            return '❌ נדחה'

        if self.is_accepted is True:
            return '✅ התקבל (המנהל ייצור איתך קשר)'


class EmployerCooperationProposal(models.Model):
    employer = models.ForeignKey(Employer, verbose_name='Работодатель, запросивший сотрудничество', related_name='outbox_proposals', on_delete=models.CASCADE, null=True)
    worker = models.ForeignKey(Worker, verbose_name='Работник, получивший запрос', related_name='inbox_proposals', on_delete=models.CASCADE, null=True)
    is_accepted = models.BooleanField(verbose_name='Принят?', default=None, null=True, blank=True)
    is_proceeded = models.BooleanField(verbose_name='Отправлен в админ чат?', default=False)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Дата создания', auto_now=True)

    class Meta:
        verbose_name = 'предложение о сотрудничестве от работодателей'
        verbose_name_plural = 'предложения о сотрудничестве от работодателей'
        ordering = ('-updated_at',)

    @property
    def readable_rus_accepted_status(self):
        if self.is_accepted is None:
            return '⏳ ожидает ответа'

        if self.is_accepted is False:
            return '❌ отклонен'

        if self.is_accepted is True:
            return '✅ принят (администратор свяжется с вами)'
    
    @property
    def readable_heb_accepted_status(self):
        if self.is_accepted is None:
            return '⏳ ממתין לתשובה'

        if self.is_accepted is False:
            return '❌ נדחה'

        if self.is_accepted is True:
            return '✅ התקבל (המנהל ייצור איתך קשר)'
