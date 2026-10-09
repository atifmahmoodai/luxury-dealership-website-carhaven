from django.conf import settings
def brand(request):
 return {'brand':{'name':settings.SITE_NAME,'demo':settings.DEMO,'origin':settings.SITE_ORIGIN,'email':settings.CONTACT_EMAIL,'phone':settings.CONTACT_PHONE,'whatsapp':settings.WHATSAPP,'address':settings.ADDRESS,'about':settings.COMPANY_ABOUT,'currency':settings.CURRENCY},'canonical':settings.SITE_ORIGIN+request.path}
