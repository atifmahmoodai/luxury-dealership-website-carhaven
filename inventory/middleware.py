import hashlib
from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from .models import Throttle
def allowed(request,scope,limit):
 ip=request.META.get('REMOTE_ADDR','unknown')
 # The bundled reverse proxy overwrites this header. Trust only in an isolated proxy deployment.
 if settings.SECURE_PROXY_SSL_HEADER:ip=request.META.get('HTTP_X_REAL_IP',ip)
 key=hashlib.sha256((settings.SECRET_KEY+scope+ip).encode()).hexdigest()
 now=timezone.now()
 with transaction.atomic():
  row,_=Throttle.objects.get_or_create(key=key,defaults={'expires_at':now+timedelta(minutes=15)})
  row=Throttle.objects.select_for_update().get(pk=key)
  if row.expires_at<now:row.count=0;row.expires_at=now+timedelta(minutes=15)
  row.count+=1;row.save()
  return row.count<=limit
class Protection:
 def __init__(self,get_response):self.get_response=get_response
 def __call__(self,request):
  if request.method=='POST' and request.path=='/staff/login/' and not allowed(request,'login',25):return HttpResponse('Too many attempts. Try again in 15 minutes.',status=429)
  response=self.get_response(request)
  response['X-Content-Type-Options']='nosniff'
  if not request.path.startswith('/staff/'):
   response['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
  if request.path.startswith(('/staff/','/contact/')):response['Cache-Control']='no-store'
  if settings.DEMO:response['X-Robots-Tag']='noindex, nofollow'
  return response
