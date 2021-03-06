from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import subprocess
from subprocess import PIPE, STDOUT
from threading import Thread
from django import forms
from django_currentuser.middleware import get_current_user, get_current_authenticated_user

class ScrapyScript(models.Model):
    script_name = models.CharField(max_length=250)
    project_dir = models.CharField(max_length=250, default=None, null=True)
    project_name = models.CharField(max_length=250, default=None, null=True)
    spider_name = models.CharField(max_length=250, default=None, null=True)
    created = models.DateField(auto_now=True)
    start = models.DateField()
    end = models.DateField()
    run_script = models.NullBooleanField(default=None)
    enviroment = models.CharField(max_length=250, default='staging', null=True)
    recreate = models.NullBooleanField("Overwrite Existing ?",default=False)
    sites_new = models.TextField(default=None, null=True)
    virtualenv = models.TextField(default=None, null=True)


    def __str__(self):
        return self.script_name

class ScrapyLog(models.Model):
    created = models.DateField(auto_now=True)
    start = models.DateTimeField()
    end = models.DateTimeField(auto_now=True)
    script = models.ForeignKey(ScrapyScript, on_delete=models.CASCADE)
    success = models.NullBooleanField(default=None)
    error_message = models.TextField(blank=True, null=True)
    traceback = models.TextField(blank=True, null = True)
    scrapylog_name = models.CharField(max_length=200)
    running = models.NullBooleanField(default=None)
    created_by = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.script.script_name

class ScrapyerBatch(models.Model):
    batch_name = models.CharField(max_length=250, null=False)
    sites_new = models.TextField(default=None, null=True)
    start = models.DateField()
    end = models.DateField()
    enviroment = models.CharField(max_length=250, default='staging', null=True)
    run_script = models.NullBooleanField(default=None)
    recreate = models.BooleanField("Overwrite Existing?", default=False)
    comment = models.TextField(blank=True, null=True, default=None)

    def __str__(self):
        return self.batch_name

    class Meta:
        verbose_name = "Scrapyer batch"
        verbose_name_plural = "Scrapyer batches"

class ScrapyerBatchScript(models.Model):
    batch = models.ForeignKey(ScrapyerBatch, on_delete=models.CASCADE, related_name="batch_script")
    script = models.ForeignKey(ScrapyScript, on_delete=models.CASCADE)
    order = models.IntegerField()


@receiver(post_save, sender=ScrapyScript)
def scrapy_log_saved(sender, instance, created, **kwargs):
    def __runtasks(instance, log):

        command = ''
        if instance.sites_new is None or not instance.sites_new.strip() :
            command = '{venv} && cd {dir} && SCRAPYER_ENV={env} scrapy crawl {spider_name} -a recreate={recreate} -a start_date={start_date} -a end_date={end_date} -t csv --loglevel=INFO --logfile=/var/apps/a/data-scrapyer/shared/log/{logfile}.log'.format(env=instance.enviroment, dir=instance.project_dir, spider_name=instance.spider_name, recreate=instance.recreate, start_date=instance.start.strftime('%Y-%m-%d'), end_date=instance.end.strftime('%Y-%m-%d'), venv=instance.virtualenv, logfile=instance.spider_name+instance.start.strftime('%Y%m'))
        else:
            command = '{venv} && cd {dir} && SCRAPYER_ENV={env} scrapy crawl {spider_name} -a recreate={recreate} -a sites_new={sites_new} -a start_date={start_date} -a end_date={end_date} -t csv --loglevel=INFO --logfile=/var/apps/a/data-scrapyer/shared/log/{logfile}.log '.format(env=instance.enviroment, dir=instance.project_dir, spider_name=instance.spider_name, sites_new=instance.sites_new, recreate=instance.recreate, start_date=instance.start.strftime('%Y-%m-%d'), end_date=instance.end.strftime('%Y-%m-%d'), venv=instance.virtualenv, logfile=instance.spider_name+instance.start.strftime('%Y%m'))

        data = subprocess.run(command, shell=True, check=False, stderr=PIPE, stdout=PIPE, executable='/bin/bash')

        if data.returncode == 0:
            log.success = True
            log.running = False
            log.traceback = data.stderr.splitlines()[-10:]+data.stdout.splitlines()[-10:]
        else:
            log.success = False
            log.running = False
            log.error_message = data.stderr.splitlines()[-10:]
            log.traceback = data.stdout.splitlines()[-10:]
        log.save()
    
    if instance.run_script:
        # __runtasks(instance)
        log = ScrapyLog(
            start = timezone.now(),
            script = instance,
            running = True,
            scrapylog_name = instance.spider_name+"_"+str(instance.start.strftime('%Y%m'))+"_"+str(timezone.now().strftime('%Y%m')),
            created_by = get_current_user().username
            )
        log.save()

        t = Thread(target=__runtasks, args=(instance,log), daemon=True)
        t.start()

@receiver(post_save, sender=ScrapyerBatch)
def scrapyer_batch_saved(sender, instance, created, **kwargs):

    def __runjob(script, username):
        ## retrieve script
        for batch_script in ScrapyerBatchScript.objects.filter(batch=script).order_by('order'):
            instance = batch_script.script
            log = ScrapyLog(
                start = timezone.now(),
                script = instance,
                running = True,
                scrapylog_name = instance.spider_name+"_"+str(script.start.strftime('%Y%m'))+"_"+str(timezone.now().strftime('%Y%m')),
                created_by = username
                )
            log.save()

            command = ''
            if script.sites_new is None or not script.sites_new.strip() :
                command = '{venv} && cd {dir} && SCRAPYER_ENV={env} scrapy crawl {spider_name} -a recreate={recreate} -a start_date={start_date} -a end_date={end_date} -t csv --loglevel=INFO --logfile=/var/apps/a/data-scrapyer/shared/log/{logfile}.log'.format(env=script.enviroment, dir=instance.project_dir, spider_name=instance.spider_name, recreate=script.recreate, start_date=script.start.strftime('%Y-%m-%d'), end_date=script.end.strftime('%Y-%m-%d'), venv=instance.virtualenv, logfile=instance.spider_name+script.start.strftime('%Y%m'))
            else:
                command = '{venv} && cd {dir} && SCRAPYER_ENV={env} scrapy crawl {spider_name} -a recreate={recreate} -a sites_new={sites_new} -a start_date={start_date} -a end_date={end_date} -t csv --loglevel=INFO --logfile=/var/apps/a/data-scrapyer/shared/log/{logfile}.log '.format(env=script.enviroment, dir=instance.project_dir, spider_name=instance.spider_name, sites_new=script.sites_new, recreate=script.recreate, start_date=script.start.strftime('%Y-%m-%d'), end_date=script.end.strftime('%Y-%m-%d'), venv=instance.virtualenv, logfile=instance.spider_name+script.start.strftime('%Y%m'))

            data = subprocess.run(command, shell=True, check=False, stderr=PIPE, stdout=PIPE, executable='/bin/bash')

            if data.returncode == 0:
                log.success = True
                log.running = False
                log.traceback = data.stderr.splitlines()[-10:]+data.stdout.splitlines()[-10:]
            else:
                log.success = False
                log.running = False
                log.error_message = data.stderr.splitlines()[-10:]
                log.traceback = data.stdout.splitlines()[-10:]
            log.save()

    if instance.run_script:
        username = get_current_user().username
        t = Thread(target=__runjob, args=(instance, username,), daemon=True)
        t.start()

'''This for set environemnt as options select'''
class ScrapyScriptForm(forms.ModelForm):
    env_types = (
        ('staging', 'staging'),
        ('production', 'production'),
    )
    enviroment = forms.ChoiceField(choices=env_types)
    sites_new = forms.CharField(widget=forms.Textarea, required=False)
    virtualenv = forms.CharField(widget=forms.Textarea, required=False)

    recreate_types = (
        (False, False),
        (True, True),
    )
    recreate = forms.ChoiceField(choices=recreate_types, label='Overwrite Existing?')
    run_script = forms.BooleanField(required=False, widget=forms.HiddenInput())

class ScrapyerBatchForm(forms.ModelForm):
    sites_new = forms.CharField(widget=forms.Textarea, required=False)
    run_script = forms.BooleanField(required=False, widget=forms.HiddenInput())
    recreate_types = (
        (False, False),
        (True, True),
    )
    recreate = forms.ChoiceField(choices=recreate_types, label='Overwrite Existing?')
