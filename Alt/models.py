from django.db import models
from django.conf import settings
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField, IntegerField
from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField
from django.dispatch.dispatcher import receiver
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.template.defaultfilters import slugify
from django.db.models.signals import post_delete, post_save, pre_save
from django.core.validators import MinValueValidator, MaxValueValidator 
from django.core.exceptions import ObjectDoesNotExist
import random
import string
from django.apps import apps
from django.utils import timezone


class ProfileImage(models.Model):
    profile = models.OneToOneField("api.UserProfile",  on_delete=models.CASCADE,  related_name ='profile_pic', blank = True, null = True)
    image = models.ImageField(upload_to= 'profiles', null = True, blank = True)

    def __str__(self):
        return self.profile.user.email + "'s profile picture"
    


class Country(models.Model):
    name= models.CharField( max_length=50, blank=False, null=False)
    flag =models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name

class AltrueActionCode(models.Model):
    code= models.CharField(max_length=50, blank= True, null= True)

    def __str__(self):
        return self.code


class AltrueAction(models.Model):
    requirement = models.TextField()
    points_awarded = models.IntegerField(blank = True, null = True)
    number_of_occurrences = models.IntegerField(blank = True, null=True)
    action_code = models.ForeignKey('Alt.AltrueActionCode', on_delete=models.CASCADE, blank = True, null = True)
    is_promoted = models.BooleanField(default=False)
    promotion = models.ForeignKey("Alt.AltruePointPromotion", on_delete=models.CASCADE, blank = True, null = True )

    def __str__(self):
        return self.requirement+' awards ' + str(self.points_awarded) +' Altrue points'

class UserAltrueAction(models.Model):
    profile_acting = models.ForeignKey("api.UserProfile", on_delete=models.CASCADE)
    altrue_action = models.ForeignKey('Alt.AltrueAction', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return  ' awarded to ' +self.profile_acting.user.email+ ' for ' 
    

class AltruePointPromotion(models.Model):
    POINT_PROMOTION_INCREASE =(
        (2, 'Double'),
        (3, 'Triple'),
       
    ) 
    DONATION_INCREASE=(
        (10, 'Ten Percent'),
        (20, 'Twenty Percent'),
        (50, 'Fifty Percent'),
        (100, 'One Hundred Percent')
    )
    multiplier  = models.IntegerField(choices=POINT_PROMOTION_INCREASE, null = True, blank= True )
    name = models.CharField(max_length = 50, null= True, blank = True)
    description= models.TextField(blank= True, null= True)
    donation_increase = models.IntegerField(choices= DONATION_INCREASE, null = True, blank=True)
    




class AltrueLevel(models.Model):
    level_number = models.IntegerField(blank=True, null= True)
    name = models.CharField(max_length=50, blank=False, null= False)
    requiredActions = models.ManyToManyField(AltrueAction, blank=True)
    minimum_points = models.IntegerField(blank = False, null= False )
    maximum_points = models.IntegerField(blank = False, null = False)


    def __str__(self):
        return self.name


class FriendInvite(models.Model):
    inviter = models.OneToOneField('api.UserProfile', on_delete=models.CASCADE, blank=True, null= True)
    invited = models.CharField(blank= False, null= False, max_length= 50)
    invite_code = models.CharField(max_length= 8, blank=True, null=True)
    completed = models.BooleanField(default= False)
    invite_date = models.DateTimeField(auto_now_add=True)
    action = models.ForeignKey('Alt.AltrueActionCode',  on_delete=models.CASCADE, blank=True, null=True)


    def __str__(self):
        return ' invited ' +self.invited
    

    def create_code(self):
        letters = string.ascii_letters
        randomized = ( ''.join(random.choice(letters) for i in range(7)) )
        self.invite_code = randomized

    
    def save(self, *args, **kwargs):
       self.create_code()
       
       super(FriendInvite, self).save(*args, **kwargs) # Call the real save() method
    


class Category(models.Model):
    name = models.CharField(max_length = 50, blank=False, )
    image = models.CharField(max_length=50)
    information =models.TextField()

    
    def __str__(self):
        return self.name
    
    

class AtrocityShirt(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False)
    price = models.FloatField()
    discount_price = models.FloatField(blank= True, null=True)
    shirt_type = models.CharField(max_length=30)
    country = models.ForeignKey('Alt.Country', on_delete=models.CASCADE)
    shirt_image = models.CharField( max_length=150)
    original_image = models.CharField(max_length =150)
    slug = models.SlugField(unique = True, null=True, blank=True)
    featured = models.BooleanField(blank=True, null=True)
    date_added= models.DateTimeField(auto_now_add=True)
  

    def __str__(self):
        return self.name
    def slug(self):
        return slugify(self.name)


class Atrocity(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    region = models.CharField(max_length=30, blank=False, null=False)
    info= models.TextField()
    image_url = models.TextField()
    category = models.ManyToManyField('Alt.Category', blank=True, null =True, related_name='atrocity')
    country = models.ForeignKey('Alt.Country', on_delete=models.CASCADE,blank=True, null=True )
    slug = models.SlugField(unique = True) 
    featured= models.BooleanField(blank = False, null = False, default=False)
    date_added= models.DateTimeField( auto_now_add=True)
    videoURL= models.URLField( max_length=200)



    @property
    def total_balance(self):
        return self.balance.balance

   
    @property
    def atrocity_shirt_list(self):
        shirt_list = []
        category = self.category.all()
        for categories in category:
           return categories.shirt.all()
    
    # find the nonprofits associated with the category of the atrocity, but exclude nonprofits associated with atrocity
    @property
    def np_list(self):
        category= self.category.all()
        np = []
        for categories in category:
            nps = categories.NonProfit.all()
            return nps
            
        
    def __str__(self):
        return self.title
    def slug(self):
        return slugify(self.title)        

    def get_absolute_url(self):
        return reverse ('Alt:Atrocity', kwargs={'slug':self.slug})

    def get_categories(self):
        return Atrocity.objects.filter(category__id =self.id)

        
       


class Shirt(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False)
    price = models.FloatField()
    discount_price = models.FloatField()
    shirt_type = models.CharField(max_length=30, blank=False, null=False) 
    country = models.ForeignKey('Alt.Country', on_delete=models.CASCADE, blank=True, null=True)
    shirt_image = models.CharField( max_length=150)
    original_image = models.CharField(max_length =150)
    slug = models.SlugField(unique = True, null=True, blank=True)
    featured = models.BooleanField(blank = False, null=False, default=False)
    date_added= models.DateTimeField(auto_now_add=True)
    category = ForeignKey('Alt.Category', blank= True, on_delete=models.CASCADE, related_name='shirt')
    altrue_story = models.TextField(blank = True, null=True)

    @property
    def similar_shirts(self):
        cat = self.category
        return Shirt.objects.filter(category = cat).exclude(id= self.id)
    
    @property
    def atrocityList(self):
        cat = self.category
        return Atrocity.objects.filter(category = cat)

    def __str__(self):
        return self.name
    

    def addToCart(self):
        return reverse('core: add-to-cart', kwargs={
            'slug':self.slug
        })

    
    def removeFromCart(self):
        return reverse( 'core: remove-from-cart', kwargs={
            'slug':self.slug
        })


    def get_absolute_url(self):
        return reverse("Alt:shirts", kwargs={"slug": self.slug})

    def no_of_ratings(self):
        ratings = Rating.objects.filter(shirt =self)
        return len(ratings)

    def average_rating(self):
        sum = 0
        ratings = Rating.objects.filter(shirt =self)
        for rating in ratings:
            sum += rating.stars
        if len(ratings) > 0:
            return sum /len(ratings)
        else:
            return 0
             
    def get_categories(self):
        return Shirt.objects.filter(category__id =self.id)

def slug_generator(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug='SLUG'

pre_save.connect(slug_generator, sender=Shirt)    
    
class Rating(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True, editable=False)
    shirt = models.ForeignKey("Alt.Shirt", on_delete=models.CASCADE)
    user = models.ForeignKey("api.User", on_delete=models.CASCADE)
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = (('user', 'shirt'),)
        index_together = (('user', 'shirt'),)


    def __str__(self):
        return self.shirt.name

    def get_absolute_url(self):
        return reverse("Rating_detail", kwargs={"pk": self.pk})



class NonProfit(models.Model):
    name= models.CharField(max_length=50, blank=False, null=False)
    logo =  models.TextField(blank = True, null = True)
    description =models.TextField()
    year_started = models.IntegerField()
    mission_statement=models.TextField()
    vision_statement=models.TextField()
    website_url= models.URLField()
    category = models.ManyToManyField(Category, blank=True, null=True, related_name='NonProfit' )
    slug = models.SlugField(unique = True, blank =True, null= True)
    featured = models.BooleanField(blank=False, null=False, default=False)
    date_added= models.DateTimeField(auto_now_add=True)
    main_image= models.CharField(max_length=200, blank= True, null = True)
    owner = models.OneToOneField('api.UserProfile', on_delete=models.CASCADE, related_name='nonprofit', null=True)
    contributors = models.ManyToManyField('api.UserProfile', related_name='contributors', blank= True)
    facebook = models.CharField(max_length = 30, blank = True, null = True)
    instagram = models.CharField(max_length = 30, blank = True, null = True)

    @property
    def companies_supporting(self):
        companies= self.company.all()
        company_list=[]
        for company in companies:
            if(company.logo):
                company_list.append({company.name: company.logo})
            company_list.append({company.name})
        return company_list
            
        
    @property
    def nonprofit_links(self):
        links = 'api.Links'.objects.filter(nonprofit = self)
        return links

    @property
    def total_balance(self):
        return self.balance.balance

    @property
    def shirtList(self):
        categories = self.category.all()
        for category in categories:
            return category.shirt.all()
    @property
    def atrocity_List(self):
        categories = self.category.all()
        for category in categories:
            return category.atrocity.all()

    def get_absolute_url(self):
        return reverse("Alt:NonProfit", kwargs={"slug": self.slug})
    

    def get_categories(self):
        return NonProfit.objects.filter(category__id =self.id)

    def __str__(self):
        return self.name

    

    
class OrderItem(models.Model):
    user = models.ForeignKey("api.UserProfile", on_delete=models.CASCADE)
    ordered_shirt = models.ForeignKey("Alt.Shirt", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    
    def __str__(self):
        return f'{self.quantity} of {self.ordered_shirt.name}'


    def get_total_shirt_price(self):
        return self.quantity * self.ordered_shirt.price

    def get_discount_shirt_price(self):
        return self.quantity * self.ordered_shirt.discount_price

    def get_amount_donated(self):
        return self.get_total_shirt_price() * .35

    def get_final_price(self):
        if self.ordered_shirt.discount_price:
            return self.get_discount_shirt_price()
        return self.get_total_shirt_price()


class Order(models.Model):
    user = models.ForeignKey("api.UserProfile", on_delete=models.CASCADE, related_name='orders')
    shirts = models.ManyToManyField("Alt.OrderItem")
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default = False)

    def __str__(self):
        return self.user.user.email

    def get_total_price(self):
        total = 0
        for order_item in self.shirts.all():
            total += OrderItem.get_final_price()
        return total





class CheckoutAddress(models.Model):
    user = models.ForeignKey('api.UserProfile', on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100, blank=True, null=True)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    special_directions = models.TextField(blank= True, null = True)

    def __str__(self):
        return self.user.email




class NonProfitBalance(models.Model):
    nonprofit= models.OneToOneField(NonProfit, on_delete=models.CASCADE, related_name='balance')
    balance = models.DecimalField(decimal_places=2, max_digits=10, default=0)
   
    
    # def update_balace(self, amount):
    #     new_amount = self.balance + amount
    #     self.balance = new_amount
    #     self.save()

    
    def __str__(self):
        return self.nonprofit.name
    def get_absolute_url(self):
        return reverse("NonProfitBalOreance_detail", kwargs={"pk": self.pk})

class AtrocityBalance(models.Model):
    atrocity = models.OneToOneField(Atrocity, on_delete=models.CASCADE, related_name = 'balance')
    balance = models.DecimalField(decimal_places=2, max_digits = 10, default=0)
    last_transaction = models.DateTimeField( auto_now=True, null= True, blank= True)
    
    

    # def update_balance(self, amount ):
    #     new_amount = self.balance + amount
    #     self.balance = new_amount
    #     self.save()
    #     return self

    def __str__(self):
        return self.atrocity.title
    
    def get_absolute_url(self):
        return reverse('AtrocityBalance_detail', kwargs={"pk": self.pk})





class CompanyStore(models.Model):
    street_address = models.CharField(max_length=10, blank= True, null=True)
    zip = models.CharField(max_length=100, blank = True, null=True)
    country = CountryField(multiple=False)
    state = models.CharField(max_length=2, null=True, blank=True)


    

    class Meta:
        verbose_name = ("CompanyStore")
        verbose_name_plural = ("CompanyStores")

    def __str__(self):
        return self.location

    def get_absolute_url(self):
        return reverse("CompanyStore_detail", kwargs={"pk": self.pk})




class ForProfitCompany(models.Model):
    owner = models.OneToOneField("api.UserProfile", on_delete=models.CASCADE)
    name= models.CharField(max_length = 30, blank=True, null= True)
    contributors = ManyToManyField("api.UserProfile",related_name='forprofitcontributors', blank=True, null=True)
    nonprofits = ManyToManyField(NonProfit,related_name='company_nonprofit', blank= True)
    atrocities = ManyToManyField(Atrocity, related_name ='company_atrocity', blank = True)
    year_started = models.CharField(max_length= 4, blank = True, null=True)
    logo = models.CharField(max_length = 200, blank=True, null=True)
    image = models.CharField(max_length = 200, blank=True, null=True)
    headquarters = models.CharField(max_length = 50,  blank= True, null= True)
    mission = models.CharField(max_length = 100, blank=True, null= True)
    locations = ManyToManyField(CompanyStore, related_name = 'company', blank=True, null=True)
    description = models.TextField(blank= True, null = True)
    website_address = models.TextField(blank=True, null = True)
    slug = models.SlugField(blank=True, null=True, unique=True)
    categories = models.ManyToManyField(Category,related_name = 'company')
    contributors_pending = models.ManyToManyField('api.UserProfile', related_name='contributors_pending', blank =True)
    is_featured= models.BooleanField(default= False)
    facebook = models.CharField(max_length = 50, blank= True, null =True)
    instagram = models.CharField(max_length =30,blank = True, null =True)
    coupons_of_company = ManyToManyField('Alt.CompanyCoupon', related_name='coupons_of_company', blank=True)
    

    class Meta:
        verbose_name_plural = ("ForProfitCompanies")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("CompanyStore_detail", kwargs={"pk": self.pk})

    def slugFormatter(self):
        word = self.name
        update = word.split()[0]
        return update
        
    def save(self, *args, **kwargs):
        slug = self.slugFormatter()
        self.slug = slug + self.year_started
        super(ForProfitCompany, self).save()


class CompanyCoupon(models.Model):
    name= models.CharField(max_length = 30, blank=False, null=False)
    locations =models.ManyToManyField('Alt.CompanyStore', related_name ='coupon', blank=True, null=True)
    company = models.ForeignKey('Alt.ForProfitCompany',  on_delete=models.CASCADE, related_name='coupon', blank =False, null=False)
    coupon_code = models.CharField(max_length= 10, blank = True, null = True)
    expiration_date = models.DateField(blank = True, null=True)
    description =  models.TextField(blank= True, null=True)
    coupon_image = models.CharField(blank = True, null=True, max_length=200)
    slug = models.SlugField(blank=True, null=True )


    

    class Meta:
        verbose_name = ("CompanyCoupon")
        verbose_name_plural = ("CompanyCoupons")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("CompanyCoupon_detail", kwargs={"pk": self.pk})


    def save(self, *args, **kwargs):
        self.slug = self.company.name + str(self.pk)
        if not self.name:
            self.name = self.slug
        super(CompanyCoupon, self).save()



class CompanyNonProfitRelationship(models.Model):
    
    MATCH_PERCENTAGE =(
        (10, 'Ten Percent'),
        (25, 'Twenty Five Percent'),
        (50, 'Fifty Percent'),
        (100, 'Full Match')
    )
    company = models.ForeignKey('Alt.ForProfitCompany',  on_delete=models.CASCADE, related_name='npcompanyrelation')
    nonprofit = models.ForeignKey("Alt.NonProfit",  on_delete=models.CASCADE, related_name='npcompanyrelation')
    match_level = models.IntegerField(choices=MATCH_PERCENTAGE)
    total_raised = models.FloatField(default=0, null=True, blank= True)
    funding_limit = models.FloatField(default=0, null=True, blank=True )

    
    

    class Meta:
        verbose_name = ("CompanyNonProfitRelationship")
        verbose_name_plural =("CompanyNonProfitRelationships")

    def __str__(self):
        return f'{self.company.name} matches {self.match_level}% for donations to {self.nonprofit.name}'

    def get_absolute_url(self):
        return reverse("CompanyNonProfitRelationship_detail", kwargs={"pk": self.pk})


class CompanyAtrocityRelationship(models.Model):

    MATCH_PERCENTAGE =(
        (10, 'Ten Percent'),
        (25, 'Twenty Five Percent'),
        (50, 'Fifty Percent'),
        (100, 'Full Match')
    )
    company = models.ForeignKey('Alt.ForProfitCompany',  on_delete=models.CASCADE, related_name='atrocitycompanyrelation')
    atrocity = models.ForeignKey('Alt.Atrocity',  on_delete=models.CASCADE, related_name='atrocitycompanyrelation')
    match_level = models.IntegerField(choices=MATCH_PERCENTAGE)
    total_raised = models.FloatField(default = 0, blank= True, null= True)
    funding_limit = models.FloatField(blank=True, null=True, default=0)
    

    class Meta:
        verbose_name = ("CompanyAtrocityRelationship")
        verbose_name_plural = ("CompanyAtrocityRelationships")

    def __str__(self):
        return f'{self.company.name} matches {self.match_level}% for donations to {self.atrocity.title}'

    def get_absolute_url(self):
        return reverse("CompanyAtrocityRelationship_detail", kwargs={"pk": self.pk})
 
class CompanyBalance(models.Model):
    company = models.OneToOneField("Alt.ForProfitCompany",  on_delete=models.CASCADE) 
    balance = models.DecimalField( max_digits=7, decimal_places=2, default =0)
    last_transaction = models.DateTimeField(auto_now= True, null=True, blank = True) 
    
    def __str__(self):
        return self.company.name
    

    
class CompanyDonation(models.Model):
    company = models.ForeignKey('Alt.ForProfitCompany', on_delete=models.CASCADE, related_name='company_donation')
    wallet = models.ForeignKey('Alt.CompanyBalance', on_delete=models.CASCADE, related_name = 'company_donation')
    amount = models.DecimalField( max_digits=6, decimal_places=2)
    nonprofit = models.ForeignKey('Alt.NonProfit', blank= True, null = True, on_delete=models.CASCADE, related_name = 'company_donation_nonprofit')
    atrocity = models.ForeignKey('Alt.Atrocity', blank=True, null=True, on_delete=models.CASCADE, related_name='company_donation_atrocity')
    donation_date = models.DateTimeField( auto_now_add=True, null=False, blank=False)
    
    def __str__(self):
        return self.company.name
    


class NonProfitProject(models.Model):
    nonprofit = models.ForeignKey('Alt.NonProfit', on_delete=models.CASCADE, related_name='np_project_nonprofit')
    cause = models.ForeignKey('Alt.Category', on_delete=models.CASCADE, related_name='np_project_cause')
    atrocity = models.ForeignKey('Alt.Atrocity', on_delete=models.CASCADE, related_name='np_project_atrocity', blank= True, null= True)
    title = models.CharField(max_length = 140, blank = True, null = True)
    information = models.TextField(blank = True, null = True)
    fundraising_goal = models.IntegerField()
    followers = models.ManyToManyField('api.UserProfile', related_name='np_project_followers' , blank = True)
    supporters = models.ManyToManyField('api.UserProfile', related_name='np_project_supporters', blank = True)


    def __str__(self):
        if self.title:
            return self.title
        return self.nonprofit.name
       
    
    def get_absolute_url(self):
        return reverse("NonProfitProject_detail", kwargs={"pk": self.pk})
    
        

class NonProfitAtrocityRelationShip(models.Model):
    nonprofit = models.ForeignKey('Alt.NonProfit', on_delete=models.CASCADE, related_name='nonprofitatrocityRelationship')
    atrocity = models.ForeignKey('Alt.Atrocity', on_delete= models.CASCADE, related_name='nonprofitAtrocityRelationship')
    projects = models.ManyToManyField('Alt.NonProfitProject', related_name='nonprofitAtrocityRelationship', blank= True)
    

    def __str__(self):
        if self.projects:
            return f'{self.nonprofit.name} is working on {len(self.projects.all())} to help {self.atrocity}'
        return  f'{self.nonprofit.name} is working to help {self.atrocity.title}'
    
    def get_absolute_url(self):
        return reverse("NonProfitAtrocityRelationship_detail", kwargs={"pk": self.pk})
    




# Model Signals Below ---->>>

@receiver(post_save, sender= NonProfit)
def create_nonprofit_account(sender, instance=None, created=False, **kwargs ):
    if created:
        NonProfitBalance.objects.create(nonprofit =instance)
    else:
        non = NonProfitBalance.objects.filter(nonprofit = instance)
        if non.exists():
            pass
        else:
            NonProfitBalance.objects.create(nonprofit= instance)
            
            
@receiver(post_save, sender = ForProfitCompany)
def create_company_wallet(sender, instance = None, created=False, **kwargs):
    if created:
        ForProfitCompany.objects.create(company = instance)
    else:
        comp = CompanyBalance.objects.filter(company =instance)
        if comp.exists():
            pass
        else:
            CompanyBalance.objects.create(company = instance)

@receiver(post_save, sender = Atrocity)
def create_atrocity_account(sender, instance=None, created=False, **kwargs):
    if created:
        AtrocityBalance.objects.create(atrocity = instance)
    else:
        atro = AtrocityBalance.objects.filter(atrocity = instance)
        if atro.exists():
            pass
        else:
            AtrocityBalance.objects.create(atrocity = instance)

@receiver([post_save, post_delete], sender= 'api.UserDonation')
def updateBalancesFromUserDonation( instance, **kwargs):
    if instance.nonprofit:
        nonprof= NonProfitBalance.objects.get(nonprofit = instance.nonprofit)
        if instance.amount > 0:
            new_amount = instance.amount + nonprof.balance
            nonprof.balance = new_amount
            nonprof.save(update_fields =['balance'])
        else: pass
    elif instance.atrocity:
        atroc = AtrocityBalance.objects.get(atrocity = instance.atrocity)
        if instance.amount > 0:
            new_amount = instance.amount + atroc.balance
            atroc.balance = new_amount
            atroc.save(update_fields =['balance'])
        else:pass
    else:
        pass

@receiver(post_save, sender = NonProfitProject)
def createNPRelationShipIfnotCreated(instance, created, **kwargs):
    if created and instance.atrocity:
       obj,created = NonProfitAtrocityRelationShip.objects.get_or_create(atrocity = instance.atrocity, nonprofit =instance.nonprofit)
       obj.projects.add(instance)


# @receiver(post_save, sender= 'api.UserProfile')
# def friendInvite(instance, created, **kwargs):
#     if created:
#         FriendInvite.objects.get(inviter = str(instance.user.email))


   
    
    

@receiver(post_save, sender ='api.CompanyMatchDonation')
def updateTotal(instance, created = False, **kwargs):
    if created:
        if instance.nonprofit:
            co = ForProfitCompany.objects.get(pk =instance.company_id)
            wallet = CompanyBalance.objects.get(company =co)

            CompanyDonation.objects.create(amount= instance.amount, nonprofit = instance.nonprofit, company = instance.company, wallet = wallet)
            amount = float(instance.amount)
            new_company_wallet_amount = float(wallet.balance) - amount
            wallet.balance = new_company_wallet_amount
            wallet.save(update_fields=['balance']) 
           
            try:
                com = CompanyNonProfitRelationship.objects.get(company = instance.company, nonprofit =instance.nonprofit)
                updated_total = float(instance.amount) + com.total_raised
                com.total_raised = updated_total
                com.save(update_fields=['total_raised'])
              
            except: ObjectDoesNotExist
        elif instance.atrocity:
            cos = ForProfitCompany.objects.get(pk =instance.company_id)
            wallet = CompanyBalance.objects.get(company=cos)
            CompanyDonation.objects.create(amount= instance.amount, nonprofit = instance.nonprofit, company = instance.company, wallet = wallet)
            amount = float(instance.amount)
            new_company_wallet_amount = float(wallet.balance) - amount
            wallet.balance = new_company_wallet_amount
            wallet.save(update_fields=['balance']) 
            try:
                co = CompanyAtrocityRelationship.objects.get(company = instance.company, atrocity = instance.atrocity)
                updated_tot = float(instance.amount) + co.total_raised
                co.total_raised = updated_tot
                co.save(update_fields=['total_raised'])
                
            except: ObjectDoesNotExist
        pass
