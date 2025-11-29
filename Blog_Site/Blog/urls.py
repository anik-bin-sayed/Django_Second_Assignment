from django.urls import path
from . import views
from .views import (
    PostListView, PostDeleteView, 
    PostUpdateView, post_detail, CategoryListView,
)

urlpatterns = [
    

    #dashboard 
    path('dashboard/', views.dashboard, name='dashboard'),
    
    #CRUD
    path('post/new/', views.create_post, name='post_create'),
    path('post/<slug:slug>/update/', PostUpdateView.as_view(), name='post_update'),
    path('post/<slug:slug>/delete/', PostDeleteView.as_view(), name='post_delete'),
    
    # category
    path('category/new/', views.create_category, name= 'create_category'),
    path('category/<int:id>/delete/', views.delete_category, name='delete_category'),
    path('category/<int:id>/update/', views.update_category, name='update_category'),


    # interaction
    path('post/<slug:slug>/comment/', views.add_comment, name = 'add_comment'),
    path('post/<slug:slug>/like/', views.like_post,name='like_post'),

    # public urls
    path('', PostListView.as_view(), name = 'post_list'),
    path('post/<slug:slug>/', post_detail, name = 'post_detail'),
    path('category/<slug:category_slug>/', views.category_posts, name='category_posts'),
    path('categories', CategoryListView.as_view(), name='category_list'),
    path('tag/<slug:tag_slug>/', views.tagged_posts, name='tagged_posts'),

    # user related
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name = 'user_logout'),

]
