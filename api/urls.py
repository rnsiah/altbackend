from django.conf.urls import include
from rest_framework import routers
from api.views import AllUserCompletedOrders, AllUserDonations, AtrocityList, CategoryList, CompanyList, FeaturedShirts, NPLists, NonProfitList, RatingViewSet, RefugeeShirts, ShirtList, UserCompletedOrders, UserProfileView, UserViewSet, LinkList, UserOrder
from django.urls import path, re_path
from . import views



router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register('ratings', RatingViewSet)
router.register('shirts', ShirtList )
router.register('nonprofits', NonProfitList)
router.register('userprofile', UserProfileView)
router.register('atrocities', AtrocityList)
router.register('order',UserOrder)
# router.register('completedorders', UserCompletedOrders)
router.register('categories', CategoryList)
router.register('companies', CompanyList)
router.register('userdonations',AllUserDonations)
router.register('infolinks',LinkList)





urlpatterns = [
    re_path(r'^', include(router.urls)),
    # path('usernonprofits/<int:pk>/', views.UserNonProfitsView.as_view()),
    # path('userprofiles/<int:pk>/', views.UserProfileDetail.as_view()),
    path('profilepage/<int:pk>', views.UserProfileDetail.as_view()),
    path('refugeesshirts', views.RefugeeShirts.as_view()),
    path('worldpovertyshirts', views.PovertyShirts.as_view()),
    path('worldhungershirts', views.WorldHungerShirts.as_view()),
    path('featuredshirts', views.FeaturedShirts.as_view()),
    path('featuredatrocities', views.FeaturedAtrocities.as_view()),
    path('featurednonprofits', views.FeaturedNonProfits.as_view()),
    path('allusercompletedorders', views.AllUserCompletedOrders.as_view()),
    path('findusers', views.FindUserList.as_view()),
    path('followingDonations/<int:id>', views.UserFollowerDonations.as_view()),
    path('nonprofs/', views.NPLists.as_view())
    # path('cart', views.GetCart.as_view()),
 

   

    
    
]