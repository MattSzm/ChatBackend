from django.urls import path
import user.views as userViews


app_name = 'user'

urlpatterns = [
    path('search/<str:phrase>/', userViews.UserListSearch.as_view(),
         name='user-search-results'),
    path('friends/', userViews.Friends.as_view(),
         name='friends'),
    path('invitations/', userViews.Invitations.as_view(),
         name='invitations'),
    path('<uuid:uuid>/', userViews.UserDetail.as_view(),
         name='user-detail'),


]
