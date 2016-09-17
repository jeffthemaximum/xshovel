from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from scraper.tasks import scrape_and_update_sheet_task
from channels import Channel
import pudb

# Create your views here.
@csrf_exempt
def new(request):
    name = {
        'sheet_name': request.POST.get('name')
    }
    Channel('scrape_wiley_by_sheet_name').send(name)
    return HttpResponse('hello')