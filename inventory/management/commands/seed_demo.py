from django.conf import settings
from django.core.management.base import BaseCommand,CommandError
from inventory.models import Vehicle
class Command(BaseCommand):
 help='Add explicitly fictional, reversible demo inventory. Never adds staff accounts.'
 def handle(self,*args,**options):
  if not settings.DEMO:raise CommandError('Demo seed is disabled after client approval.')
  for number,make,model,year,price,mileage,body,fuel in [('DEMO-001','Porsche','911 Carrera',2023,118500,12800,'Coupe','Petrol'),('DEMO-002','Mercedes-Benz','S-Class',2022,84900,24500,'Sedan','Hybrid'),('DEMO-003','Land Rover','Range Rover Sport',2023,96750,18600,'SUV','Diesel')]:
   Vehicle.objects.get_or_create(stock_number=number,defaults={'make':make,'model':model,'year':year,'price':price,'mileage':mileage,'body':body,'fuel':fuel,'transmission':'Automatic','colour':'Illustrative specification','description':'Demonstration inventory only. This is not an offer for sale. Price, mileage and specifications are fictional examples; approved vehicle photography and verified stock details must be supplied before publication.','features':'Example specification — verify against the actual vehicle','state':'available','is_demo':True,'featured':True})
  self.stdout.write(self.style.SUCCESS('Three demo records available. No client stock or accounts were created.'))
