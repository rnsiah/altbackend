from django.contrib import admin
from .models import CompanyBalance, CompanyDonation, NonProfitAtrocityRelationShip, NonProfitProject, CompanyAtrocityRelationship, CompanyNonProfitRelationship ,AtrocityShirt, Shirt, Atrocity, Category, NonProfit, Country, Rating, Order, OrderItem, CheckoutAddress, CompanyCoupon, CompanyStore, ForProfitCompany, AltrueAction, AltrueLevel, UserAltrueAction, FriendInvite, AltrueActionCode, ProfileImage
from Alt.models import AtrocityBalance, NonProfitBalance




class ShirtAdmin(admin.ModelAdmin):
    list_display =('name',)
    prepopulated_fields = {'slug': ('name',)} 

admin.site.register(Shirt, ShirtAdmin)


class NonProfitAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)} 

admin.site.register(NonProfit, NonProfitAdmin)

# Register your models here.

admin.site.register(Atrocity)
admin.site.register(Category)
admin.site.register(AtrocityShirt)

admin.site.register(Country)
admin.site.register(Rating)
    
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CheckoutAddress)
admin.site.register(AltrueActionCode)

class NonProfitBalanceAdmin(admin.ModelAdmin):
    list_display = ('nonprofit', 'balance',)

admin.site.register(NonProfitBalance, NonProfitBalanceAdmin)

class AtrocityBalanceAdmin(admin.ModelAdmin):
    list_display = ('atrocity', 'balance', )
admin.site.register(AtrocityBalance, AtrocityBalanceAdmin)


admin.site.register(FriendInvite)



class CompanyAdmin(admin.ModelAdmin):
    list_display=('name',)
admin.site.register(ForProfitCompany, CompanyAdmin)

admin.site.register(CompanyCoupon)

admin.site.register(CompanyStore)

class CompanyDonationAdmin(admin.ModelAdmin):
    list_display = ('company', 'amount', 'nonprofit', 'atrocity')
    
admin.site.register(CompanyDonation, CompanyDonationAdmin)

class CompanyBalanceAdmin(admin.ModelAdmin):
    list_display = ('company', 'balance')
    
admin.site.register(CompanyBalance, CompanyBalanceAdmin)

class NonProfitProjectAdmin(admin.ModelAdmin):
    list_display =('nonprofit', 'title')
    
admin.site.register(NonProfitProject, NonProfitProjectAdmin)
admin.site.register(NonProfitAtrocityRelationShip)

class CompanyAtroRelationshipAdmin(admin.ModelAdmin):
    list_display = ('company', 'atrocity', 'total_raised')
admin.site.register(CompanyAtrocityRelationship, CompanyAtroRelationshipAdmin)

class CompanyNPRelationshipAdmin(admin.ModelAdmin):
    list_display = ('company', 'nonprofit', 'total_raised')
admin.site.register(CompanyNonProfitRelationship, CompanyNPRelationshipAdmin)


class AltrueLevelAdmin(admin.ModelAdmin):
    list_display = ('level_number', 'name')
admin.site.register(AltrueLevel, AltrueLevelAdmin)

admin.site.register(UserAltrueAction)
admin.site.register(AltrueAction)
admin.site.register(ProfileImage)



