from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from scraper.tasks import scrape_and_update_sheet_task
from channels import Channel
from scraper.models import Scrape
from django.shortcuts import get_object_or_404
import pudb

# Create your views here.
@csrf_exempt
def new(request):
    scrape = Scrape(name=request.POST.get('name'))
    scrape.save()
    name = {
        'sheet_name': scrape.name,
        'scrape_id': scrape.id
    }
    Channel('scrape_wiley_by_sheet_name').send(name)
    return redirect('scraper:show', scrape_id=scrape.id)

def show(request, scrape_id):
    scrape = get_object_or_404(Scrape, pk=scrape_id)
    context = { 
        'scrape': scrape 
    }
    return render(request, 'show.html', context)