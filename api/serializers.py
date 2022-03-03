from os import read
import profile
from django.conf import settings
from datetime import datetime, timedelta

from django.db.models.fields import IntegerField
from django.db.models.fields.related import RelatedField
from django.forms import all_valid
from django.template.defaultfilters import truncatechars_html
from rest_framework import serializers
from api.models import AltruePoints, Balance, CompanyMatchDonation, Donation, Donor, Link, User, UserDonation, UserProfile
from Alt.models import AltrueAction, AltrueLevel, Atrocity, AtrocityBalance, Category, CompanyAtrocityRelationship, CompanyCoupon, CompanyDonation, CompanyNonProfitRelationship, CompanyStore, Country, ForProfitCompany, NonProfit, NonProfitBalance, Order, OrderItem, Rating, Shirt, NonProfitProject, ProfileImage, ShirtColor, ShirtSize, ShirtVariations
from django.contrib.auth import get_user_model
from drf_writable_nested import WritableNestedModelSerializer, UniqueFieldsMixin, NestedUpdateMixin
from rest_auth.serializers import TokenSerializer
from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
    ListBulkCreateUpdateDestroyAPIView,
)
from rest_flex_fields import FlexFieldsModelSerializer
from django.core.files import File
from django.contrib.sites.models import Site





class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


        


class AltrueLevelSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = AltrueLevel
        fields  = ['name','minimum_points','maximum_points']


class ProfileImageSerializer(FlexFieldsModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:     
        model = ProfileImage
        fields= ['url']

    def get_url(self,obj):
        if settings.DEBUG:  # debug enabled for dev and stage
            return 'http://10.0.0.238:8000'+ obj.image.url 



class CompanyRepSerializer(FlexFieldsModelSerializer):
    
    class Meta:
        model = ForProfitCompany
        fields =['id', 'logo', 'name']


class ProfileRepSerializer(FlexFieldsModelSerializer):
    id = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        
        fields =['username','id', 'profile_picture']

    def get_id(self,obj):
        return obj.pk
    
    def get_profile_picture(self, obj):
        pic = ProfileImage.objects.get(profile = obj)
        serialized = ProfileImageSerializer(pic).data
        return serialized

        

class ColorSerializer(FlexFieldsModelSerializer):
    
    hex = serializers.SerializerMethodField()
    
    class Meta:
        model = ShirtColor
        fields =['color','id', 'hex']
    
    def get_hex(self, obj):
        return '0xFF' + obj.hex_code


class CountrySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'flag']

class AtrocityShirtSerializer(FlexFieldsModelSerializer):
    class Meta:
        
        model = Shirt
        depth = 1
        fields = ('id','name', 'price','shirt_image','category')
        
    

class AltrueActionSerializer(FlexFieldsModelSerializer):
    
    class Meta:
        model = AltrueAction
        fields = ['requirement', 'points_awarded']



class AtrocityNonProfitSerializer(FlexFieldsModelSerializer):

    class Meta:
        model= NonProfit
        depth=1
        fields=( 'id','name','logo')

class CategorySerializer(FlexFieldsModelSerializer):
    nonprofit_count = serializers.SerializerMethodField()
    all_nonprofits = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields=['id','name', 'image','information','all_nonprofits','nonprofit_count' ]
        depth = 1
    
    def get_all_nonprofits(self, obj):
        nonprofit = NonProfit.objects.filter(category = obj)
        if nonprofit is None:
            return None    
        serialized = NonProfitSerializer(nonprofit, many=True, omit =['facebook','owner','category', 'description', 'year_started', 'mission_statement','vision_statement','website_url','category','slug', 'shirtList', 'main_image','total_balance', 'atrocity_List','companies_supporting','nonprofit_links','links', 'projects','donationsInWeek','recentDonors','matchingPartnerships'])
        return serialized.data

    def get_nonprofit_count(self, obj):
         nonprofit = NonProfit.objects.filter(category = obj)
         if nonprofit is None:
             return 0
         return len(nonprofit)


class ProjectRepSerializer(FlexFieldsModelSerializer):
    supporters = ProfileRepSerializer(many=True, read_only=True)
    followers = ProfileRepSerializer(many= True, read_only=True)
    cause = CategorySerializer(read_only=True)
    fundraising_goal = serializers.SerializerMethodField()
    currentFunds = serializers.SerializerMethodField()

    class Meta:
        model = NonProfitProject
        fields = ['id','title', 'fundraising_goal', 'currentFunds','information', 'cause','supporters', 'followers']


        
    def get_fundraising_goal(self, obj):
        return str(obj.fundraising_goal)
    
    def get_currentFunds(self, obj):
        total =[]
        project_donations = UserDonation.objects.filter(project = obj)
        for donation in project_donations:
            total.append(donation.amount)
        all = sum(total)
        return all

class CategoryField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        category = Category.objects.get(id = value.id)
        serializer = CategorySerializer(category)
        return serializer.data


class ShirtSizeSerializer(FlexFieldsModelSerializer):
    
    
    sizevalue = serializers.SerializerMethodField()
    
    class Meta:
        model = ShirtSize
        fields = ['size', 'sizevalue']
        
    def get_sizevalue(self, obj):
        return obj.get_size_display()



class NonProfitBalanceSerializer(FlexFieldsModelSerializer):
    
    class Meta:
        model = NonProfitBalance

class AtrocityBalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtrocityBalance
        


class AtrocitySerializer(FlexFieldsModelSerializer):
    country = CountrySerializer(read_only= True, required = False)
    category = CategorySerializer(many= True, read_only=True, required= False, omit=['all_nonprofits','nonprofit_count'])
    atrocity_shirt_list =AtrocityShirtSerializer(many = True, read_only =True) 
    np_list = AtrocityNonProfitSerializer(many=True, read_only=True)
    links= serializers.SerializerMethodField()
    recentDonors= serializers.SerializerMethodField()




    class Meta:
        model = Atrocity
        fields = ('id','title', 'region', 'info' ,'image_url', 'category','country','slug', 'atrocity_shirt_list','videoURL','total_balance', 'np_list','links', 'recentDonors')

    def get_recentDonors(self, obj):
        love = UserDonation.objects.filter(atrocity = obj)
        lis = []
        for lover in love:
            lis.append(lover.user)
        serialized = ProfileRepSerializer(lis, many = True)
        return serialized.data

    def get_links(self, obj):
        links =Link.objects.filter(atrocity = obj)
        linkList= []
        for link in links:  
            linkrep= {"link":link.link,
            'publication':link.publication,
            'author': link.author,
            "title" : link.title}
            linkList.append(linkrep)
        if len(linkList) == 0:
            return None
        return linkList
                        
                    
        



class ShirtAtrocitySerializer(FlexFieldsModelSerializer):
    country = CountrySerializer(read_only= True, required = False)
    category = CategorySerializer(many= True, read_only=True, required= False, omit=['all_nonprofits','nonprofit_count'])

    class Meta:
        model = Atrocity
        fields = ['id','title', 'region', 'info' ,'image_url', 'country', 'category' ]




class ShirtVariationSerializer(FlexFieldsModelSerializer):
    color = ColorSerializer( read_only = True)
    class Meta:
        model = ShirtVariations
        fields = ['image', 'color' ,'shirt']

class ShirtSerializer(FlexFieldsModelSerializer):
    
 
    country= CountrySerializer(read_only=True, required = False)
    category = CategorySerializer( read_only=True, required = False, omit =['all_nonprofits','nonprofit_count'])
    atrocityList = ShirtAtrocitySerializer(read_only =True, required= False, many = True)
    similar_shirts = AtrocityShirtSerializer(read_only =True, many = True)
    available_colors = ColorSerializer(many = True, read_only =True)
    available_sizes = ShirtSizeSerializer(many= True, read_only =True)
    variations = serializers.SerializerMethodField()
    required_level = AltrueLevelSerializer(read_only =True)


   
    

    class Meta:
        
        model = Shirt
        fields = ['id', 'name', 'price', 'country','available_colors','available_sizes',
         'shirt_image', 'category', 'slug','original_image', 'no_of_ratings', 
         'average_rating','altrue_story', 'similar_shirts', 'atrocityList', 'variations','required_level']
        
    def get_variations(self, obj):
        lis = []
        variations = ShirtVariations.objects.filter(shirt_id = obj.id)
        for variation in variations:
            lis.append(variation)
        response = ShirtVariationSerializer(lis, many = True, read_only=True)
        return response.data       
    
    
    # def get_available_colors(self, obj):
    #     li =[]
    #     for color in obj.avaialable_colors.all():
    #         ShirtColor.objects.get(c)
            
    


class ShirtListSerialzier(FlexFieldsModelSerializer):
    
    child = ShirtSerializer()

    
    
    def update(self,instance, validate_data):
        shirt_mapping = {shirt.id: shirt for shirt in instance}
        data_mapping = {item['id']: item for item in validate_data}

        ret=[]
        for shirt_id, data in data_mapping.items():
            shirt = shirt_mapping.get(shirt_id, None)
            if shirt is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(shirt,data))

        for shirt_id, shirt in shirt_mapping.items():
            if shirt_id not in shirt_mapping:
                shirt.delete()

        return ret




class NonProfitListSerializer(serializers.ListSerializer):
    
    
    def update(self,instance, validate_data):
        nonprofit_mapping = {nonprofit.id: nonprofit for nonprofit in instance}
        data_mapping = {item['id']: item for item in validate_data}

        ret=[]
        for nonprofit_id, data in data_mapping.items():
            nonprofit = nonprofit_mapping.get(nonprofit_id, None)
            if nonprofit is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(nonprofit,data))

        for nonprofit_id, nonprofit in nonprofit_mapping.items():
            if nonprofit_id not in nonprofit_mapping:
                nonprofit.delete()

        return ret

    


class NonProfitSerializer(FlexFieldsModelSerializer):
    # name = serializers.CharField()
    # instagram = serializers.CharField()
    # facebook = serializers.CharField()
    # description = serializers.CharField()
    # year_started = serializers.IntegerField()
    # vision_statement = serializers.CharField()
    # mission_statement = serializers.CharField()
    # website_url = serializers.URLField()
    category = CategorySerializer(many= True, read_only=True, omit=['all_nonprofits','nonprofit_count'])
    atrocity_List = ShirtAtrocitySerializer(many=True, read_only =True)
    shirtList = AtrocityShirtSerializer(many = True, read_only = True)
    links = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    owner = ProfileRepSerializer(read_only = True)
    donationsInWeek = serializers.SerializerMethodField(read_only= True)
    recentDonors = serializers.SerializerMethodField(read_only = True)
    matchingPartnerships = serializers.SerializerMethodField(read_only = True)
    avgDonation= serializers.SerializerMethodField(read_only =True)
    


    class Meta:
        model = NonProfit
        fields = ['id','owner','name','logo', 'avgDonation','description','facebook', 'year_started', 'mission_statement','vision_statement','website_url','category','slug', 'shirtList', 'main_image','total_balance', 'atrocity_List','companies_supporting','nonprofit_links','links', 'projects','donationsInWeek','recentDonors','matchingPartnerships']
        depth = 1
    
    def get_links(self, obj):
        links =Link.objects.filter(nonprofit = obj)
        linkList= []
        for link in links:
            linkrep= {"link":link.link,
            'publication':link.publication,
            'author': link.author,
            "title" : link.title}
            linkList.append(linkrep)
        return linkList
    
    def get_recentDonors(self, obj):
        love = UserDonation.objects.filter(nonprofit = obj)
        lis = []
        for lover in love:
            lis.append(lover.user)
        serialized = ProfileRepSerializer(lis, many = True)
        return serialized.data
            
    def get_matchingPartnerships(self, obj):
        relationships = CompanyNonProfitRelationship.objects.filter(nonprofit = obj)
        serialized  = CompanyNonProfitRelationshipSerializer(relationships , many = True, omit=['nonprofit'])
        return serialized.data
        
    def get_avgDonation(self, obj):
        uds = UserDonation.objects.filter(nonprofit =obj)
        cds = CompanyMatchDonation.objects.filter(nonprofit = obj)
        totalDonationCount = len(cds) + len(uds)
        if totalDonationCount > 0:
            avg = obj.total_balance / totalDonationCount
            
            return round(avg,2)
        return 0
        
         
    
    def get_donationsInWeek(self, obj):
        startdate = datetime.today()
        enddate = startdate + timedelta(days=6)
        companydonations =CompanyDonation.objects.filter(donation_date__range = [startdate, enddate])
        userdonations = UserDonation.objects.filter(donation_date__range = [startdate, enddate])           
        all_donations = len(companydonations) + len(userdonations)
        return all_donations
        
                      
    def get_projects(self, obj):
        projects = NonProfitProject.objects.filter(nonprofit = obj)
        projectList = []
        follower_list =[]
        for project in projects:
            projectList.append(project)
        response = ProjectRepSerializer(projectList, many= True, read_only=True )
          
            # atrocity = AtrocitySerializer(source= project.atrocity, read_only = True)
            # category = CategorySerializer(source = project.cause, read_only=True)
                
            
            # project_rep = {
                
            #      'cause':category.data,
            #     'atrocitu': atrocity.data,
            #       'information':project.information,
            #       'fundraising_goal':project.fundraising_goal,
            #       'title': project.title,
                
            #       }
            # projectList.append(project_rep)
        return response.data
            
    def create(self, validated_data):
        
        NonProfit.objects.create(**validated_data)

class RatingSerializer(FlexFieldsModelSerializer):

    class Meta:
        model = Rating
        fields= ['user', 'shirt', 'stars']



class UserSerializer(FlexFieldsModelSerializer):

    profile= serializers.HyperlinkedRelatedField(many= False, read_only= False, queryset= UserProfile.objects.all() ,view_name = 'userprofile-detail' )

    
    class Meta:
        model = User
        fields = ('url', 'email', 'first_name', 'last_name', 'password','username','id' ,'profile', 'profile_created' )
        extra_kwargs = {'password': {'write_only': True},
                        'profile':{}}
        depth = 1

    def create(self, validated_data):
        userprofile_data = validated_data.pop('userprofile')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, **userprofile_data)
        return user

    def update(self, instance, validated_data):
        userprofile_data = validated_data.pop('userprofile')
        userprofile = instance.userprofile

        instance.email = validated_data.get('email', instance.email)
        instance.save()

        userprofile.title = userprofile_data.get('title', userprofile.title)
        userprofile.dob = userprofile_data.get('dob', userprofile.dob)
        userprofile.address = userprofile_data.get('address', userprofile.address)
        userprofile.country = userprofile_data.get('country', userprofile.country)
        userprofile.city = userprofile_data.get('city', userprofile.city)
        userprofile.zip = userprofile_data.get('zip', userprofile.zip)
        userprofile.photo = userprofile_data.get('photo', userprofile.photo)
        userprofile.save()

        return instance

 
 
 

class OrderShirtSerializer(FlexFieldsModelSerializer):
    
    
    class Meta:
        model= Shirt
        fields =('id','name','price','shirt_type','shirt_image','slug',)
        omit =['available_sizes','available_colors']


class OrderItemSerializer(FlexFieldsModelSerializer):
    ordered_shirt = OrderShirtSerializer(omit=['avaialable_sizes', 'available_colors']) 
    size = ShirtSizeSerializer() 
    color = ColorSerializer()
    
    
    class Meta:
              
        model = OrderItem
        depth=2
        fields=('ordered_shirt', 'quantity', 'color', 'size')
    
    def create(self, validated_data):
        return OrderItem(**validated_data)
    


class OrderSerializer(FlexFieldsModelSerializer):
    shirts = OrderItemSerializer(many =True)

    class Meta:
        
        

        model = Order
        depth=1
        fields=('shirts', )    

class NonProfit_UserDonation_Serializer(FlexFieldsModelSerializer):

    class Meta:
        model = NonProfit
        fields=('name', 'logo')        


class UserDonationSerializer(FlexFieldsModelSerializer):

    nonprofit= NonProfitSerializer(fields =['id','name','logo'])
    atrocity = AtrocitySerializer(fields = ['id', 'title', 'category'])
    project = ProjectRepSerializer()

    

    class Meta:
        model = UserDonation
        fields=('id','amount', 'nonprofit', 'atrocity', 'project')

    def get_atroCategory(self, obj):
        if obj.atrocity :
            categories = obj.atrocity.category.all()
            category = categories[0]
            return category.name

    def create(self, validated_data):
        return UserDonation(**validated_data)   
    

class DonorSerializer(FlexFieldsModelSerializer):
    
    donation_category = CategorySerializer(read_only=True)
    # date = serializers.SerializerMethodField('get_date')


    class Meta:
        model = Donor
        fields = ('id','email', 'first_name', 'last_name', 'amount_donated', 'donation_category',)

    

    def get_date(self, obj):
        return obj.donation.donation_date
    def get_donation(self,obj):
        return obj.donation_category.name
    


class UserProfileSerializer(FlexFieldsModelSerializer):
   
  
    balance = serializers.ReadOnlyField(source='available')
    donor = DonorSerializer(many= True)
    orders = OrderSerializer(many = True)
    atrocity_list = AtrocitySerializer(many=True)
    shirt_list = ShirtSerializer(many = True, omit=['available_sizes', 'available_colors'])
    nonProfit_list= NonProfitSerializer(many=True, omit=['owner','facebook','description', 'year_started', 'mission_statement','vision_statement','avgDonation','website_url','category','slug', 'shirtList', 'main_image','total_balance', 'atrocity_List','companies_supporting','nonprofit_links','links', 'projects','donationsInWeek','recentDonors','matchingPartnerships'])
    userdonations = UserDonationSerializer(many=True, fields = [])
    NPTotals = serializers.SerializerMethodField()
    AtroTotals = serializers.SerializerMethodField()
    altruepoints = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    altrue_level = AltrueLevelSerializer(read_only =True)
    amount_followers = serializers.SerializerMethodField()
    profiles_following = ProfileRepSerializer(many = True)
    donationTotal = serializers.SerializerMethodField()
    np = serializers.SerializerMethodField()
    comp = serializers.SerializerMethodField()

    requirementsForNextLevel = AltrueActionSerializer(many = True, read_only = True)
    # pointsToNextLevel = serializers.SerializerMethodField()

      
    class Meta:
        model = UserProfile
        fields = ('user','username','altrue_level','title','np','comp','donationTotal', 'dob', 'address', 'country', 'city', 'zip', 'qr_code_img', 'has_company','has_nonprofit','is_companyContributor','is_nonprofitContributor','shirt_list', 'atrocity_list', 'nonProfit_list','profiles_following', 'balance', 'donor', 'orders', 'userdonations', 'amount_following','amount_followers', 'NPTotals' ,'AtroTotals', 'altruepoints', 'profile_picture', 'altrue_level','requirementsForNextLevel')
        expandable_fields ={}
    
    def create(self, validated_data):
        return UserProfile(**validated_data)

    def get_profile_picture(self, obj):
        img = ProfileImage.objects.get(profile = obj)
        serialized = ProfileImageSerializer(img).data
        return serialized
    
    def get_donationTotal(self, obj):
        all_donations = UserDonation.objects.filter(user = obj)
        lis = []
        for donor in all_donations:
            lis.append(float(donor.amount)) 
        total= sum(lis)
        return round(total, 2)
    
    def get_np(self, obj):
        try:
            np = NonProfit.objects.get(owner  = obj)
            serialized = NonProfitSerializer(np, omit=['facebook','owner','description', 'year_started', 'mission_statement','vision_statement','avgDonation','website_url','category','slug', 'shirtList', 'main_image','total_balance', 'atrocity_List','companies_supporting','nonprofit_links','links', 'projects','donationsInWeek','recentDonors','matchingPartnerships'])
            return serialized.data
        except NonProfit.DoesNotExist:
            np = None
            return np
        
    def get_comp(self, obj):
        try:
            com = ForProfitCompany.objects.get(owner = obj)
            serialized = ForProfitCompanySerializer(com, fields=['id', 'name','logo'])
            return serialized.data
        except ForProfitCompany.DoesNotExist:
            com =None
            return com
        
    def get_amount_followers(self, obj):
        users  = UserProfile.objects.all()
        
        
        for user in users:
            lis = 0
            if obj in user.following.all():
                lis+=1
        return lis
    

    def get_pointsToNextLevel(self, obj):
        userPoints = AltruePoints.objects.get(account =obj)
        next_level = AltrueLevel.objects.get(level_number = obj.altrue_level.level_number +1)

        points_left = next_level.minimum_points - userPoints.balance
        return points_left

    def get_NPTotals(self, obj):
        nps= NonProfit.objects.all()
        total =0
        oflist =[]
        lis =[]
        for np in nps:
            alldon = UserDonation.objects.filter(user = obj, nonprofit=np)
            #Have all the nonprofits and the donations made to them
            #for sum up all donation amounts 
            for don in alldon:
                tot = 0
                li= []
                li.append(float(don.amount))
                tot =sum(li)
                lis.append(tot)
            total = sum(lis)
            eachTotal = {np.name: total}
            oflist.append(eachTotal)
            return oflist

    
    def get_altruepoints(self, obj):
        userPoints = AltruePoints.objects.get(account =obj)
        return userPoints.balance
            


    def get_AtroTotals(self, obj):
        atr = Atrocity.objects.all()
        total=0
        ofList = []
        atro_list = []
        for atr in atr:
            alldonations = UserDonation.objects.filter(user = obj, atrocity = atr)
            for don in alldonations:
                tot = 0
                li= []
                li.append(float(don.amount))
                tot =sum(li)
                atro_list.append(tot)
            total = sum(atro_list)
            eachTotal= {atr.title : total}
            ofList.append(eachTotal)
            return ofList




        

        
            

    # def partial_update(self, request, *args, **kwargs):
        

   
    # def update(self, instance, validated_data):

class CompanyCouponSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = CompanyCoupon
        fields = ['name', 'expiration_date', 'description', 'coupon_image','coupon_code']
        
    def create(self, validated_data):
        return CompanyCoupon(**validated_data)

class LinkSerializer(FlexFieldsModelSerializer):
    atrocity = AtrocitySerializer()
    nonprofit = NonProfitSerializer(fields =['id', 'name', 'logo'])
  
    
    class Meta:
        model = Link
        fields = ('atrocity', 'link', 'publication','nonprofit','company', 'author')




class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email','profile_created')


class CustomTokenSerializer(TokenSerializer):
    user = UserTokenSerializer(read_only = True)

    class Meta(TokenSerializer.Meta):
        fields = ('key', 'user',)

class CompanyStoreSerializer(FlexFieldsModelSerializer):
    class Meta:
        fields=('location')


class CompanyAtrocityRelationShipSerializer(FlexFieldsModelSerializer):
    atrocity = AtrocitySerializer(fields=['id','title','country', 'category'])
    company = CompanyRepSerializer()
                                  
    class Meta:
        model = CompanyAtrocityRelationship
        fields = ['atrocity','match_level', 'total_raised','funding_limit','company']
        
        
    def create(self, validated_data):
        return CompanyAtrocityRelationship(**validated_data)
        
class CompanyNonProfitRelationshipSerializer(FlexFieldsModelSerializer):
    nonprofit = NonProfitSerializer(fields =['id', 'name', 'logo'])
    company = CompanyRepSerializer()
   
    class Meta:
        model = CompanyNonProfitRelationship
        fields = ['nonprofit','company', 'match_level', 'total_raised','funding_limit']
        
    def create(self, validated_data):
        return CompanyNonProfitRelationship(**validated_data)
    
    
    
    

class ForProfitCompanySerializer(FlexFieldsModelSerializer):
    categories = CategorySerializer(many=True)
    nonprofits = NonProfitSerializer(many = True, fields =['id', 'name', 'logo'])
    atrocities = AtrocitySerializer(many=True, fields=['id','title','country', 'category','np_list'], omit='np_list[np_list]' )
    # locations = CompanyStoreSerializer(many= True, fields=['location'])
    owner = UserProfileSerializer(fields =['user','username','title', 'dob', 'address', 'country', 'city', 'zip', 'qr_code_img'], omit=['shirt_list', 'atrocity_list', 'nonProfit_list', 'balance', 'donor', 'orders', 'userdonations', 'getFollowProfiles'])
    links = serializers.SerializerMethodField()
    coupons = serializers.SerializerMethodField()
    atrocityRelationships = serializers.SerializerMethodField()
    nonprofitRelationships = serializers.SerializerMethodField()
    totalDonated = serializers.SerializerMethodField()
    totalDonationCount = serializers.SerializerMethodField()
    
    
    
    class Meta:
        model = ForProfitCompany
        fields = ['owner','id','name','contributors','image','categories','logo','description','year_started','mission', 'slug','nonprofits', 'atrocities','headquarters','website_address','coupons','links','nonprofitRelationships', 'atrocityRelationships','totalDonated', 'totalDonationCount']
        expandable_fields = {
            ''
            "nonprofits": 
            ('serializer.NonProfitSerializer', 
            {'many':True, "omit": ["shirtList", "atrocity_list"]}),

            "atrocities":(AtrocitySerializer, {"many": True, "omit":['atrocity_shirt_list', 'np_list']})
        }
    def get_links(self, obj):
        lis=[]
        links =Link.objects.filter(company = obj)
        for link in links:
            serialized = LinkSerializer(link).data
            lis.append(serialized)
        return lis
            

    def get_coupons(self, obj):
        lis = []
        coupons = CompanyCoupon.objects.filter(company =obj)
        for coupon in coupons :
            serialized = CompanyCouponSerializer(coupon).data
            lis.append(serialized)
        return lis
            
            
    def get_totalDonationCount(self, obj):
        count = CompanyDonation.objects.filter(company=obj).count()
        return count
    
    def get_totalDonated(self, obj):
        totals=[]
        totalDonations = CompanyDonation.objects.filter(company =obj)
        for donation in totalDonations:
            totals.append(donation.amount)
        final = sum(totals)
        return final
            

        
        
    
    def get_atrocityRelationships(self, obj):
        lis = []
        relationships = CompanyAtrocityRelationship.objects.filter(company =obj)
        for relationship in relationships:
            serialized =  CompanyAtrocityRelationShipSerializer(relationship).data
            lis.append(serialized)
        return lis
    
    def get_nonprofitRelationships(self, obj):
        lis = []
        relationships = CompanyNonProfitRelationship.objects.filter(company = obj)
        for relationship in relationships:
            serialized = CompanyNonProfitRelationshipSerializer(relationship).data
            lis.append(serialized)
        return lis
    
    def create(self, validated_data):
        profile = validated_data.pop('owner')
        return ForProfitCompany.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.mission = validated_data.get('mission', instance.mission)
        instance.description = validated_data.get('description', instance.description)
        instance.website_address = validated_data.get('website_address', instance.website_address)
        instance.facebook = validated_data.get('facebook', instance.facebook)
        instance.instagram = validated_data.get('instagram', instance.instagram)
    
    
# class CompanyMatchDonationSerializer(FlexFieldsModelSerializer):
    
    
#     class Meta:
#         model
#     company amount nonprofit atrocity user_matched donation_date

class NonProfitProjectSerializer(FlexFieldsModelSerializer):
    nonprofit = NonProfitSerializer
    cause = CategorySerializer
    atrocity = AtrocitySerializer()
    currentFunds = serializers.SerializerMethodField()
    
    class Meta:
        model = NonProfitProject
        fields = ['id','nonprofit', 'cause', 'atrocity','information','fundraising_goal', 'currentFunds']


    def create(self, validated_data):
        return NonProfitProject(**validated_data)
    
    def get_currentFunds(self, obj):
        total =[]
        donations = UserDonation.objects.filter(project = obj)
        for don in donations:
            total.append(don.amount)
        all= sum(total)
        return all