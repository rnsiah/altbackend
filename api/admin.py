
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Donation, Donor, User, UserProfile, Balance, CompanyMatchDonation
from api.models import AltruePoints, Link, UserDonation


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password','username')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name','profile_created')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'profile_created')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    inlines = (UserProfileInline, )


class DonorAdmin(admin.ModelAdmin):
    model = Donor
    fields = ('email', 'last_name', 'amount_donated', 'sent_to', 'first_name','donation_category')
    list_display = ('email', 'last_name', 'amount_donated', 'sent_to', 'first_name')


class BalanceAdmin(admin.ModelAdmin):
    model = Balance
    fields = ('account', 'balance')
    list_display =('account', 'balance', 'last_transaction')

class DonationAdmin(admin.ModelAdmin):
    model = Donation
    fields= ('donor',)
    
    list_display = ('donor','donation_date','donation_amount', 'receiver')


class AltruePointsAdmin(admin.ModelAdmin):
    model = AltruePoints
    fields=('account', 'balance',)

    list_display = ('account', 'balance', 'last_transaction')



admin.site.register(Donor, DonorAdmin)
admin.site.register(Balance, BalanceAdmin)
admin.site.register(Donation, DonationAdmin)
admin.site.register(AltruePoints, AltruePointsAdmin)


class UserDonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'nonprofit', 'atrocity')
    
admin.site.register(UserDonation, UserDonationAdmin)

class CompanyMatchAdmin(admin.ModelAdmin):
    list_display = ('company','donation_date','nonprofit', 'atrocity')
    model= CompanyMatchDonation
admin.site.register(CompanyMatchDonation, CompanyMatchAdmin)




class LinkAdmin(admin.ModelAdmin):
    list_display = [ 'publication', 'atrocity', 'nonprofit','company']
    model = Link

    
admin.site.register(Link, LinkAdmin)

