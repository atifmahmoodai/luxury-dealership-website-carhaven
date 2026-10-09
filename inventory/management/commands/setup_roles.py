from django.contrib.auth.models import Group,Permission
from django.core.management.base import BaseCommand
class Command(BaseCommand):
 help='Create the Inventory team role without creating accounts.'
 def handle(self,*args,**options):
  group,_=Group.objects.get_or_create(name='Inventory team')
  names=['view_vehicle','add_vehicle','change_vehicle','view_photo','add_photo','change_photo','delete_photo','view_enquiry','change_enquiry']
  group.permissions.set(Permission.objects.filter(content_type__app_label='inventory',codename__in=names))
  self.stdout.write('Inventory team permissions configured. Assign the group and Staff status to approved users.')
