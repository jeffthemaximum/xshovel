from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from scraper.tasks import scrape_and_update_sheet_task
import pudb

# Create your views here.
@csrf_exempt
def new(request):
    pu.db
    name = request.POST.get('s')
    id = request.POST.get('id')
    scrape_and_update_sheet_task.delay(name, id)
    return HttpResponse('hello')