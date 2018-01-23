from django.contrib import admin
from .models import ScrapyScript, ScrapyLog, ScrapyScriptForm


@admin.register(ScrapyScript)
class ScrapyScriptAdmin(admin.ModelAdmin):
    list_display = ('id', 'script_name', 'project_name', 'spider_name')
    form = ScrapyScriptForm

@admin.register(ScrapyLog)
class ScrapyLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'scrapylog_name', 'start', 'end', 'running', 'success', 'error_message', 'traceback')
    list_filter = ['success', 'start']

    '''disable add, it will retrieve automatically'''
    def has_add_permission(self, request):
        return False


