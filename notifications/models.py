from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from filer.fields.image import FilerImageField

from core.models import TGUser
from notifications.utils import translate_to_heb


NOTIFICATION_TYPES = (
    ('1', 'Индивидуальное'),
    ('2', 'Всем работникам'),
    ('3', 'Всем работодателям'),
    ('4', 'Всем пользователям')
)

class LinkButton(models.Model):
    notification = models.ForeignKey('Notification', verbose_name='Уведомление', on_delete=models.CASCADE, related_name='buttons')
    text_rus = models.CharField(verbose_name='Текст (русский)', max_length=50)
    text_heb = models.CharField(verbose_name='Текст (иврит)', max_length=50)
    link = models.CharField(verbose_name='Ссылка', max_length=1024, help_text='Обязательно должна содержать "https://"')
    my_order = models.PositiveIntegerField(verbose_name='Порядок', default=0, blank=False, null=False)

    class Meta:
        verbose_name = 'кнопка с ссылкой'
        verbose_name_plural = 'кнопки с ссылками'
        ordering = ('my_order',)
    
    def __str__(self):
        return self.link


class Notification(models.Model):
    target = models.CharField(verbose_name='Тип уведомления', choices=NOTIFICATION_TYPES, max_length=30)
    user = models.ForeignKey(TGUser, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='notifications', null=True, blank=True, help_text='Учитывается только если выбран тип "индивидуальное"')
    text_rus = CKEditor5Field(verbose_name='Текст уведомления (русский)', blank=True, null=True)
    text_heb = CKEditor5Field(verbose_name='Текст уведомления (иврит)', blank=True, null=True)
    notify_time = models.DateTimeField(verbose_name='Время уведомления', help_text='Указывается в UTC (-3 от МСК).')
    image = FilerImageField(verbose_name='Изображение', on_delete=models.SET_NULL, null=True, blank=True)
    is_valid = models.BooleanField(verbose_name='Рассылка валидна?', default=False) 
    started = models.BooleanField(verbose_name='Рассылка началась?', default=False) 
    notified = models.BooleanField(verbose_name='Успешно?', null=True, blank=True, default=None)

    success_users = models.IntegerField(default=0)
    total_send_users = models.IntegerField(default=0)
    total_users = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'уведомление пользователей'
        verbose_name_plural = 'уведомления пользователей'
        ordering = ('-notify_time',)
    
    def __str__(self):
        return self.target
    
    def save(self, *args, **kwargs) -> None:
        if self.text_rus == '<p>&nbsp;</p>' and self.text_heb == '<p>&nbsp;</p>':
            self.is_valid = False
        
        elif (self.target == '2' or self.target == '4') and self.text_rus == '<p>&nbsp;</p>':
            self.is_valid = False

        elif self.target == '1' and self.user is None:
            self.is_valid = False
        
        else:
            self.is_valid = True

        if (self.target == '3' or self.target == '4') and self.text_heb == '<p>&nbsp;</p>':
            if self.text_rus != '<p>&nbsp;</p>':
                text_heb = translate_to_heb(self.text_rus)
                if text_heb:
                    self.text_heb = text_heb
                else:
                    self.is_valid = False
        
        if self.target == '1':
            if self.user:
                if self.user.target == '2' and self.text_heb == '<p>&nbsp;</p>':
                    if self.text_rus != '<p>&nbsp;</p>':
                        text_heb = translate_to_heb(self.text_rus)
                        if text_heb:
                            self.text_heb = text_heb
                        else:
                            self.is_valid = False
                
                elif self.user.target == '1' and self.text_rus == '<p>&nbsp;</p>':
                    self.is_valid = False
            else:
                self.is_valid = False
        
        if self.pk:
            if self.buttons.all():
                for button in self.buttons.all():
                    if 'https://' not in button.link:
                        self.is_valid = False
                        break

        super().save(*args, **kwargs)
        