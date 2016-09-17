from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from scraper.tasks import scrape_and_update_sheet_task
from channels import Channel
from scraper.models import Scrape
import pudb

# Create your views here.
@csrf_exempt
def new(request):
    scrape = Scrape(name=request.POST.get('name'))
    scrape.save()
    name = {
        'sheet_name': scrape.name,
        'sheet_id': scrape.id
    }
    Channel('scrape_wiley_by_sheet_name').send(name)
    return HttpResponse('hello')