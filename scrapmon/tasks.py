from django.utils import timezone
import subprocess
from subprocess import PIPE, STDOUT
from celery.task import task
from .models import ScrapyScript, ScrapyLog

@task(ignore_result=True, max_retries=1)
def execute_scrapy(command, script_id):
    print("Executing Command %s :", command)
    script = ScrapyScript.objects.get(pk = script_id)
    log = ScrapyLog(
        start = timezone.now(),
        script = script,
        running = True,
        scrapylog_name = script.spider_name+"_"+str(timezone.now().strftime('%Y%m'))
        )
    log.save()

    data = subprocess.run(command, shell=True, check=False, stderr=PIPE, stdout=PIPE, executable='/bin/bash')
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
