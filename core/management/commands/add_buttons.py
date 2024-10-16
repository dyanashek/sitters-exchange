from django.core.management import BaseCommand

from core.models import Button


class Command(BaseCommand):
    def handle(self, *args, **options):
        buttons = [
            ['search_job', 'Ищу работу', 'אני מחפש עבודה'],
            ['search_workers', 'Ищу сотрудников', 'אני מחפש עובדים'],
            ['yes', 'Да', 'כן'],
            ['no', 'Нет', 'לא'],
            ['confirm', 'Подтвердить', 'אשר'],
            ['cancel', 'Отменить', 'בטל'],
            ['request_phone', 'Предоставить номер 📱', 'ספק מספר 📱'],
            ['add_photo', 'Добавить фото', ''],
            ['next_step', 'К следующему шагу', 'לשלב הבא'],
            ['retype', 'Ввести заново', 'הזן מחדש'],
            ['change_cv', 'Изменить резюме', ''],
            ['enable_notifications', 'Включить уведомления', 'הפעל התראות'],
            ['disable_notifications', 'Отключить уведомления', 'כבה התראות'],
            ['searching_yes', 'Установить "ищу работу"', ''],
            ['searching_no', 'Установить "не ищу работу"', ''],
            ['main_menu', 'Главное меню 🏠', 'תפריט ראשי 🏠'],
            ['more_workers', 'Больше работников в боте', 'עוד עובדים בבוט'],
            ['more_jobs', 'Больше вакансий в боте', ''],
            ['change_data', 'Изменить данные', 'שנה את מספר הטלפון'],
            ['back', '⬅️ Назад', '⬅️ חזרה'],
            ['cooperation_proposals', 'Предложения сотрудничества', 'הצעות לשיתוף פעולה'],
            ['inbox', '📩 Входящие', '📩 דואר נכנס'],
            ['outbox', '📤 Исходящие', '📤 דואר יוצא'],
            ['jobs', 'Вакансии', 'משרות פנויות'],
            ['my_jobs', 'Мои вакансии', 'המשרות שלי'],
            ['all_jobs', 'Все вакансии', 'הכל'],
            ['jobs_suitable', 'Подходящие вакансии', ''],
            ['jobs_active', '✅ Активные', '✅ פעיל'],
            ['jobs_archive', '🗄 Архив', '🗄 ארכיון'],
            ['jobs_declined', '❌ Отклоненные', '❌ נדחו'],
            ['job_create', '➕ Добавить вакансию', '➕ הוסף משרה פנויות'],
            ['profile', '👤 Профиль', '👤 פרופיל'],
            ['reviews', '💬 Отзывы', '💬 חוות דעת'],
            ['workers', 'Работники', 'עובדים'],
            ['workers_all', 'Все работники', 'כל העובדים'],
            ['workers_suitable', 'Подходящие работники', 'עובדים מתאימים'],
            ['activate', 'Активировать', 'הפעל'],
            ['deactivate', 'Деактивировать', 'השבת'],
            ['view', '👁 Посмотреть', '👁 צפה'],
            ['make_proposal', 'Предложить сотрудничество', 'הצע שיתוף פעולה'],
            ['view_proposal', '👁 Посмотреть отправленный отклик', '👁 צפה בתגובה שנשלחה'],
            ['resend_proposal', 'Предложить повторно', 'הצע שוב'],
            ['accept', '✅ Принять', '✅ קבל'],
            ['decline', '❌ Отклонить', '❌ דחה'],
            ['view_employer_jobs', '👁 Посмотреть вакансии работодателя', ''],
            ['add_review', '💬 Оставить отзыв', '💬 השאר חוות דעת'],
            ['view_reviews', '💬 Посмотреть отзывы', '💬 צפה בחוות דעת'],
            ['permanent', 'Постоянная', 'קבועה'],
            ['temporary', 'Временная', 'זמנית'],
        ]
        for item in buttons:
            slug = item[0]
            text_rus = item[1]
            text_heb = item[2]

            prev_text = Button.objects.filter(slug=slug).first()
            if not prev_text:
                my_order = Button.objects.count()
                new_text = Button(slug=slug, rus=text_rus, heb=text_heb, my_order=my_order)
                new_text.save()
                print(f'Создан текст {slug}: {text_rus}\n{text_heb}')
            else:
                if prev_text.rus != text_rus:
                    prev_text.rus = text_rus
                    prev_text.save()
                    print(f'{slug}: заменен русский текст')

                if prev_text.heb != text_heb:
                    prev_text.heb = text_heb
                    prev_text.save()
                    print(f'{slug}: заменен текст на иврите')
        
        print('done')

