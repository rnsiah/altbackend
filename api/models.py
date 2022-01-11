from django.db import models
from django.db.models.fields.related import ForeignKey
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import segno
import qrcode
from PIL import Image, ImageDraw
from django.core.files import File
import os   
from django.core.files.storage import FileSystemStorage
from io import BytesIO
from io import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import Alt
from Alt.models import AltrueAction, AltrueActionCode, AltrueLevel, Atrocity, AtrocityBalance, CompanyAtrocityRelationship, CompanyBalance, CompanyDonation, CompanyNonProfitRelationship, ForProfitCompany, FriendInvite, NonProfit, NonProfitBalance, UserAltrueAction, ProfileImage
from django.core.exceptions import ObjectDoesNotExist
import decimal
from django.utils import timezone







class User(AbstractUser):
    username = models.CharField(max_length=100, blank = True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    profile_created = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def __str__(self):
        return str(self.email)





def upload_path_handler():
    return None




class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', primary_key=True)
    username = models.CharField(max_length=100,unique= True, null=True, blank = True)
    title = models.CharField(max_length=5, null= True, blank=True)
    dob = models.CharField(null=True, blank=True, max_length= 12)
    address = models.CharField(max_length=255, null=True, blank= True)
    country = models.CharField(max_length=50, null= True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    zip = models.CharField(max_length=5, null=True, blank =True)
    shirt_list = models.ManyToManyField("Alt.Shirt",  verbose_name=("shirts"), blank=True, related_name='UserProfiles')
    atrocity_list = models.ManyToManyField('Alt.Atrocity', blank=True, related_name='UserProfiles')
    nonProfit_list = models.ManyToManyField('Alt.NonProfit',  blank=True, related_name='UserProfiles')
    slug = models.SlugField(blank = True, null = True)
    qr_code_img = models.ImageField(upload_to= 'qr_codes', blank=True, null=True)
    following = models.ManyToManyField(User, blank=True, related_name= 'userprofile')
    comapnies = models.ManyToManyField('Alt.ForProfitCompany', related_name='userprofile', blank=True)
    company_rewards = models.ManyToManyField('Alt.CompanyCoupon', related_name='userprofile', blank=True)
    has_nonprofit = models.BooleanField(default=False)
    has_company = models.BooleanField(default=False)
    is_companyContributor = models.BooleanField(default=False)
    is_nonprofitContributor= models.BooleanField(default= False)
    altrue_level= models.ForeignKey("Alt.AltrueLevel",  on_delete=models.CASCADE,null= True, blank = True)
    requirementsForNextLevel = models.ManyToManyField('Alt.AltrueAction', related_name='userprofile', blank=True)
    

 

    @property
    def available(self):
        return self.balance.balance

    @property
    def user_orders(self):
        return self.order.all()
    
    @property
    def userdonations(self):
        return self.user_donation.all()

    @property
    def amount_following(self):
        people_following = self.following.all()
        return len(people_following)
    
    @property
    def amount_followers(self):
        user = User.objects.all()
        lis=[]
        for use in user:
            users = UserProfile.objects.get(user = use )
            thelist = users.following.all()
            if self in thelist:
                lis.append(users)
        return len(lis)
        

        
    

    def get_absolute_url(self):
        return reverse("api:user", kwargs={"slug": self.slug})
    

    def __str__(self):
        return str(self.user.email)


    def get_userName(self):
        return str(self.username)

    def get_webUrl(self):
        user_site = f' www.altrueglobal/user/{self.get_userName()}' 
        return str(user_site)

    def check_if_userNamechanged(self):
        if self.pk is None:
            return False
        # else:
        #     original = UserProfile.objects.get(pk =self.pk)
        #     if original.username != self.username:
        #         return True
        #     return False


    # def saveProfilePicture(self):
       

    #     with open (settings.MEDIA_ROOT +'/'+file_name, "rb") as reopen:
    #         django_file= File(reopen)
    #         self.profile_picture.save(file_name, django_file, save=False)

    def save(self, *args, **kwargs):
        
        self.slug = self.username
        self.generate_qr()
        super(UserProfile, self).save()
        # elif self.pk:
        #     original = UserProfile.objects.get(pk=self.pk)
        #     if original.username != self.username:
        #         self.slug = self.username
        #         self.generate_qr()
        #         super(UserProfile,self).save()
        #     # if self.profile_picture is not None:
        #     #     self.saveProfilePicture()
        #     #     super(UserProfile, self).save()
        # super(UserProfile, self).save()
        
    ## Things to do 
        # Write logic to check save profile picture to its own folder based on username
        

           
   
     

        
    def generate_qr(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=0,
        )
        qr.add_data(f'www.altrueglobal.org/true/{self.get_userName()}')
        qr.make(fit =True)
        filename = 'qr-%s.png' % (self.get_userName())
        img= qr.make_image()
        img.save(settings.MEDIA_ROOT + filename)
        with open (settings.MEDIA_ROOT +filename, "rb") as reopen:
            django_file= File(reopen)
            self.qr_code_img.save(filename, django_file, save=False)

    

class Balance(models.Model):
    account = models.OneToOneField('api.UserProfile', on_delete=models.CASCADE, primary_key=True, related_name='balance')
    balance = models.DecimalField(decimal_places = 2, max_digits=4 ,default = 0)
    last_transaction = models.DateTimeField(default=timezone.now) 


    class Meta:
        verbose_name = _("Balance")
        verbose_name_plural = _("Balances")

    # def add_to_balance(self, balance=0):
    #     self.balance += balanc
    #     self.save()


    def __str__(self):
        return self.account.user.email

    def get_absolute_url(self):
        return reverse("Balance_detail", kwargs={"pk": self.pk})


class AltruePoints(models.Model):
    account = models.OneToOneField('api.UserProfile', on_delete=models.CASCADE, primary_key=True, related_name='altrue_points')
    balance = models.IntegerField(default = 0)
    last_transaction = models.DateTimeField( default=timezone.now)

    def __str__(self):
        return self.account.user.email
    def get_absolute_url(self):
        return reverse("altrue_points_detail", kwargs={"pk": self.pk})
    
    def save(self, *args, **kwargs):
       self.last_transaction = timezone.now()
       super(AltruePoints, self).save(*args, **kwargs) # Call the real save() method
    

class Donor(models.Model):
    email = models.EmailField(max_length=254)
    first_name = models.CharField( max_length=50)
    last_name = models.CharField(max_length = 50)
    amount_donated = models.DecimalField(decimal_places=2, max_digits=5)
    donation_category = models.ForeignKey( "Alt.Category", on_delete=models.CASCADE,  blank=True, null=True,  related_name='category')
    sent_to = models.ForeignKey('api.UserProfile', on_delete=models.CASCADE, related_name='donor')
    donation_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email
 
    

    
class Donation(models.Model):
    stripe_charge_id = models.CharField(max_length=100)
    donor = models.ForeignKey('api.Donor', on_delete=models.CASCADE, related_name='donation')
    donation_amount = models.DecimalField(decimal_places=2, max_digits=5)
    receiver = models.ForeignKey('api.Balance', on_delete=models.CASCADE, related_name= 'donation')
    donation_date = models.DateTimeField(default=timezone.now)

    


    @property
    def getAmount(self):
        return self.donor.amount
    @property    
    def get_reciever(self):
        return self.donor.sent_to.user.email
    @property
    def donation_cause(self):
        return self.donor.donation_category


class UserDonation(models.Model):

    DONATION_TYPE=(
        ('S', 'Single'),
        ('MU', 'Multiple Orgnanizations'))
    user = models.ForeignKey('api.UserProfile', on_delete=models.CASCADE, related_name='user_donation')
    wallet = models.ForeignKey('api.Balance', on_delete=models.CASCADE, related_name = 'user_donationc')
    amount = models.DecimalField( max_digits=3, decimal_places=2)
    nonprofit = models.ForeignKey('Alt.NonProfit', related_name='user_donation', blank= True, null = True, on_delete=models.CASCADE)
    atrocity = models.ForeignKey('Alt.Atrocity', blank=True, null=True, on_delete=models.CASCADE, related_name='user_donation')
    donation_type = models.CharField(max_length = 2, choices=DONATION_TYPE)
    is_matched =models.BooleanField(default = False)
    donation_date = models.DateTimeField(default=timezone.now)
    
    

    def __str__(self):
        return self.user.user.email




class CompanyMatchDonation(models.Model):

    company = models.ForeignKey("Alt.ForProfitCompany", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=3, decimal_places=2)
    nonprofit = models.ForeignKey('Alt.NonProfit', related_name='company_donation', blank=True, null=True, on_delete=models.CASCADE)
    atrocity = models.ForeignKey("Alt.Atrocity", on_delete=models.CASCADE, blank= True, null=True)
    user_matched = models.ForeignKey('api.UserDonation', on_delete=models.CASCADE, blank=True, null=True)
    donation_date= models.DateTimeField(default=timezone.now)


    def __str__(self):
        return str(self.amount)
    
# class CompanyNewsUpdate(models.Model):
#     company = models.ForeignKey("Alt.ForProfitCompany", on_delete=models.CASCADE, related_name='companyupdate')
#     atrocity = models.ForeignKey

class Link(models.Model):
    link = models.CharField(max_length = 200, blank = False, null = False)
    atrocity = models.ForeignKey('Alt.Atrocity', related_name= 'link', blank = True, null= True, on_delete= models.CASCADE)
    nonprofit = models.ForeignKey('Alt.NonProfit', related_name='link', blank = True, null = True, on_delete= models.CASCADE)
    company = models.ForeignKey('Alt.ForProfitCompany', related_name='link', blank = True, null = True, on_delete=models.CASCADE)
    author = models.CharField(max_length = 30, blank = False, null=False)
    title = models.CharField(max_length=100, blank=False, null=False)
    publication = models.CharField(max_length = 30, blank = False, null =False)


    def __str__(self):
        if(self.atrocity and self.publication):
            return f'{self.publication} article on {self.atrocity}'
        elif(self.nonprofit and self.publication):
            return f'{self.publication} article on {self.nonprofit}'
        elif(self.company and self.publication):
            return f'{self.publication} article on {self.company}'
        
        return self.link
    



@receiver(post_save, sender= UserDonation)
def matchUserCompanyDonation(sender, instance, created=False, **kwargs):
    if created and instance.is_matched is True:
        if instance.nonprofit:
            nonProfitDonatedTo = NonProfit.objects.get(id= instance.nonprofit.id)
            companies = ForProfitCompany.objects.filter(nonprofits = nonProfitDonatedTo)
            for company in companies:
                try:
                    
                    match = CompanyNonProfitRelationship.objects.get(nonprofit = nonProfitDonatedTo, company =company)
                    decimaled_match = float(match.match_level)
                    match = decimaled_match /100
                    matched_amount  = float(instance.amount) * match
                    final = float(matched_amount)
                    np_balance = NonProfitBalance.objects.get(nonprofit= nonProfitDonatedTo)
                    
                    CompanyMatchDonation.objects.create(nonprofit = nonProfitDonatedTo, company= company, user_matched = instance, amount = str(final) )
                    new_np_balance = float(np_balance.balance)+ final
                    np_balance.balance =float(new_np_balance)
                    np_balance.save()                    
                    # instance.save(is_matched =True)
                except ObjectDoesNotExist:
                  pass
        elif instance.atrocity:
            atrocityDonatedTo = Atrocity.objects.get(id=instance.atrocity.id)
            comp= ForProfitCompany.objects.filter(atrocities = atrocityDonatedTo)
            for co in comp:
                try:
                    mat = CompanyAtrocityRelationship.objects.get(atrocity = atrocityDonatedTo, company= co)
                    dec_match = float(mat.match_level)
                    ma = dec_match/100
                    total_don_amount = float(instance.amount) * ma
                    fina = float(total_don_amount)
                    atroc_balance = AtrocityBalance.objects.get(atrocity = atrocityDonatedTo)
                    CompanyMatchDonation.objects.create(atrocity = atrocityDonatedTo, company = co, user_matched = instance, amount =str(total_don_amount))
                   
                    new_atro_balance = float(atroc_balance.balance) + fina
                    atroc_balance.balance = float(new_atro_balance)
                    atroc_balance.save()

                except ObjectDoesNotExist:
                    pass

                
                
                
                
                    

## 1.Have Company, Get companies matching agreement, create a companyDonation


#Creates a wallet for donations when profile is created
@receiver(post_save, sender = UserProfile)
def createAccount(sender, instance=None, created=False, **kwargs):
    if created:
        Balance.objects.create(account = instance)
        AltruePoints.objects.create(account = instance)
       
                    
        

@receiver(post_save, sender= UserDonation)
def updateBalance(sender, instance, created, **kwargs):
    userBalance = Balance.objects.get(pk = instance.user.pk)
    try:
        if userBalance.balance >= instance.amount:
            updatedBalance = userBalance.balance - instance.amount
            userBalance.balance = updatedBalance
            userBalance.save()
        else:
            pass
    except:
        raise Exception(' Something Went Wrong')


@receiver(post_save, sender='Alt.NonProfit')
def updateProfileHasNonProfit(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.get(pk = instance.owner.pk)
        profile.has_nonprofit = True


# Creates a donation object when someone(external) donates to a profile
@receiver(post_save, sender = Donor)
def create_donation(sender, instance =None, created = False, **kwargs):
    
    Donation.objects.create(donor = instance, donation_amount= instance.amount_donated, receiver = instance.sent_to.balance, donation_date= instance.donation_date)




@receiver(post_save, sender = UserProfile)
def profile_updated(sender, instance, created,  **kwargs):
        if not created:
            user = User.objects.get(pk = instance.pk)
            
            
            if user.profile_created == False:
                user.profile_created = True
                
                
                
               
        else: None
    




## Updates The  User's Altrue Points When User Completes A Task      
@receiver(pre_save, sender= 'Alt.UserAltrueAction') 
def awardAltruePoints(instance, created=True, **kwargs):
    if not created:
        user = instance.profile_acting
        #get point_wallet
        point_wallet = AltruePoints.objects.get(account = user )

        #get_specific_action to be rewarded
        the_action = AltrueAction.objects.get(pk= instance.altrue_action)
        
        requirementsNeededForNextLevel = user.requirementsForNextLevel.all()
        #remove action from list
        if the_action in requirementsNeededForNextLevel:
            user.requirementsForNextLevel.remove(the_action)
                        

        #check how many times user has compleated specific action to see if they arent over the maximum to receive points
        noOfActionsAlreadyDone = UserAltrueAction.objects.filter(profile_acting = user, altrue_action =the_action).count()

        # award if they havent reached the max number of actions
        if noOfActionsAlreadyDone <= instance.altrue_action.number_of_occurrences:
            #check if the action was promoted and give promotion if so
            if instance.altrue_action.is_promoted is True:
                amount_awarded = the_action.points_awarded * the_action.promotion.multiplier
                point_wallet.balance += amount_awarded
                point_wallet.save()
            else:
                amount_awarded = the_action.points_awarded
                point_wallet.balance += amount_awarded
                point_wallet.save()

        # check altrueLevel and point total to see if user 
        # satisfied all requirements needed to move to the next level
        user_level = user.altrue_level.level_number
        Alevel = AltrueLevel.objects.get(level_number = user_level)
        altue_level_number = Alevel.level_number
        next_level = AltrueLevel.objects.get(level_number= altue_level_number+1)
        
        count = user.requirementsForNextLevel.all().count()

        #if satisfied, changing them to the next level
        if user.altrue_points.balance > next_level.minimum_points and count == 0:
            user.altrue_level= next_level
            next_level_requirements = next_level.requiredActions.all()
            # update the requirements to move to the next level
            for requirement in next_level_requirements:
                user.requirementsForNextLevel.add(requirement)   
            user.save(update_fields= ['altrue_level', 'requirementsForNextLevel'])

        
        





## Updates the User's wallet balance when user receives a donation
@receiver([post_save, post_delete], sender= Donation)
def updateUserAccountBalance(instance, **kwargs):
    donation_amount = instance.donation_amount
    balance = Balance.objects.get(pk = instance.receiver_id)
    love = balance.balance
    new_amount = love + donation_amount
    balance.balance = new_amount
    balance.save(update_fields=['balance'])
    



# Creates UserProfile when new user is registered onto platform
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_userProfile(sender, instance, created=False, **kwargs):
    if created:
        nonLevl = AltrueLevel.objects.get(level_number = 0)
        user = UserProfile.objects.get_or_create(user = instance, altrue_level=nonLevl)
        
        
@receiver(post_save, sender= UserProfile)
def create_add_requirements(sender, instance, created, **kwargs):
    if created:
        levlone =AltrueLevel.objects.get(level_number= 1)
        requirements = levlone.requiredActions.all()
        for requirement in requirements:
            action =AltrueAction.objects.get(id =requirement.id)
            instance.requirementsForNextLevel.add(action)
     


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    

    

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance) 



# @receiver(post_save, sender = UserProfile)
# def profile_creation_award(sender, instance, created=False, **kwargs):
#     if  created:
#         code = AltrueActionCode.objects.get(code ='createProfile')
#         action = AltrueAction.objects.get(action_code = code)
#         done_actions = UserAltrueAction.objects.filter(profile_acting = instance, altrue_action = action)
#         profile = UserProfile.objects.get(pk = instance.pk)
#         try:
#             if done_actions.count() == 0:
#                 profile_pic = ProfileImage.objects.get(profile_id = profile.pk)
#         except ProfileImage.DoesNotExist:
#             return None
#             if profile_pic:
#                 UserAltrueAction.objects.create(profile_acting = instance, altrue_action = action)


        




# @receiver(post_save, sender = UserProfile)
# def follow_first_np_award(sender, instance, created, **kwargs):
#     ncode = AltrueActionCode.objects.get(code='followFirstNonProfit')
#     naction = AltrueAction.objects.get(action_code = ncode)
#     ndone_actions = UserAltrueAction.objects.filter(profile_acting = instance)
#     if naction not in ndone_actions:
#             user =UserAltrueAction.objects.create(profile_acting = instance)


# @receiver(post_save, sender = UserProfile)
# def follow_first_company_award(sender, instance, created, **kwargs):
#     if created:
#         if instance.comapnies.all().count() > 0 and  instance.requirementsForNextLevel is not None:
#             code = AltrueActionCode.objects.get(code='followFirstCompany')
#             action = AltrueAction.objects.get(action_code = code)
#             done_actions = UserAltrueAction.objects.filter(profile_acting = instance)
#             if action not in done_actions:
#                 user =UserAltrueAction.objects.create(profile_acting = instance, altrue_action = action)
        
# @receiver(post_save, sender = UserProfile)
# def follow_first_atrocity_award(sender, instance, created, **kwargs):
#     if created:
#         if  instance.atrocity_list.all().count() > 0 and instance.requirementsForNextLevel is not None:
#             code = AltrueActionCode.objects.get(code='followFirstAtrocity')
#             action = AltrueAction.objects.get(action_code = code)
#             done_actions = UserAltrueAction.objects.filter(profile_acting = instance)
#             if action not in done_actions:
#                 user =UserAltrueAction.objects.create(profile_acting = instance)






# #Creates Altrue Points when user registers profile and Makes Them Have Altrue Level None with requirements
# @receiver(post_save, sender=UserProfile)
# def create_AltruePoints(sender, instance, created=False, **kwargs):
#     if created:
#         AltruePoints.objects.get_or_create(account= instance)
#         levelo = AltrueLevel.objects.get(level_number =0)
#         instance.altrue_level = levelo
#         # get next level requirements

#         levlone =AltrueLevel.objects.get(level_number= 1)
#         requirements = levlone.requiredActions.all()
#         reqs_needed = []
#         for requirement in requirements:
#             action =AltrueAction.objects.get(id =requirement.id)
#             reqs_needed.append(action)
#         for reqs in reqs_needed:
#             instance.requirementsForNextLevel.add(reqs)
#         instance.save(update_fields= ['altrue_level', 'requirementsForNextLevel'])

        


# @receiver(pre_save, sender= UserProfile)
# def qr_codeNprofilePic(sender, instance, **kwargs):
#     try:
#         obj = sender.objects.get(pk=instance.pk)
#     except sender.DoesNotExist:
#         pass
#     else:
#         if not obj.username == instance.username:
#             newqr = sender.generate_qr()
   