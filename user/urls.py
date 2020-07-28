from django.urls import path
import user.views as userViews


app_name = 'user'

urlpatterns = [
    path('<uuid:uuid>/', userViews.UserDetail.as_view(),
         name='user-detail'),

]
