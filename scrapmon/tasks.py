from django.utils import timezone
import subprocess
from subprocess import PIPE, STDOUT
from celery.task import task
from .models import ScrapyScript, ScrapyLog

@task(ignore_result=True, max_retries=1)
def execute_scrapy():
    index = 0
    for script in ScrapyScript.objects.all():
        if index == 0:
            prerequisite(script.project_dir)

        log = ScrapyLog(
            start = timezone.now(),
            script = script,
            running = True,
            scrapylog_name = script.spider_name+"_"+str(timezone.now())
            )
        log.save()
        command = 'cd {dir} && scrapy crawl {spider_name} -t csv --loglevel=INFO '.format(dir=script.project_dir, spider_name=script.spider_name)
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
        index +=1

def prerequisite(project_dir):
    subprocess.run('cd '+project_dir+' && pip install -r ../requirements.txt', shell=True, check=False, stderr=PIPE, stdout=PIPE)