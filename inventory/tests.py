import tempfile,uuid
from io import BytesIO
from pathlib import Path
from PIL import Image
from django.test import TestCase,Client,override_settings
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Vehicle,Photo,Enquiry

class InventoryTests(TestCase):
 def setUp(self):
  self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
  self.override=override_settings(MEDIA_ROOT=Path(self.directory.name));self.override.enable();self.addCleanup(self.override.disable)
  self.car=Vehicle.objects.create(stock_number='TEST-1',make='Example',model='Tourer',year=2024,price='50000.00',mileage=2500,body='Coupe',fuel='Petrol',transmission='Automatic',colour='Silver',description='A fictional test vehicle.')
 def image(self):
  stream=BytesIO();Image.new('RGB',(640,400),'#789177').save(stream,'PNG');return SimpleUploadedFile('car.png',stream.getvalue(),content_type='image/png')
 def publish(self):
  photo=Photo.objects.create(vehicle=self.car,image=self.image(),alt='Fictional vehicle side view')
  self.car.state='available';self.car.full_clean();self.car.save();return photo
 def test_drafts_and_their_photos_are_private(self):
  photo=Photo.objects.create(vehicle=self.car,image=self.image(),alt='Draft photo')
  self.assertEqual(self.client.get(self.car.get_absolute_url()).status_code,404)
  self.assertEqual(self.client.get(photo.get_absolute_url()).status_code,404)
  self.assertEqual(self.client.get(photo.image.url).status_code,404)
  self.assertNotContains(self.client.get('/collection/'),'Tourer')
 def test_photo_required_before_publishing_and_image_normalization(self):
  self.car.state='available'
  with self.assertRaises(ValidationError):self.car.full_clean()
  photo=self.publish();self.assertTrue(photo.image.name.endswith('.jpg'))
  with Image.open(photo.image.path) as image:self.assertEqual(image.format,'JPEG');self.assertFalse(image.getexif())
  self.assertEqual(self.client.get(photo.get_absolute_url()).status_code,200)
  self.assertEqual(self.client.get(photo.image.url).status_code,200)
 def test_invalid_images_and_bad_price_are_rejected(self):
  with self.assertRaises(ValidationError):Photo.objects.create(vehicle=self.car,image=SimpleUploadedFile('x.jpg',b'<script>bad</script>'),alt='Invalid')
  self.car.price=-1
  with self.assertRaises(ValidationError):self.car.full_clean()
 def test_inventory_search_filters_and_reserved_state(self):
  self.publish()
  self.assertContains(self.client.get('/collection/?q=Tourer'),'Tourer')
  self.assertNotContains(self.client.get('/collection/?max_price=1'),'Explore Example')
  self.assertContains(self.client.get('/collection/?max_price=NaN'),'Enter a valid maximum price')
  self.assertContains(self.client.get('/collection/?make=Example&body=Coupe'),'Tourer')
  self.car.state='reserved';self.car.save();self.assertContains(self.client.get(self.car.get_absolute_url()),'Reserved')
 def test_archived_and_demo_stock_hidden_from_live_collection(self):
  self.publish();self.car.is_demo=True;self.car.save()
  with override_settings(DEMO=False):self.assertEqual(self.client.get(self.car.get_absolute_url()).status_code,404);self.assertNotContains(self.client.get('/sitemap.xml'),str(self.car.id))
  self.car.state='archived';self.car.save();self.assertEqual(self.client.get(self.car.get_absolute_url()).status_code,404)
 def test_staff_permission_and_admin_audit(self):
  user=User.objects.create_user('limited',password='Fictional-testing-password-27!',is_staff=True)
  self.client.force_login(user)
  self.assertEqual(self.client.get(reverse('admin:inventory_vehicle_change',args=[self.car.pk])).status_code,403)
  self.client.logout();self.assertEqual(self.client.get('/staff/').status_code,302)
 def test_enquiry_persists_once_and_does_not_send_email(self):
  self.publish();url='/contact/?vehicle='+str(self.car.id)
  token=self.client.get(url).context['form'].initial['token']
  data={'name':'Fictional Buyer','email':'buyer@example.test','phone':'','message':'Please discuss a viewing.','consent':'on','token':token}
  self.assertRedirects(self.client.post(url,data),'/contact/received/')
  self.assertEqual(Enquiry.objects.count(),1);self.assertEqual(Enquiry.objects.first().vehicle,self.car)
  self.client.post(url,data);self.assertEqual(Enquiry.objects.count(),1)
  from django.core import mail
  self.assertEqual(len(mail.outbox),0)
 def test_consent_tampered_token_honeypot_and_csrf(self):
  token=self.client.get('/contact/').context['form'].initial['token'];data={'name':'Fictional','email':'buyer@example.test','message':'Hello','token':token}
  self.assertEqual(self.client.post('/contact/',data).status_code,400)
  data['consent']='on';data['token']='tampered';self.assertEqual(self.client.post('/contact/',data).status_code,400)
  data['token']=token;data['website']='spam';self.assertEqual(self.client.post('/contact/',data).status_code,400)
  self.assertEqual(Client(enforce_csrf_checks=True).post('/contact/',data).status_code,403)
  self.assertEqual(Enquiry.objects.count(),0)
 def test_enquiry_abuse_limit(self):
  for _ in range(10):self.client.post('/contact/',{})
  self.assertEqual(self.client.post('/contact/',{}).status_code,429)
 def test_sitemap_and_security_headers(self):
  self.publish();response=self.client.get('/');self.assertIn('noindex',response['X-Robots-Tag']);self.assertIn("frame-ancestors 'none'",response['Content-Security-Policy'])
  self.assertContains(self.client.get('/robots.txt'),'Disallow: /')
  with override_settings(DEMO=False):self.assertContains(self.client.get('/sitemap.xml'),self.car.get_absolute_url())
  self.assertRedirects(self.client.get('/contact/received/'),'/contact/')
