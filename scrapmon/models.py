from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import subprocess
from subprocess import PIPE, STDOUT
from threading import Thread

class ScrapyScript(models.Model):
    script_name = models.CharField(max_length=250)
    project_dir = models.CharField(max_length=250, default=None, null=True)
    project_name = models.CharField(max_length=250, default=None, null=True)
    spider_name = models.CharField(max_length=250, default=None, null=True)
    created = models.DateField(auto_now=True)
    start = models.DateField()
    end = models.DateField()
    run_script = models.NullBooleanField(default=None)

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

    def __str__(self):
        return self.script.script_name


@receiver(post_save, sender=ScrapyScript)
def scrapy_log_saved(sender, instance, created, **kwargs):
    def __runtasks(instance):
        subprocess.run('cd '+instance.project_dir+' && pip install -r ../requirements.txt', shell=True, check=False, stderr=PIPE, stdout=PIPE)
        log = ScrapyLog(
            start = timezone.now(),
            script = instance,
            running = True,
            scrapylog_name = instance.spider_name+"_"+str(timezone.now())
            )
        log.save()
        command = 'cd {dir} && scrapy crawl {spider_name} -t csv --loglevel=INFO '.format(dir=instance.project_dir, spider_name=instance.spider_name)
        data = subprocess.run(command, shell=True, check=False, stderr=PIPE, stdout=PIPE)
        if data.returncode == 0:
            log.success = True
            log.running = False
            log.traceback = data.stderr.splitlines()[-23:]+data.stdout.splitlines()[-23:]
        else:
            log.success = False
            log.running = False
            log.error_message = data.stderr.splitlines()[-50:]
            log.traceback = data.stdout.splitlines()[-23:]
        log.save()
    
    if instance.run_script:
        t = Thread(target=__runtasks, args=(instance,), daemon=True)
        t.start()
        
