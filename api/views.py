from django.contrib.auth.decorators import permission_required
from django.db.models.query import Prefetch
from django.forms.models import model_to_dict
from django.conf import settings
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from Alt.models import Atrocity, Category, CompanyStore, ForProfitCompany, NonProfit, Order, Rating, Shirt
from api.models import Balance, Link, User, UserDonation, UserProfile
from rest_framework.response import Response
from rest_framework.decorators import action, authentication_classes, permission_classes
from .serializers import CompanyStoreSerializer, NonProfitListSerializer, OrderItemSerializer, ShirtListSerialzier, ShirtSerializer, NonProfitSerializer, AtrocitySerializer,  CategorySerializer, RatingSerializer, UserProfileSerializer
from api.serializers import ForProfitCompanySerializer, LinkSerializer, OrderSerializer, UserDonationSerializer, UserSerializer
from api.permissions import IsLoggedInUserOrAdmin, IsAdminUser
from django.shortcuts import get_object_or_404
from django.http.response import Http404
from django.http import HttpResponse
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
    ListBulkCreateUpdateDestroyAPIView,
)
from requests.api import request
from rest_flex_fields import is_expanded



class FlexFieldsMixin(object):
    permit_list_expands = []

    def get_serializer_context(self):
        default_context = super(FlexFieldsMixin, self).get_serializer_context()

        if hasattr(self, "action") and self.action == "list":
            default_context["permitted_expands"] = self.permit_list_expands

        return default_context


class FlexFieldsModelViewSet(FlexFieldsMixin, viewsets.ModelViewSet):
    pass



class UserProfileFinder(generics.RetrieveUpdateDestroyAPIView):
  serializer_class= UserProfileSerializer
  queryset= UserProfile.objects.all()




class UserProfileView(viewsets.ModelViewSet):
  queryset=UserProfile.objects.all()
  serializer_class = UserProfileSerializer
  authentication_classes = (TokenAuthentication, )

  @action(detail = True, methods=['post'])
  def addUserDonationToNonProfit(self, request, *args, **kwargs):
    userprofile = self.get_object()
    wallet = Balance.objects.get(account = userprofile)
    amount = request.data['amount']
    np = NonProfit.objects.get(slug = request.data['slug'])
    donation_type = request.data['donation_type']
    newDonation = UserDonation.create(user = userprofile, wallet=wallet, amount = amount, donation_type=donation_type, nonprofit= np )
    newDonation.save()
    response = {'message': 'You have donated ${amount} to help ${atrocity.title}'}
    return Response(response, status=status.HTTP_201_CREATED)


  @action(detail = True, methods =['post'])
  def addUserDonationToAtrocity(self, request, *args, **kwargs):
    userprofile = self.get_object()
    wallet = Balance.objects.get(account = userprofile)
    amount = request.data['amount']
    atrocity = Atrocity.objects.get(id = request.data['id'])
    donation_type = request.data['donation_type']
    newDonation = UserDonation.create(user = userprofile, wallet=wallet, amount = amount, donation_type=donation_type, atrocity =atrocity )
    newDonation.save()
    response = {'message': 'You have donated ${amount} to help ${atrocity.title}'}
    return Response(response, status=status.HTTP_201_CREATED)

  @action(detail=True, methods=['patch'])
  def manageUserFollowers(self, request, *args, **kwargs):
    profile = self.get_object()
    following_list = profile.following.all()
    profile_to_follow = UserProfile.objects.get(id = request.data['id'])
    if request.data['follow']:
      try:
        if profile_to_follow not in following_list:
          profile.following.add(profile_to_follow)
          profile.save()
          response = {'message': 'Now Following ${profile_to_follow.username}'}
          return Response(response, status=status.HTTP_200_OK )
        else:
          response = {'message': 'You are already Following This Profile'}
          return Response(response, status=status.HTTP_200_OK)
      except:
        response = {"message" :'Something Went Wrong'}
        return Response(response, status=status.HTTP_200_OK)
    elif request.data['unfollow']:
      try:
        if profile_to_follow in following_list:
          profile.following.remove(profile_to_follow)
          profile.save()
          response = {'message': 'You have unfollowed ${profile_to_follow.username}'}
          return Response(response, status=status.HTTP_200_OK)
        else:
          response = {'message': 'You are not Following This Profile'}
          return Response(response, status=status.HTTP_200_OK)
      except:
        response = {"message" :'Something Went Wrong'}
        return Response(response, status=status.HTTP_200_OK) 


        
    

  # @action(detail = True, methods =['patch'])
  # def add_profilePic(self, request, *args, **kwargs):
  #     userprofile = self.get_object()
  #     picture  = request.data['profile_picture']
  #     userprofile.profile_picture  = picture
  #     userprofile.save(update_fields=['profile_picture'])
  #     response = {'message': 'Profile Picture has been updated', 'result': 'success'}
  #     return Response(response, status=status.HTTP_200_OK)



  @action(detail= True, methods=['patch'])
  def add_shirt(self, request, *args, **kwargs,):
      userprofile = self.get_object()
      shirt_list= userprofile.shirt_list.all()
      shirt_instance = Shirt.objects.get(slug = request.data['slug'])
      try:
        if shirt_instance in shirt_list:
          print(shirt_instance)
          response = {'message': 'This Shirt Is already In Your List','result': 'hey'}
          return Response(response, status= status.HTTP_200_OK)
        else:
          print(shirt_instance)
          userprofile.shirt_list.add(shirt_instance)
          userprofile.save()
          response= {'message': 'Shirt_List Updated', 'result':'hey'}
          return Response(response, status= status.HTTP_200_OK)
      except:
        print(shirt_instance)
        response = {'message': "Something went wrong", 'result': 'hey'}
        return Response(response, status=status.HTTP_200_OK)
  
  @action(detail =True, methods=['patch'])
  def remove_shirt(self, request, *args, **kwarsgs):
    userprofile = self.get_object()
    
    try:
      shirt_instance = Shirt.objects.get(id =request.data['id'])
      userprofile.shirt_list.remove(shirt_instance)
      userprofile.save()
      response ={ 'message': 'Shirt List has been update', 'result':'hey'}
      return Response(response, status= status.HTTP_200_OK)
    except:
      response = {'message': "Something went wrong", 'result': 'hey'}
      return Response(response, status=status.HTTP_200_OK)

  @action(detail=True, methods=['patch'])
  def add_atrocity(self, request, *args, **kwargs):
    userprofile = self.get_object()
    atrocity_list = userprofile.atrocity_list.all()
    atrocity_instance = Atrocity.objects.get(id = request.data['id'])
    try:
      if atrocity_instance in atrocity_list:
        response ={ 'message': 'Atrocity List has been update', 'result':'hey'}
        return Response(response, status= status.HTTP_200_OK)
      else:
         
        userprofile.atrocity_list.add(atrocity_instance)
        userprofile.save()
        response = {'message': 'This Atrocity is already in your list', 'result': 'hey'}
        return Response(response, status= status.HTTP_200_OK)
    except:
      response = {'message': "Something went wrong", 'result': 'hey'}
      return Response(response, status=status.HTTP_200_OK)
  
  @action(detail = True, methods=['patch'])
  def remove_atrocity(self, request, *args, **kwargs):
    userprofile = self.get_object()
    atrocity_list = userprofile.atrocity_list.all()
    atrocity_instance = Atrocity.objects.get(id = request.data['id'])
    try:
      
      if atrocity_instance in atrocity_list:
        userprofile.atrocity_list.remove(atrocity_instance)
        userprofile.save()
        response ={ 'message': 'Atrocity List has been updated', 'result': 'hey'}
        return Response(response, status= status.HTTP_200_OK)
    except:
      response = {'message': "Something went wrong", 'result':'hey'}
      return Response(response, status=status.HTTP_200_OK)

  @action(detail = True, methods=['patch'])
  def add_nonprofit(self, request, *args, **kwargs):
    userprofile = self.get_object()
    nonprofit_list = userprofile.nonProfit_list.all()
    try:
      nonprofit_instance = NonProfit.objects.get(id = request.data['id'])
      if nonprofit_instance not in nonprofit_list:
        userprofile.nonProfit_list.add(nonprofit_instance)
        userprofile.save()
        response={ 'message': 'Nonprofit List has been update', 'result': 'hey'}
        return Response(response, status= status.HTTP_200_OK)
      else:
        response =  {'message': 'This NonProfit is already in your list', 'result': 'hey'}
        return Response(response, status= status.HTTP_200_OK)
    except:
      response = {'message': "Something went wrong", 'result': 'hey'}
      return Response(response, status=status.HTTP_200_OK)
      
  @action(detail = True, methods=['patch'])
  def remove_nonprofit(self, request, *args, **kwargs):
    userprofile= self.get_object()
    nonprofit_list = userprofile.nonProfit_list.all()
    try:
      nonprofit_instance = NonProfit.objects.get(id = request.data['id'])
      if nonprofit_instance in nonprofit_list:
        userprofile.nonProfit_list.remove(nonprofit_instance)
        userprofile.save()
        response={ 'message': 'Nonprofit List has been update', 'result': 'hey'}
        return Response(response, status= status.HTTP_200_OK)
    except:
      response = {'message': "Something went wrong", 'result': 'hey'}
      return Response(response, status=status.HTTP_200_OK)

  @action(detail=True, methods=['patch'])
  def add_company(self, request, *args, **kwargs):
    userprofile = self.get_object()
    company_list = userprofile.compannies.all()
    try:
      company_instance = ForProfitCompany.objects.get(id = request.data['id'])
      if company_instance not in company_list:
        userprofile.company.add(company_instance)
        userprofile.save()
        response = {'message': 'Company list has been updated', 'result': company_instance}
        return Response(response, status= status.HTTP_200_OK)
      else:
        response = {'message': 'This Company is already in your list', 'result': company_instance}
        return Response(response, status= status.HTTP_200_OK)
    except:
      response = {'message': "Something went wrong", 'result': 'hey'}
      return Response(response, status=status.HTTP_200_OK)
  

  @action(detail = True, methods=['patch'])
  def remove_company(self, request, *args, **kwargs):
    userprofile= self.get_object()
    company_list = userprofile.company.all()
    try:
      company_instnace = ForProfitCompany.objects.get(id = request.data['id'])
      if company_instnace in company_list:
        userprofile.company.remove(company_instnace)
        userprofile.save()
        response={ 'message': 'Nonprofit List has been update', 'result': 'hey'}
        return Response(response, status= status.HTTP_200_OK)
    except:
      response = {'message': "Something went wrong", 'result': 'hey'}
      return Response(response, status=status.HTTP_200_OK)

  @action(detail = True, methods=['get'])
  def followerNonProfitDonations(self, request, *args, **kwargs):
    userprofile = self.get_object()
    donation_list =[]
    following_list = userprofile.following.all()
    try:
      for follower in following_list:   
        nonprofit = NonProfit.objects.filter(id = request.data['id'])
        all_donations = UserDonation.objects.filter(user =follower, nonprofit = nonprofit)
        for donation in all_donations:
          serializer = UserDonationSerializer(donation)
          donation_list.append(serializer.data)  
      response = {'message':'donations', 'result':donation_list} 
      return Response(response, status = status.HTTP_200_OK)
      
    except:
      response = {'message': "Something went wrong", 'result': 'hey'}
      return Response(response, status=status.HTTP_200_OK)

    
  # response = {'message': 'Companies', 'result':serializer.data}
# class UpdaeteForProfitCompany(APIView):
#   permission_classes =(IsAuthenticated,)
#   def


    








class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsLoggedInUserOrAdmin]
        elif self.action == 'list' or self.action == 'destroy':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    

# class UserDetail(APIView):
#   permission_classes = (IsAuthenticated, )
  

class ForProfitCompanyAddLocation(APIView):
  permission_classes= (IsAuthenticated,)


  def get_object(self, pk):
    try: 
      return ForProfitCompany.objects.get(pk=pk)
    except ForProfitCompany.DoesNotExist:
      raise Http404
  def patch(self, request, pk, format=None):
    company = self.get_object(pk)
    if request.data['location']:
      location_serializer = CompanyStoreSerializer()
      serializer= ForProfitCompanySerializer(company, data = request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return HttpResponse(status=200)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
  

class FindUserList(APIView):
  permission_classes = (IsAuthenticated, )

  def get(self,request, format=None):
    users = UserProfile.objects.all()
    userlist = []
    for profile in users:
      representation = {'username': str(profile.username),
      'id': (profile.user.id)}
  
      userlist.append(representation)
    return Response(userlist)


class LinkList(viewsets.ModelViewSet):
  permission_classes= []
  serializer_class = LinkSerializer
  queryset = Link.objects.all()




class UserProfileDetail(APIView):
   permission_classes = (IsAuthenticated, )

   def get_object(self, pk):
    try:
      return UserProfile.objects.get(pk = pk)
    except UserProfile.DoesNotExist:
      raise Http404

    def get(self, request, pk, format=None):
      userprofile = self.get_object(pk)
      serializer = UserProfileSerializer(userprofile)
      return Response(serializer.data)

   def patch(self, request, pk, format=None):
      userprofile = self.get_object(pk)      
      serializer = UserProfileSerializer(userprofile, data=request.data, partial=True)
      if serializer.is_valid():
      

        
        
          
        serializer.save()
        return HttpResponse(status=200)
      return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


   def delete(self, request, pk, format=None):
       userprofile = self.get_object(pk)
       userprofile.delete()
       return Response(status = status.HTTP_204_NO_CONTENT)



# class UserFriendsDonationList(APIView):
#   permission_classes=(IsAuthenticated,)
#   def

class ShirtList(viewsets.ModelViewSet):
  

  serializer_class = ShirtSerializer
  queryset= Shirt.objects.all()

  @action(detail=True, methods=['POST'])
  def rate_shirt(self,request, pk=None):
    if 'stars' in request.data:
      shirt = Shirt.objects.get(id=pk)
      stars = request.data['stars']
      user = request.user
      


      try:
        rating = Rating.objects.get(user = user.id, shirt = shirt.id)
        rating.stars = stars
        rating.save()
        serializer = RatingSerializer(rating, many =False)
        response = {'message': 'Rating Updated', 'result':serializer.data}
        return Response(response, status=status.HTTP_200_OK)
      except:
        rating = Rating.objects.create(user =user, shirt= shirt)
        serializer =RatingSerializer(rating)
        response = {'message': 'Rating Created', 'result':serializer.data}
        return Response(response, status=status.HTTP_200_OK)
    else:
      response = {'messeage': 'You need to provide a rating'}
      return Response(response, status=status.HTTP_400_BAD_REQUEST)

  
class CompanyList(viewsets.ModelViewSet):
  permission_classes = (IsAuthenticated,  )
  
  serializer_class = ForProfitCompanySerializer
  queryset = ForProfitCompany.objects.all()

  @action(detail=True, methods=['patch'])
  def add_contributor(self, request, *args, **kwargs):
    company = self.get_object()
    pend_contr = company.pending_contributors.all()
    try:
      profile_instance = UserProfile.objects.get(user_id = request.data['user'])
      if profile_instance not in pend_contr:
        pend_contr.add(profile_instance)
        company.save()
        response = {"message": "You have invited {profile.username} to be a contributor"}
        return Response(response, status= status.HTTP_200_OK)
      elif profile_instance in pend_contr:
        response ={'message': 'You have already invited this user. Please wait for them to respond to your request'}
        return Response(response, status = status.HTTP_200_OK)
    except:
      response={"message":"Oops! Something went wrong, please try again"}
      return Response(response, status= status.HTTP_400_BAD_REQUEST )    


  @action(detail=True, methods=['patch'])
  def deletePendingContributor(self, request, *args, **kwargs):
    company= self.get_object()
    contributors = company.contributors.all()
    pending = company.pending_contributors.all()

  @action(detail=False, methods=['get'])
  def atrocity(self, request):
    companies = ForProfitCompany.objects.filter(categories__in=[1])
    serializer = ForProfitCompanySerializer(companies, many = True)
    response = {'message': 'Companies', 'result':serializer.data}
    return Response(serializer.data)


     
class NonProfitList(viewsets.ModelViewSet):
  permission_classes = []
  serializer_class = NonProfitSerializer
  queryset = NonProfit.objects.all()
  

class NPLists(generics.ListCreateAPIView):
  queryset= NonProfit.objects.all()
  serializer_class = NonProfitSerializer
  name  = 'nonprofit-list'
  filter_fields=(
    'category'
  )
  

class AtrocityList(viewsets.ModelViewSet):
  permission_classes = []
  serializer_class = AtrocitySerializer
  queryset= Atrocity.objects.all()

class CategoryList(viewsets.ModelViewSet):
  permission_classes = []
  serializer_class = CategorySerializer
  queryset= Category.objects.all()

class RatingViewSet(viewsets.ModelViewSet):
  queryset = Rating.objects.all()
  serializer_class = RatingSerializer
  authentication_classes = (TokenAuthentication, )
  



class PovertyShirts(generics.ListAPIView):
  permission_classes =[]
  serializer_class = ShirtSerializer

  def get_queryset(self):
    return Shirt.objects.filter(category_id= 3)

class RefugeeShirts(generics.ListAPIView):
  permission_classes=[]
  serializer_class = ShirtSerializer
  def get_queryset(self):
      return Shirt.objects.filter(category_id = 2)
  
class WorldHungerShirts(generics.ListAPIView):
  permission_classes = []
  serializer_class = ShirtSerializer
  def get_queryset(self):
    return Shirt.objects.filter(category_id =1)


class FeaturedShirts(generics.ListAPIView):
  permission_classes = []
  serializer_class = ShirtSerializer
  
  def get_queryset(self):
    return Shirt.objects.filter(featured = True)


class FeaturedAtrocities(generics.ListAPIView):
  permission_classes = []
  serializer_class = AtrocitySerializer
  
  def get_queryset(self):
    return Atrocity.objects.filter(featured = True)




class AllUserDonations(viewsets.ModelViewSet):
  queryset = UserDonation.objects.all().order_by('donation_date')
  serializer_class =UserDonationSerializer



class FeaturedNonProfits(generics.ListAPIView):
  permission_classes = []
  serializer_class = NonProfitSerializer
  
  def get_queryset(self):
    return NonProfit.objects.filter(featured = True)


class UserOrder(viewsets.ModelViewSet):
  permission_classes = (IsAuthenticated, )
  serializer_class= OrderSerializer
  queryset = Order.objects.all()

  @action(detail=True, methods = ["GET"])
  def get_cart(self, request, *args, **kwargs):
    user = request.user
    profile = UserProfile.objects.get(user = user)
    cart = Order.objects.filter(completed = False, user = profile).latest()
    return cart


  

# class GetCart(APIView):
#   permission_classes = [IsAuthenticated]
#   def get(self, request, format =None):
#     user = request.user
#     order_list = []
#     profile = UserProfile.objects.get(user = user)
#     open_cart = Order.objects.filter(completed =False, user = profile).latest
#     shirts = open_cart.shirts.all()
#     for shirt in shirts:
#       serialized = OrderItemSerializer(shirt).data
#       order_list.append(serialized)
#     response = {''} 
#     return order_list

  

class UserCompletedOrders(viewsets.ModelViewSet):
  permission_classes= [IsAuthenticated]
  serializer_class= OrderSerializer
  
  # user = request.user
  # profile = UserProfile.objects.get(user = user)
  
  # open_order = Order.objects.filter(completed=False, user= profile )
  

class AllUserCompletedOrders(generics.ListAPIView):
  permission_classes= [IsAuthenticated]
  serializer_class = OrderSerializer
  
  def get_queryset(self):
    user = self.request.user.profile
    return Order.objects.filter(user = user)



  

class UserFollowerDonations(APIView):
  permission_classes = [IsAuthenticated]
  serializer_class = UserProfileSerializer
  
  
  def get(self, request, format=None):
        profile = request.user
        friend_list =[]
        new_list =[]
        nonprofit = NonProfit.objects.get(id = request.data['id'])
        userprofile = UserProfile.objects.filter(user = profile)
        followers = userprofile.following.all()
        for follower in followers:
          donations = UserDonation.objects.filter(user = follower)
          for donation in donations:
            if donation.nonprofit is nonprofit:
              friend_list.append(follower)
          for friend in friend_list:
            serializer = UserProfileSerializer(friend_list, many =True)
        return Response(serializer.data)


  
  
  

  
   

  