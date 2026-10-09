from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from .models import Vehicle,Photo,Enquiry
admin.site.site_header='CarHaven · Inventory studio'
admin.site.site_title='CarHaven staff'
admin.site.index_title='Manage the collection'
class PhotoFormSet(BaseInlineFormSet):
 def clean(self):
  super().clean()
  if any(self.errors):return
  if self.instance.state in ('available','reserved','sold') and not self.instance.is_demo:
   remaining=[f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE') and f.cleaned_data.get('image')]
   if not remaining:raise ValidationError('A published vehicle must retain at least one approved photo.')
class PhotoInline(admin.TabularInline):
 model=Photo
 formset=PhotoFormSet
 extra=0
 def has_delete_permission(self,request,obj=None):return obj is None or obj.state=='draft'
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
 list_display=('stock_number','year','make','model','price','state','is_demo','updated_at')
 list_filter=('state','make','body','featured','is_demo')
 search_fields=('stock_number','make','model')
 inlines=[PhotoInline]
 readonly_fields=('id','created_at','updated_at')
 actions=['archive_selected']
 @admin.action(description='Archive selected vehicles (remove from public site)')
 def archive_selected(self,request,queryset):
  for vehicle in queryset:
   vehicle.state='archived';vehicle.save(update_fields=['state','updated_at']);self.log_change(request,vehicle,'Archived from public inventory')
 def has_delete_permission(self,request,obj=None):return False
@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
 list_display=('name','vehicle','state','created_at')
 list_filter=('state','created_at')
 search_fields=('name','email','phone')
 readonly_fields=('id','vehicle','name','email','phone','message','consent','created_at')
 def has_add_permission(self,request):return False
