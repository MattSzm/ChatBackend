from django.urls import path
from django.views.decorators.cache import cache_page

import user.views as userViews


app_name = 'user'

urlpatterns = [
    path('search/<str:phrase>/', userViews.UserListSearch.as_view(),
         name='user-search-results'),
    path('friends/', userViews.Friends.as_view(),
         name='friends'),
    path('invitations/', userViews.Invitations.as_view(),
         name='invitations'),
    path('currentuser/', userViews.CurrentUser.as_view(),
         name='fetch-current-user'),
    path('<uuid:uuid>/', cache_page(60)(userViews.UserDetail.as_view()),
         name='user-detail'),

]
