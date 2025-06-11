from django.contrib import admin
from django import forms
from .models import Category, Destination, DestinationImage

class DestinationImageInline(admin.TabularInline):
    model = DestinationImage
    extra = 0  # Show 3 empty forms by default
    max_num = 10  # Maximum number of images allowed

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class DestinationAdminForm(forms.ModelForm):
    images = MultipleFileField(
        required=False,
        help_text='You can select multiple images at once'
    )

    class Meta:
        model = Destination
        fields = '__all__'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'custom_name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('custom_name',)}
    search_fields = ('name', 'custom_name', 'description')
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'custom_name', 'description'),
            'description': "Select a predefined category or choose 'Other' to create a custom one"
        }),
        ('Advanced', {
            'fields': ('slug',),
            'classes': ('collapse',)
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'custom_name' in form.base_fields:
            form.base_fields['custom_name'].required = False
        return form

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    form = DestinationAdminForm
    list_display = ('name', 'category', 'address', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description', 'address')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [DestinationImageInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if 'images' in request.FILES:
            for image in request.FILES.getlist('images'):
                DestinationImage.objects.create(
                    destination=obj,
                    image=image,
                    is_primary=not DestinationImage.objects.filter(destination=obj).exists()  # First image is primary
                )

@admin.register(DestinationImage)
class DestinationImageAdmin(admin.ModelAdmin):
    list_display = ('destination', 'caption', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('destination__name', 'caption')
