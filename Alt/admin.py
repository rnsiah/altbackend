from django.contrib import admin
from .models import  AltruePointPromotion, CompanyBalance, CompanyDonation, CompanyProjectRelationShip, NonProfitAtrocityRelationShip, NonProfitProject, CompanyAtrocityRelationship, CompanyNonProfitRelationship ,AtrocityShirt, Shirt, Atrocity, Category, NonProfit, Country, Rating, Order, OrderItem, CheckoutAddress, CompanyCoupon, CompanyStore, ForProfitCompany, AltrueAction, AltrueLevel, ShirtColor, ShirtSize, ShirtVariations, UserAltrueAction, FriendInvite, AltrueActionCode, ProfileImage, UserMatchRelationShip
from Alt.models import AtrocityBalance, NonProfitBalance




class ShirtAdmin(admin.ModelAdmin):
    list_display =('name',)
    prepopulated_fields = {'slug': ('name',)} 

admin.site.register(Shirt, ShirtAdmin)



admin.site.register(ShirtVariations)

class NonProfitAdmin(admin.ModelAdmin):
    list_display = ('id','name',)
    prepopulated_fields = {'slug': ('name',)} 

admin.site.register(NonProfit, NonProfitAdmin)

# Register your models here.


admin.site.register(ShirtColor)

class ShirtDisplayAdmin(admin.ModelAdmin):
    list_display = ['get_size_display']
    
    
admin.site.register(ShirtSize, ShirtDisplayAdmin)
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
    list_display = ('id','nonprofit', 'balance',)

admin.site.register(NonProfitBalance, NonProfitBalanceAdmin)

class AtrocityBalanceAdmin(admin.ModelAdmin):
    list_display = ('atrocity', 'balance','last_transaction' )
admin.site.register(AtrocityBalance, AtrocityBalanceAdmin)


admin.site.register(FriendInvite)


admin.site.register(CompanyProjectRelationShip)

# class CompanyAdmin(admin.ModelAdmin):
#     list_display=('name',)
# admin.site.register(ForProfitCompany, CompanyAdmin)


admin.site.register(ForProfitCompany)

admin.site.register(CompanyCoupon)

admin.site.register(CompanyStore)

class CompanyDonationAdmin(admin.ModelAdmin):
    list_display = ('company', 'amount', 'nonprofit', 'atrocity')
    
admin.site.register(CompanyDonation, CompanyDonationAdmin)

class CompanyBalanceAdmin(admin.ModelAdmin):
    list_display = ('id','company', 'balance')
    
admin.site.register(CompanyBalance, CompanyBalanceAdmin)

class NonProfitProjectAdmin(admin.ModelAdmin):
    list_display =('id','nonprofit', 'title')
    
admin.site.register(NonProfitProject, NonProfitProjectAdmin)
admin.site.register(NonProfitAtrocityRelationShip)

class CompanyAtroRelationshipAdmin(admin.ModelAdmin):
    list_display = ('company', 'atrocity', 'total_raised')
admin.site.register(CompanyAtrocityRelationship, CompanyAtroRelationshipAdmin)

class CompanyNPRelationshipAdmin(admin.ModelAdmin):
    list_display = ('company', 'nonprofit', 'total_raised')
admin.site.register(CompanyNonProfitRelationship, CompanyNPRelationshipAdmin)

class UserMatchRelationShipAdmin(admin.ModelAdmin):
    list_display = ('user_matching_donation','user_being_matched')
admin.site.register(UserMatchRelationShip, UserMatchRelationShipAdmin)


class AltrueLevelAdmin(admin.ModelAdmin):
    list_display = ('level_number', 'name','minimum_points', 'maximum_points')
admin.site.register(AltrueLevel, AltrueLevelAdmin)

class UserActionAdmin(admin.ModelAdmin):
    model = UserAltrueAction
    list_display = ('profile_acting','altrue_action','points','date_completed', )
    
    def points(self, obj):
        action = obj.altrue_action

        try:
            love = AltrueAction.objects.get(pk = action.pk)
            if love.is_promoted ==True:
                total = love.points_awarded * love.promotion.multiplier
                return total
            return love.points_awarded
        except love.DoesNotExist:
            return 0
        


admin.site.register(UserAltrueAction, UserActionAdmin)



class AltruePointPromotionAdmin(admin.ModelAdmin):
    model = AltruePointPromotion
    
    list_display = ('name','is_active','start_date','end_date','actions_promoted')

    def actions_promoted(self, obj):
        li = []
        love = list(AltrueAction.objects.filter(promotion =obj))
        for lo in love:
            li.append({lo.id:lo.requirement})
        return li

admin.site.register(AltruePointPromotion, AltruePointPromotionAdmin)



class AltrueActionAdmin(admin.ModelAdmin):
    model = AltrueAction
    list_display = ('id','requirement', 'needed_to_pass', 'points_awarded','code')
    
    def needed_to_pass(self, obj):
        level1 = AltrueLevel.objects.get(level_number =1)
        level2 = AltrueLevel.objects.get(level_number =2)
        if obj in level1.requiredActions.all():
            return "Level 0"
        elif obj in level2.requiredActions.all():
            return "Level 1"
        return 'No Level'
        
    def code(self, obj):
        return obj.action_code


admin.site.register(AltrueAction, AltrueActionAdmin)



class ProfileImageAdmin(admin.ModelAdmin):
    model =ProfileImage
    list_display =('profile_id', 'profile') 
    ordered=('profile_id',)
admin.site.register(ProfileImage, ProfileImageAdmin)



