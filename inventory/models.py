import uuid
from io import BytesIO
from PIL import Image,ImageOps,UnidentifiedImageError
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator,MaxValueValidator
from django.urls import reverse
Image.MAX_IMAGE_PIXELS=40_000_000

class Vehicle(models.Model):
 class State(models.TextChoices):
  DRAFT='draft','Draft'
  AVAILABLE='available','Available'
  RESERVED='reserved','Reserved'
  SOLD='sold','Sold'
  ARCHIVED='archived','Archived'
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
 stock_number=models.CharField(max_length=30,unique=True)
 make=models.CharField(max_length=60)
 model=models.CharField(max_length=90)
 year=models.PositiveSmallIntegerField(validators=[MinValueValidator(1900),MaxValueValidator(2100)])
 price=models.DecimalField(max_digits=12,decimal_places=2,validators=[MinValueValidator(0)])
 mileage=models.PositiveIntegerField(help_text='Odometer reading in kilometres.')
 body=models.CharField(max_length=20,choices=[(x,x) for x in ['Coupe','Sedan','SUV','Convertible','Wagon','Hatchback']])
 transmission=models.CharField(max_length=20,choices=[('Automatic','Automatic'),('Manual','Manual')])
 fuel=models.CharField(max_length=20,choices=[(x,x) for x in ['Petrol','Diesel','Hybrid','Electric']])
 colour=models.CharField(max_length=40)
 description=models.TextField(max_length=6000)
 features=models.TextField(blank=True,max_length=3000,help_text='One verified feature per line.')
 state=models.CharField(max_length=12,choices=State.choices,default=State.DRAFT,db_index=True)
 featured=models.BooleanField(default=False)
 is_demo=models.BooleanField(default=False,help_text='Illustrative inventory. Excluded from production browsing.')
 created_at=models.DateTimeField(auto_now_add=True)
 updated_at=models.DateTimeField(auto_now=True)
 class Meta:
  ordering=['-featured','-created_at']
  constraints=[models.CheckConstraint(condition=models.Q(price__gte=0),name='nonnegative_price')]
 def __str__(self):return f'{self.year} {self.make} {self.model}'
 def get_absolute_url(self):return reverse('vehicle',args=[self.id])
 def clean(self):
  if self.state in ('available','reserved','sold') and not self.is_demo and not self.photos.exists():raise ValidationError('Save as Draft, add approved photos, then publish.')
  if not settings.DEMO and self.is_demo and self.state!='draft':raise ValidationError('Demo inventory cannot be published in production.')
 @property
 def feature_list(self):return [s.strip() for s in self.features.splitlines() if s.strip()]

class Photo(models.Model):
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
 vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE,related_name='photos')
 image=models.ImageField(upload_to='vehicles/')
 alt=models.CharField(max_length=180,help_text='Describe the vehicle and angle, e.g. front three-quarter view.')
 position=models.PositiveSmallIntegerField(default=0)
 class Meta:ordering=['position','id']
 def __str__(self):return self.alt
 def clean(self):
  if not self.image or self.image._committed:return
  if self.image.size>8*1024*1024:raise ValidationError('Image must be under 8 MB.')
  try:
   self.image.seek(0)
   with Image.open(self.image) as source:
    if source.width*source.height>40_000_000:raise ValidationError('Image exceeds 40 megapixels.')
    if source.format not in ('JPEG','PNG','WEBP') or getattr(source,'n_frames',1)>1:raise ValidationError('Use a single-frame JPEG, PNG or WebP.')
    source.load();image=ImageOps.exif_transpose(source).convert('RGB');image.thumbnail((2400,1800));output=BytesIO();image.save(output,'JPEG',quality=88,optimize=True)
   self.image=ContentFile(output.getvalue(),name=f'{uuid.uuid4()}.jpg')
  except (UnidentifiedImageError,OSError,Image.DecompressionBombError,Image.DecompressionBombWarning) as e:raise ValidationError('Invalid image or image exceeds 40 megapixels.') from e
 def save(self,*args,**kwargs):self.full_clean();return super().save(*args,**kwargs)
 def get_absolute_url(self):return reverse('photo',args=[self.id])

class Enquiry(models.Model):
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
 vehicle=models.ForeignKey(Vehicle,on_delete=models.SET_NULL,null=True,blank=True)
 name=models.CharField(max_length=100)
 email=models.EmailField()
 phone=models.CharField(max_length=40,blank=True)
 message=models.TextField(max_length=3000)
 consent=models.BooleanField()
 state=models.CharField(max_length=20,choices=[('new','New'),('contacted','Contacted'),('closed','Closed')],default='new')
 staff_notes=models.TextField(blank=True)
 created_at=models.DateTimeField(auto_now_add=True)
 class Meta:ordering=['-created_at']
 def __str__(self):return f'{self.name} · {self.created_at:%Y-%m-%d}' if self.created_at else self.name

class Throttle(models.Model):
 key=models.CharField(max_length=64,primary_key=True)
 count=models.PositiveIntegerField(default=0)
 expires_at=models.DateTimeField()
