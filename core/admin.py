from django.contrib import admin
from django.db.models import Q
from adminsortable2.admin import SortableAdminMixin

from core.models import (Text, Button, TGUser, Worker, 
                         Employer, Job, WorkerReview, EmployerReview,
                         ChannelForWorkers, ChannelForEmployers,
                         WorkerCooperationProposal, EmployerCooperationProposal,)


@admin.register(Text)
class TextAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('rus', 'heb', 'my_order',)
    search_fields = ('slug', 'rus', 'heb',)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.slug:
            return ('slug',)
        return []


@admin.register(Button)
class ButtonAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('rus', 'heb', 'my_order',)
    search_fields = ('slug', 'rus', 'heb',)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.slug:
            return ('slug',)
        return []


@admin.register(TGUser)
class TGUserAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'target', 'created_at',)
    list_filter = ('target',)
    search_fields = ('tg_id',)

    def has_module_permission(self, request):
        return False


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('final_min_salary', 'created_at', 'is_searching', 'is_approved', 'get_thumbnail')
    list_filter = ('areas', 'is_searching', 'is_approved',)
    search_fields = ('tg_id', 'phone', 'username',)

    def final_min_salary(self, obj):
        return f'{obj.min_salary}₪'

    final_min_salary.short_description = 'минимальная зарплата'

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'username', 'phone', 'created_at', 'are_active_jobs',)
    search_fields = ('tg_id', 'phone', 'username',)

    def are_active_jobs(self, obj):
        jobs = obj.jobs.filter(Q(is_active=True) & Q(is_approved=True)).all()

        if jobs:
            return True
        return False
    
    are_active_jobs.short_description = 'Есть активные вакансии?'
    are_active_jobs.boolean = True


@admin.register(ChannelForWorkers)
class ChannelForWorkersAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active',)
    list_filter = ('is_active',)


@admin.register(ChannelForEmployers)
class ChannelForEmployersAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active',)
    list_filter = ('is_active',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('final_min_salary', 'created_at', 'is_approved', 'is_active')
    list_filter = ('areas', 'is_active', 'is_approved',)

    def final_min_salary(self, obj):
        return f'{obj.min_salary}₪'

    final_min_salary.short_description = 'минимальная зарплата'


@admin.register(WorkerCooperationProposal)
class WorkerCooperationProposalAdmin(admin.ModelAdmin):
    list_display = ('worker_phone', 'employer_phone', 'created_at', 'is_accepted', 'is_proceeded')
    list_filter = ('is_accepted', 'is_proceeded',)

    def worker_min_salary(self, obj):
        return f'{obj.worker.min_salary}₪'
    
    def job_min_salary(self, obj):
        return f'{obj.job.min_salary}₪'

    def worker_phone(self, obj):
        return str(obj.worker.phone)
    
    def employer_phone(self, obj):
        return str(obj.employer.phone)

    worker_min_salary.short_description = 'Зарплата от (сотрудник)'
    job_min_salary.short_description = 'Зарплата от (вакансия)'
    worker_phone.short_description = 'Телефон работника'
    employer_phone.short_description = 'Телефон работодателя'


@admin.register(EmployerCooperationProposal)
class EmployerCooperationProposalAdmin(admin.ModelAdmin):
    list_display = ('worker_phone', 'employer_phone', 'created_at', 'is_accepted', 'is_proceeded')
    list_filter = ('is_accepted', 'is_proceeded',)

    def worker_min_salary(self, obj):
        return f'{obj.worker.min_salary}₪'

    def worker_phone(self, obj):
        return str(obj.worker.phone)
    
    def employer_phone(self, obj):
        return str(obj.employer.phone)

    worker_min_salary.short_description = 'Зарплата от (сотрудник)'
    worker_phone.short_description = 'Телефон работника'
    employer_phone.short_description = 'Телефон работодателя'



@admin.register(WorkerReview)
class WorkerReviewAdmin(admin.ModelAdmin):
    list_display = ('rate', 'created_at', 'is_approved',)
    list_filter = ('is_approved',)


@admin.register(EmployerReview)
class EmployerReviewAdmin(admin.ModelAdmin):
    list_display = ('rate', 'created_at', 'is_approved',)
    list_filter = ('is_approved',)
