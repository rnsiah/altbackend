import profile
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
from Alt.models import AltrueAction, AltrueActionCode, AltrueLevel, Atrocity, CompanyAtrocityRelationship, CompanyDonation, CompanyNonProfitRelationship, CompanyProjectRelationShip, ForProfitCompany, NonProfit, NonProfitProject, UserAltrueAction, ProfileImage, UserMatchRelationShip, UserMatchTransaction
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
    
    @property
    def altrue_level(self):
        profile = UserProfile.objects.get(user= self)
        if not profile.altrue_level:
            return 'Null'
        return profile.altrue_level





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
    profiles_following = models.ManyToManyField('api.UserProfile' )

 

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
    def follower_list(self):
        follow_list= []
        users = self.following.all()
        pic = ProfileImage.objects.get(profile = self)
        for user in users:
            representation = {'username': str(user.username),
            'id': (user.user.id),
            'profile_pic': pic.image }
            follow_list.append(representation)
        return follow_list
            

    def setfirstLevel(self):
        levelo = AltrueLevel.objects.get(level_number =0)
        self.altrue_level = levelo
        
    
    
    def noneLevelCheck(self):
        
        levelno = self.altrue_level.level_number
        if levelno == 0:
            level = AltrueLevel.objects.get(level_number =levelno+1)

            all =[]
            requirements = level.requiredActions.all()
            for requirement in requirements:
                all.append(requirement)
            for any in all:
                self.requirementsForNextLevel.add(any)
        
            
        else:
            pass
        

    def checkaggregates(self):
        codes = []
        codes.append(self.atrocityawardcheck())
        codes.append(self.nonprofitawardcheck())
        codes.append(self.companyawardcheck())
        return codes

    def aggcheck(self):
        lit = []
        actions = [13, 8, 9]
        for action in actions:
            the_action = AltrueAction.objects.get(pk=action)
            ## see if user has completed these actions
            completed = UserAltrueAction.objects.filter(profile_acting = self, altrue_action=the_action)
            if completed:
                #remove from the list
                lit.append(the_action)
            return lit
        return lit
              
        
    
    def picupdatecheck(self):
        if 'default.png' not in str(self.profile_pic.image):
            return True
        else:
            return False
    
    def atrocityawardcheck(self):
        if len(self.atrocity_list.all()) >= 3:
            love =AltrueAction.objects.get(pk =13)
            return love.action_code.code
        else:
            return None

    def nonprofitawardcheck(self):
        if len(self.nonProfit_list.all()) >= 3:
            love =AltrueAction.objects.get(pk =8)
            return love.action_code.code
        else:
            return None

    def companyawardcheck(self):
        if len(self.comapnies.all()) >= 3:
            love =AltrueAction.objects.get(pk =9)
            return love.action_code.code
        else: 
            return None

    def needsTolevelUp(self):
        current_level = self.altrue_level
        print(current_level)
    
        needsToBeCompleted = AltrueLevel.objects.get(level_number =current_level.level_number+1)
        print(needsToBeCompleted)
        done_actions = list(UserAltrueAction.objects.filter(profile_acting = self))
        lo = list(needsToBeCompleted.requiredActions.all())
        po =[]
        for action in done_actions:
            po.append(action.altrue_action)
        print(po)
        print(lo)
        result = set(lo).intersection(po)

        print(len(result))
        print(int(self.altrue_points.balance))
        print(int(needsToBeCompleted.minimum_points))
        
        if int(self.altrue_points.balance) > int(needsToBeCompleted.minimum_points) and len(result) == len(lo) :
           return {'number': needsToBeCompleted.level_number}
        else:
            return False


    def updateLevel(self,level):
        
        new_level =AltrueLevel.objects.get(level_number= level)
        requirements = new_level.requiredActions.all()
        reqs_needed = []
        for requirement in requirements:
            action =AltrueAction.objects.get(id =requirement.id)
            reqs_needed.append(action)
        for reqs in reqs_needed:
            self.requirementsForNextLevel.add(reqs)
        if len(self.requirementsForNextLevel.all()):
            self.altrue_level = new_level
            self.save(update_fields=['altrue_level'])
            return True
        else:
            return False



    def startAltrueLevel(self):
        if self.altrue_level is None:
            self.setfirstLevel()
            
            levlone =AltrueLevel.objects.get(level_number= 1)
            requirements = levlone.requiredActions.all()
            reqs_needed = []
            for requirement in requirements:
                action =AltrueAction.objects.get(id =requirement.id)
                reqs_needed.append(action)
            for reqs in reqs_needed:
                self.requirementsForNextLevel.add(reqs) 
        else:
            pass
                    
                    
        # else:
        #     level = self.altrue_level.level_number
        #     nextLevel = AltrueLevel.objects.get(level_number = level+1)
        #     requirements  = nextLevel.requiredActions.all()
        #     reqs_needed =[]
        #     for requirement in requirements:
        #         action = AltrueAction.objects.get(id = requirement.id)
        #         reqs_needed.append(action)
        #     for reqs in reqs_needed:
        #         self.requirementsForNextLevel.add(reqs)
                
        #     pass
        # pass
        
    
     
            
            
    

    def get_absolute_url(self):
        return reverse("api:user", kwargs={"slug": self.slug})
    

    def __str__(self):
        return str(self.user.email)


    def get_userName(self):
        return str(self.username)

    def get_webUrl(self):
        user_site = ' www.altrueglobal/user/'+self.get_userName() 
        return str(user_site)

    
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
        qr.add_data('www.altrueglobal.org/true/'+self.get_userName())
        qr.make(fit =True)
        filename = 'qr-%s.png' % (self.get_userName())
        img= qr.make_image()
        img.save(settings.MEDIA_ROOT + filename)
        with open (settings.MEDIA_ROOT +filename, "rb") as reopen:
            django_file= File(reopen)
            self.qr_code_img.save(filename, django_file, save=False)

    




class Balance(models.Model):
    account = models.OneToOneField('api.UserProfile', on_delete=models.CASCADE, primary_key=True, related_name='balance')
    balance = models.DecimalField(decimal_places = 2, max_digits=6 ,default = 0)
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
        return str(self.balance)
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
    amount = models.DecimalField( max_digits=5, decimal_places=2)
    nonprofit = models.ForeignKey('Alt.NonProfit', related_name='user_donation', blank= True, null = True, on_delete=models.CASCADE)
    atrocity = models.ForeignKey('Alt.Atrocity', blank=True, null=True, on_delete=models.CASCADE, related_name='user_donation')
    donation_type = models.CharField(max_length = 2, choices=DONATION_TYPE)
    is_matched =models.BooleanField(default = False)
    donation_date = models.DateTimeField(default=timezone.now)
    project= models.ForeignKey('Alt.NonProfitProject', related_name='user_donation', on_delete=models.CASCADE, blank=True, null=True)
    
    

    def __str__(self):
        return self.user.user.email






class CompanyMatchDonation(models.Model):

    company = models.ForeignKey("Alt.ForProfitCompany", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    nonprofit = models.ForeignKey('Alt.NonProfit', related_name='company_match_donation', blank=True, null=True, on_delete=models.CASCADE)
    atrocity = models.ForeignKey("Alt.Atrocity", on_delete=models.CASCADE, blank= True, null=True)
    transaction_matched = models.ForeignKey('api.UserDonation', on_delete=models.CASCADE, related_name='company_match_donation',blank=True, null=True)
    donation_date= models.DateTimeField(default=timezone.now)
    project =  models.ForeignKey('Alt.NonProfitProject', related_name='company_match_donation', on_delete=models.CASCADE, blank= True, null =True)
    
    


    def __str__(self):
        return '{} matched {} for {}'.format(self.company.name, self.transaction_matched.username, self.amount)
    
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
            return '{} article on {}'.format(self.publication, self.atrocity)
        elif(self.nonprofit and self.publication):
            return '{} article on {}'.format(self.publication, self.nonprofit)
        elif(self.company and self.publication):
            return '{} article on {}'.format(self.publication, self.company)
        
        return self.link
 

    

class NonProfitRequest(models.Model):
    nonprofit = models.ForeignKey('Alt.NonProfit', related_name='request', on_delete=models.CASCADE)
    company = models.ForeignKey('Alt.ForProfitCompany', related_name='request', on_delete=models.CASCADE)
    request_message = models.TextField(blank = True, null = True)
    

    def __str__(self):
        return '{} is requesting to be supported by {}'.format(self.nonprofit.name, self.company.name)


class RequestVotes(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True, editable=False)
    user = models.ForeignKey('api.UserProfile', related_name='voter', on_delete=models.CASCADE )
    np_request = models.ForeignKey('api.NonProfitRequest', related_name='voter', on_delete=models.CASCADE)
    message = models.TextField(blank = True,  null = True)
    
    def __str__(self):
        return str(self.id)










# Creates UserProfile when new user is registered onto platform
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_userProfile(sender, instance, created=True, **kwargs):
    if created:
        love = UserProfile.objects.create(user = instance)
        love.save()
        Balance.objects.create(account = love)
        AltruePoints.objects.create(account = love)
        ProfileImage.objects.get_or_create(profile =love)
        love.setfirstLevel()
        levlone =AltrueLevel.objects.get(level_number= 1)
        requirements = levlone.requiredActions.all()
        reqs_needed = []
        for requirement in requirements:
            action =AltrueAction.objects.get(id =requirement.id)
            reqs_needed.append(action)
        for reqs in reqs_needed:
            love.requirementsForNextLevel.add(reqs)
        love.save() 
        
        
        
        



@receiver(post_save, sender=settings.AUTH_USER_MODEL, dispatch_uid= 'update_profile')
def save_user_profile(sender, instance, **kwargs):
    pass    

    

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance) 



#Creates a wallet for donations when profile is created
# @receiver(post_save, sender = UserProfile)
# def createAccount(sender, instance, created=False, **kwargs):
#     if created:
#         Balance.objects.create(account = instance)
#         AltruePoints.objects.create(account = instance)
        
       


@receiver(post_save, sender = UserProfile, dispatch_uid ='save username')
def profile_updated(sender, instance, created=True,  **kwargs):
        if not created:
            user = User.objects.get(pk = instance.pk)
            if instance.username is not None:
                user.username = instance.username
                user.profile_created = True
                user.save()
                pass             
            else: 
                pass
          
        else: pass        
                
                
               

    


@receiver(post_save, sender= UserDonation)
def matchUserDonation(sender, instance, created = True, **kwargs):
    userWhoDonated = instance.user
    if created:
        ##get all users who have matching relationships with the user who donated
        relationships = UserMatchRelationShip.objects.filter(user_being_matched = userWhoDonated)
        # get the amount donated by user
        amount  = float(instance.amount)
        # for each user find the amount that they chose to match based on matching relationship
        for relationship in relationships:
            amount_being_matched = amount * (relationship.match_level/100)
            if amount_being_matched <= relationship.funding_limit:
                UserMatchTransaction.objects.create(relationship = relationship, total_amount = amount_being_matched, confirmed = False)





@receiver(post_save, sender= UserDonation)
def matchUserCompanyDonation(sender, instance, created=True, **kwargs):
    if created and instance.is_matched is True:
        if instance.nonprofit:
            #find nonprofit that was donated to
            nonProfitDonatedTo = NonProfit.objects.get(id= instance.nonprofit.id)
            
            companies =[]
            cos = CompanyNonProfitRelationship.objects.filter(nonprofit = nonProfitDonatedTo)
            for co in cos:
                companies.append(co.company)
                
            for company in companies:
                try:
                    #find amount from relationship to be donated
                    theMatch = CompanyNonProfitRelationship.objects.get(nonprofit = nonProfitDonatedTo, company =company)
                    prior_donations = CompanyMatchDonation.objects.filter(nonprofit=nonProfitDonatedTo, company =company)
                    nonMatchedDonationsToNonProfit = CompanyDonation.objects.filter(company =company, nonprofit = nonProfitDonatedTo)
                    
                    alldonations = []
                    donList = []
                    for donation in prior_donations:
                        alldonations.append(donation.amount)
                    total_donations = sum(alldonations)
                

                    for don in nonMatchedDonationsToNonProfit:
                        donList.append(don.amount)
                
                    totalDons = sum(donList) + total_donations
                    
                    decimaled_match = float(theMatch.match_level)
                    match = decimaled_match /100
                    matched_amount  = float(instance.amount) * match
                    final = float(matched_amount)
                    difference = float(theMatch.funding_limit ) - float(totalDons)
                     
                    
                    if totalDons< theMatch.funding_limit and final < difference:
                        CompanyMatchDonation.objects.create(company = company, nonprofit=nonProfitDonatedTo, transaction_matched = instance, amount = final)
                    elif totalDons<theMatch.funding_limit and final>difference:
                        CompanyMatchDonation.objects.create(company = company, nonprofit = nonProfitDonatedTo, transaction_matched = instance, amount = difference)
                except ObjectDoesNotExist:
                    pass
                    
        elif instance.project:
            theproject = NonProfitProject.objects.get(id = instance.project.id)
            nonprofit = NonProfit.objects.get(id = theproject.nonprofit.id)
            companies = ForProfitCompany.objects.filter(nonprofits = nonprofit)
            # npBalance = NonProfitBalance.objects.get(nonprofit = nonprofit)
            companies =[]
            compan = CompanyProjectRelationShip.objects.filter(project = theproject)
            for co in compan:
                companies.append(co.company)
            for company in companies:
                try:
                    #find amount from relationship to be donated
                    match = CompanyNonProfitRelationship.objects.get(nonprofit = nonprofit, company =company)
                    projectRelationShip = CompanyProjectRelationShip.objects.get(company= company, project = theproject) 
                    #check all donations to this relationship and get sum to make sure  not past the limit
                    prior_donations = CompanyMatchDonation.objects.filter(project = theproject, company =company)
                    nonMatchedDonationsToNonProfit = CompanyDonation.objects.filter(company =company, nonprofit = nonprofit)
                    
                    alldonations = []
                    donList = []
                    for donation in prior_donations:
                        alldonations.append(donation.amount)
                    total_donations = sum(alldonations)
                
                
                    for don in nonMatchedDonationsToNonProfit:
                        donList.append(don.amount)
                
                    totalDons = sum(donList) + total_donations
                    
                    
                    decimaled_match = float(projectRelationShip.match_level)
                    match = decimaled_match /100
                    matched_amount  = float(instance.amount) * match
                    final = float(matched_amount)
                    differenceProject = float(theproject.fundraising_goal - theproject.total_raised)
                    differenceNP = projectRelationShip.funding_limit - totalDons
                    
                    
              
                    #update totalraised for project and make sure we dont overfund
                    #check if under the limit for organization and limit for project:
                    if theproject.is_active == True and final<differenceNP and final< differenceProject :
                        try:
                            CompanyMatchDonation.objects.create(project = theproject, company= company, transaction_matched = instance, amount =final )
                   
                        except ObjectDoesNotExist:
                            pass
                      
                    elif theproject.is_active == True and final<differenceNP and final>differenceProject:
                        try:
                            CompanyMatchDonation.objects.create(project = theproject, company= company, transaction_matched = instance, amount =differenceProject )
                   
                        except ObjectDoesNotExist:
                            pass
                      
                    elif theproject.is_active == True and final>differenceNP and final<differenceProject:
                        try:
                            CompanyMatchDonation.objects.create(project = theproject, company= company, transaction_matched = instance, amount =differenceNP )
                   
                        except ObjectDoesNotExist:
                            pass

                   
                except ObjectDoesNotExist:
                    pass
        elif instance.atrocity:
            companies = []
            atrocityDonatedTo = Atrocity.objects.get(id=instance.atrocity.id)
            comp= CompanyAtrocityRelationship.objects.filter(atrocity = atrocityDonatedTo)
            for co in comp:
                companies.append(co.company)
            for company in companies:
                try:
                    mat = CompanyAtrocityRelationship.objects.get(atrocity = atrocityDonatedTo, company= company)
                    prior_matchedDonations = CompanyMatchDonation.objects.filter(atrocity=atrocityDonatedTo, company =company)
                    nonMatchedDonationsToAtrocity = CompanyDonation.objects.filter(company =company, atrocity = atrocityDonatedTo)
                    
                    alldonations = []
                    donList = []
                    for donation in prior_matchedDonations:
                        alldonations.append(donation.amount)
                    total_donations = sum(alldonations)
                

                    for don in nonMatchedDonationsToAtrocity:
                        donList.append(don.amount)
                
                    totalDons = sum(donList) + total_donations
                    dec_match = float(mat.match_level)
                    ma = dec_match/100
                    total_don_amount = float(instance.amount) * ma
                    fina = float(total_don_amount)
                    difference = float(mat.funding_limit ) - float(totalDons)
                    new_total = float(totalDons) +fina
                    
                    
                    if totalDons< mat.funding_limit and new_total< mat.funding_limit :
                        CompanyMatchDonation.objects.create(atrocity = atrocityDonatedTo, company = company, transaction_matched = instance, amount =fina)
                    elif totalDons <mat.funding_limit and new_total > mat.funding_limit:
                        CompanyMatchDonation.objects.create(atrocity=atrocityDonatedTo, transaction_matched =instance, company = company, amount = difference)
                           
                  

                except ObjectDoesNotExist:
                    pass

                
                
                
                
                    

## 1.Have Company, Get companies matching agreement, create a companyDonation



                    
        

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





## Updates The  User's Altrue Points When User Completes A Task      
@receiver(post_save, sender= 'Alt.UserAltrueAction') 
def awardAltruePoints(instance, created=True, **kwargs):
    if created:
        user = instance.profile_acting
        profile = UserProfile.objects.get(pk =user.pk)
        #get point_wallet
        point_wallet = AltruePoints.objects.get(account = user )

        #get_specific_action to be rewarded
        the_action = AltrueAction.objects.get(pk= instance.altrue_action.pk)
        
        requirementsNeededForNextLevel = user.requirementsForNextLevel.all()
        #remove action from list
        if the_action in requirementsNeededForNextLevel:
            user.requirementsForNextLevel.remove(the_action)
                        
        else:
            pass
        #check how many times user has compleated specific action to see if they arent over the maximum to receive points
        noOfActionsAlreadyDone = UserAltrueAction.objects.filter(profile_acting = user, altrue_action =the_action)
        # award if they havent reached the max number of actions
        if len(noOfActionsAlreadyDone) <= int(the_action.number_of_occurrences):
            #check if the action was promoted and give promotion if so
            if the_action.is_promoted == True:
                UserAltrueAction.objects.filter(pk= instance.pk).update(is_promotion =True)

                amount_awarded = the_action.points_awarded * the_action.promotion.multiplier
                point_wallet.balance += amount_awarded
                point_wallet.save()
            else:
                amount_awarded = the_action.points_awarded
                point_wallet.balance += amount_awarded
                point_wallet.save()

        else:
            pass
        
        if profile.altrue_level.level_number == 0:
            nl = user.checkaggregates()
            print(nl)
            for code in nl:
                if code is not None:
                    thecode= AltrueActionCode.objects.get(code = code)
                    action = AltrueAction.objects.get(action_code = thecode)       
                    already_done =  UserAltrueAction.objects.filter(profile_acting = user, altrue_action=action)
                    if len(already_done)==0:
                        UserAltrueAction.objects.create(profile_acting = user, altrue_action= action)
                    else:
                        pass
                else: 
                    pass
        
            yo = (profile.needsTolevelUp())
        
        
            if yo != False:
                profile.updateLevel(yo['number'])
            
            pass
        else:
            pass
    else:
        pass
    

        
        





## Updates the User's wallet balance when user receives a donation
@receiver([post_save, post_delete], sender= Donation)
def updateUserAccountBalance(instance, **kwargs):
    donation_amount = instance.donation_amount
    balance = Balance.objects.get(pk = instance.receiver_id)
    love = balance.balance
    new_amount = love + donation_amount
    balance.balance = new_amount
    balance.save(update_fields=['balance'])
    

# @receiver(post_save, sender = AltrueAction)
# def levelNoneCheck(sender, instance, created=False, **kwargs):
#     if created and instance.altrue_level.level_number is 0:
#         print('about to check for')



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
# @receiver(pre_save, sender=UserProfile)
# def create_AltruePoints(sender, instance, created=False, **kwargs):
#     if created:
#         AltruePoints.objects.get_or_create(account= instance)
#         levelo = AltrueLevel.objects.get(level_number =0)
#         instance.altrue_level = levelo
#         instance.save(update_fields=['altrue_level'])
#         try:
#             if instance.altrue_level == None and len(instance.requirementsForNextLevel.all()) <1:
#                 levlone =AltrueLevel.objects.get(level_number= 1)
#                 requirements = levlone.requiredActions.all()
#                 reqs_needed = []
#                 for requirement in requirements:
#                     action =AltrueAction.objects.get(id =requirement.id)
#                     reqs_needed.append(action)
#                 for reqs in reqs_needed:
#                     instance.requirementsForNextLevel.add(reqs)
                
                
            
            
#         except: AltruePoints.DoesNotExist
        
#         # levelo = AltrueLevel.objects.get(level_number =0)
#         # instance.altrue_level = levelo
#         # # get next level requirements

#         levlone =AltrueLevel.objects.get(level_number= 1)
#         requirements = levlone.requiredActions.all()
#         reqs_needed = []
#         for requirement in requirements:
#             action =AltrueAction.objects.get(id =requirement.id)
#             reqs_needed.append(action)
#         for reqs in reqs_needed:
#             instance.requirementsForNextLevel.add(reqs)
#         # instance.save(update_fields= ['altrue_level', 'requirementsForNextLevel'])
   
            
        


# @receiver(pre_save, sender= UserProfile)
# def qr_codeNprofilePic(sender, instance, **kwargs):
#     try:
#         obj = sender.objects.get(pk=instance.pk)
#     except sender.DoesNotExist:
#         pass
#     else:
#         if not obj.username == instance.username:
#             newqr = sender.generate_qr()
   