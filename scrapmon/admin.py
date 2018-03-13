from django.contrib import admin
from .models import ScrapyScript, ScrapyLog, ScrapyScriptForm,  ScrapyerBatch, ScrapyerBatchScript, ScrapyerBatchForm


@admin.register(ScrapyScript)
class ScrapyScriptAdmin(admin.ModelAdmin):
    def edit(self, obj):
        return format_html('<a class="btn" href="/admin/scrapmon/scrapyscript/{}/change/">Change</a>', obj.id)

    def delete(self, obj):
        return format_html('<a class="btn" href="/admin/scrapmon/scrapyscript/{}/delete/">Delete</a>', obj.id)

    list_display = ('id', 'script_name', 'project_name', 'spider_name','edit', 'delete')
    form = ScrapyScriptForm

@admin.register(ScrapyLog)
class ScrapyLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'scrapylog_name', 'start', 'end', 'running', 'success', 'error_message', 'traceback')
    list_filter = ['success', 'start']

    '''disable add, it will retrieve automatically'''
    def has_add_permission(self, request):
        return False

    def has_edit_permission(self, request):
        return True


class ScrapyerBatchScriptInline(admin.StackedInline):
    model = ScrapyerBatchScript
    extra = 1

@admin.register(ScrapyerBatch)
class ScrapyerBatchAdmin(admin.ModelAdmin):
    def edit(self, obj):
        return format_html('<a class="btn" href="/admin/scrapmon/scrapyerbatch/{}/change/">Change</a>', obj.id)

    def delete(self, obj):
        return format_html('<a class="btn" href="/admin/scrapmon/scrapyerbatch/{}/delete/">Delete</a>', obj.id)

    list_display = ('batch_name','edit', 'delete')

    inlines = [ScrapyerBatchScriptInline]
    form = ScrapyerBatchForm


