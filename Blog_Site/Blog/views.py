from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

from .models import Comment, Post, Like, Category
from .forms import PostForm, CommentForm, CategoryForm, RegisterUserForm

from taggit.models import Tag

# Public Blog View
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):

        queryset = Post.objects.filter(status = 'published')

        category_slug = self.request.GET.get('category')
        if (category_slug):
            category = get_object_or_404(Category, slug = category_slug)
            queryset = queryset.filter(categories = category)
    

        query = self.request.GET.get('q')

        if (query):
            queryset = queryset.filter(
                Q(title__icontains = query) |
                Q(content__icontains = query)
            ).distinct()

        return queryset
    
    def get_context_data(self, **kwargs):
        content = super().get_context_data(**kwargs)
        content['search_query'] = self.request.GET.get('q', '')
        content['selected_category'] = self.request.GET.get('category', '')

        return content
    

def post_detail(request, slug):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, slug=slug)
    else:
        post = get_object_or_404(Post, slug=slug, status='published')

    comments = post.comments.all()
    categories = [post.category] if post.category else []

    comment_form = CommentForm()

    like_count = post.likes.count()
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = post.likes.filter(user=request.user).exists()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'like_count': like_count,
        'categories' : categories,  
        'user_has_liked': user_has_liked,
    }

    return render(request, 'blog/post_detail.html', context)
    
def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug = category_slug)
    posts = Post.objects.filter(status = 'published', category = category)

    paginator = Paginator(posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request ,'blog/category_posts.html',{
        'category':category,
        'posts' : page_obj,
        'page_obj' : page_obj
    })

def tagged_posts(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)

    posts = Post.objects.filter(status='published', tags__in=[tag]).distinct()

    paginator = Paginator(posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/tagged_posts.html', {
        'tag': tag,
        'posts': page_obj,
        'page_obj': page_obj
    })

class CategoryListView(ListView):
    model = Category
    template_name = "blog/category_list.html"
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.annotate(
            post_count = Count('posts', filter=Q(posts__status = 'published'))
        ).order_by('name')

@login_required
def create_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.author = request.user
            category.save()
            messages.add_message(request, messages.SUCCESS, f'Category "{category.name}" created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'blog/category_form.html', {'form': form})

@login_required
def update_category(request, id):
    category = get_object_or_404(Category, id = id)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'blog/category_form.html', {'form': form, 'title': 'Update Category'})

@login_required
def delete_category(request, id):
    category = get_object_or_404(Category, id = id)
    if request.method == "POST":
        category.delete()
        messages.success(request, f'Category "{category.name}" deleted successfully!')
        return redirect('category_list')
    
    return render(request, 'blog/category_confirm_delete.html', {'category': category})


@login_required
def dashboard(request):
    user_own_posts = Post.objects.filter(author=request.user).order_by('-created_at')

    total_posts = user_own_posts.count()
    published_count = user_own_posts.filter(status='published').count()
    draft_count = user_own_posts.filter(status='draft').count()

    distinct_categories_count = user_own_posts.values('category').distinct().count()

    paginator = Paginator(user_own_posts, 4)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'total_posts': total_posts,
        'published_count': published_count,
        'draft_count': draft_count,
        'distinct_categories_count': distinct_categories_count,
        'page_obj': page_obj,
    }

    return render(request, 'dashboard/dashboard.html', context)

@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save() 
            messages.success(request, "Post created successfully")
            return redirect('post_list')
    else:
        form = PostForm()

    return render(request, "blog/post_form.html", {"form": form})

    
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, "Post updated successfully")
        return super().form_valid(form)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = '/dashboard/'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post deleted successfully')
        return super().delete(request, *args, **kwargs)
    


@login_required
def add_comment(request, slug):
    post = get_object_or_404(Post, slug = slug)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully')
            return redirect('post_detail', slug = post.slug)
    else:
        form = CommentForm()
    return redirect('post_detail', slug=post.slug)

@login_required
def like_post(request, slug):
    post = get_object_or_404(Post, slug = slug)

    like, created = Like.objects.get_or_create(
        post = post,
        user = request.user
    )

    if not created:
        like.delete()
        messages.info(request, 'Post unlike')
    else:
        messages.success(request, 'Post liked')
    
    return redirect('post_detail', slug = post.slug)




# user 

def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f' User created successfully')
            return redirect('post_list')
    else:
        form = RegisterUserForm()
    
    return render(request, 'user/register.html', {'form': form, 'button_text': "Register", 'title': "Create Your account" })

def user_login(request):
    if request.method =="POST":
        form = AuthenticationForm(request, data = request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('post_list')
    else:
        form = AuthenticationForm()
    
    return render(request, 'user/register.html', {'form': form, 'button_text': "Login", 'title': "Login your account" })

def user_logout(request):
    logout(request)              
    return redirect('user_login')