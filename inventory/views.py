import uuid
from decimal import Decimal,InvalidOperation
from django.conf import settings
from django.core import signing
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse,FileResponse,Http404
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.views.decorators.http import require_GET,require_http_methods
from django.utils.html import escape
from .models import Vehicle,Photo,Enquiry
from .forms import EnquiryForm
from .middleware import allowed

def collection():
 qs=Vehicle.objects.filter(state__in=['available','reserved','sold']).prefetch_related('photos')
 if settings.DEMO:return qs.filter(Q(is_demo=True)|Q(photos__isnull=False)).distinct()
 return qs.filter(is_demo=False,photos__isnull=False).distinct()
@require_GET
def home(request):return render(request,'home.html',{'vehicles':collection().filter(state='available')[:3],'title':'Drive away with confidence','description':'Explore the CarHaven collection and arrange a personal viewing.'})
@require_GET
def inventory(request):
 qs=collection().exclude(state='sold');error=''
 make=request.GET.get('make','')[:60];body=request.GET.get('body','')[:20];search=request.GET.get('q','')[:100]
 if make:qs=qs.filter(make=make)
 if body:qs=qs.filter(body=body)
 if search:qs=qs.filter(Q(make__icontains=search)|Q(model__icontains=search)|Q(stock_number__icontains=search))
 maximum=request.GET.get('max_price','')
 if maximum:
  try:
   amount=Decimal(maximum)
   if not amount.is_finite() or amount<0 or amount>9999999999:raise InvalidOperation
   qs=qs.filter(price__lte=amount)
  except InvalidOperation:error='Enter a valid maximum price.';qs=qs.none()
 sort=request.GET.get('sort','newest');ordering={'newest':'-created_at','price_low':'price','price_high':'-price','mileage':'mileage'}.get(sort,'-created_at');qs=qs.order_by(ordering,'id')
 page=Paginator(qs,9).get_page(request.GET.get('page'))
 query=request.GET.copy();query.pop('page',None)
 return render(request,'inventory.html',{'vehicles':page,'page':page,'query':query.urlencode(),'makes':collection().values_list('make',flat=True).distinct().order_by('make'),'bodies':['Coupe','Sedan','SUV','Convertible','Wagon','Hatchback'],'error':error,'title':'The collection','description':'Browse vehicle specifications, pricing and availability in the CarHaven collection.'})
@require_GET
def vehicle(request,pk):
 car=get_object_or_404(collection(),pk=pk)
 return render(request,'vehicle.html',{'car':car,'title':str(car),'description':car.description[:160]})
@require_GET
def photo(request,pk):
 item=get_object_or_404(Photo,pk=pk)
 if not collection().filter(pk=item.vehicle_id).exists() and not (request.user.is_active and request.user.has_perm('inventory.view_vehicle')):raise Http404
 try:response=FileResponse(item.image.open('rb'),content_type='image/jpeg')
 except FileNotFoundError:raise Http404
 response['Content-Disposition']='inline; filename="vehicle.jpg"'
 response['Cache-Control']='private, no-store'
 return response
@require_GET
def stored_photo(request,filename):
 item=get_object_or_404(Photo,image='vehicles/'+filename)
 return photo(request,item.pk)
@require_GET
def about(request):return render(request,'about.html',{'title':'A considered approach','description':'Meet CarHaven and learn how to arrange your next vehicle viewing.'})
@require_GET
def privacy(request):return render(request,'privacy.html',{'title':'Privacy notice','description':'How CarHaven handles vehicle enquiries and staff access.'})
@require_http_methods(['GET','POST'])
def contact(request):
 car=None;key=request.GET.get('vehicle')
 if key:
  try:car=get_object_or_404(collection().exclude(state='sold'),pk=uuid.UUID(key))
  except ValueError:raise Http404
 if request.method=='POST':
  if not allowed(request,'enquiry',10):return HttpResponse('Too many enquiries. Please wait 15 minutes.',status=429)
  form=EnquiryForm(request.POST)
  if form.is_valid():
   try:
    payload=signing.loads(form.cleaned_data['token'],salt='enquiry',max_age=86400)
    if payload.get('vehicle')!=(str(car.id) if car else None) or form.cleaned_data['website']:raise signing.BadSignature
    enquiry_id=uuid.UUID(payload['id'])
   except (signing.BadSignature,ValueError,KeyError):form.add_error(None,'This form has expired. Reload the page and try again.')
   else:
    values={k:form.cleaned_data[k] for k in ['name','email','phone','message','consent']};values['vehicle']=car
    Enquiry.objects.get_or_create(id=enquiry_id,defaults=values)
    request.session['received_enquiry']=str(enquiry_id)
    return redirect('thanks')
 else:
  form=EnquiryForm(initial={'token':signing.dumps({'id':str(uuid.uuid4()),'vehicle':str(car.id) if car else None},salt='enquiry')})
 return render(request,'contact.html',{'form':form,'car':car,'title':'Start a conversation','description':'Ask about a vehicle or request a personal viewing.'},status=400 if request.method=='POST' else 200)
@require_GET
def thanks(request):
 if not request.session.get('received_enquiry'):return redirect('contact')
 return render(request,'thanks.html',{'title':'Enquiry received','description':'Your enquiry has been recorded for the dealership team.'})
@require_GET
def robots(request):return HttpResponse('User-agent: *\n'+('Disallow: /\n' if settings.DEMO else 'Disallow: /staff/\nDisallow: /contact/\nSitemap: '+settings.SITE_ORIGIN+'/sitemap.xml\n'),content_type='text/plain')
@require_GET
def sitemap(request):
 paths=[] if settings.DEMO else ['/',reverse('inventory'),reverse('about'),reverse('contact')]+[v.get_absolute_url() for v in collection()]
 xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{escape(settings.SITE_ORIGIN+p)}</loc></url>' for p in paths)+'</urlset>'
 return HttpResponse(xml,content_type='application/xml')
@require_GET
def health(request):
 from django.db import connection
 with connection.cursor() as cursor:cursor.execute('SELECT 1')
 return HttpResponse('ok',content_type='text/plain')
