


from django.http import HttpResponse
from hurong import models
import datetime

def delete_phone_log(request):
    now_date = datetime.date.today()
    last_there_days = (now_date - datetime.timedelta(days=2))
    objs = models.XiaohongshuPhoneLog.objects.filter(
        create_datetime__lt=last_there_days
    )
    objs.delete()

    return HttpResponse('')