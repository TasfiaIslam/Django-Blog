from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages

from django.views.generic import ( ListView, DetailView, CreateView, UpdateView, DeleteView )
from .models import Post, BlogComment
from .forms import CommentForm


# Create your views here.

def home(request):
     context = {'posts': Post.objects.all()}
     return render(request, 'blog/home.html', context)

class PostListView(ListView):
     model = Post
     template_name = 'blog/home.html' # <app>/<model>_<viewtype>.html
     context_object_name = 'posts'
     ordering = ['-date_posted']
     paginate_by = 5

class UserPostListView(ListView):
     model = Post
     template_name = 'blog/user_posts.html' # <app>/<model>_<viewtype>.html
     context_object_name = 'posts'
     paginate_by = 5

     def get_queryset(self):
          user = get_object_or_404(User, username=self.kwargs.get('username'))
          return Post.objects.filter(author=user).order_by('-date_posted')

class PostDetailView(DetailView):
     model = Post
     context_object_name = "posts"
     queryset = Post.objects.prefetch_related('blogcomment_set')

     def get_context_data(self, *args, **kwargs):
          context = super(PostDetailView, self).get_context_data(*args, **kwargs)

          data = get_object_or_404(Post, id=self.kwargs['pk'])
          total_likes = data.total_likes()

          liked = False
          if data.likes.filter(id=self.request.user.id).exists():
               liked = True

          context["total_likes"] = total_likes
          context["liked"] = liked
          return context


class PostCreateView(LoginRequiredMixin, CreateView):
     model = Post
     fields = ['title', 'content']

     def form_valid(self, form):
          form.instance.author = self.request.user
          return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
     model = Post
     fields = ['title', 'content']

     def form_valid(self, form):
          form.instance.author = self.request.user
          return super().form_valid(form)
     
     def test_func(self):
          post = self.get_object()
          if self.request.user == post.author:
               return True
          return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
     model = Post
     success_url = '/'

     def test_func(self):
          post = self.get_object()
          if self.request.user == post.author:
               return True
          return False

def postComment(request, pk):

     post = get_object_or_404(Post, pk=pk)
     if request.method == 'POST':
          form = CommentForm(request.POST)

          if form.is_valid():
               form = request.POST.get('comment')
               user = request.user
               post = Post.objects.get(id=pk)
               parentId = request.POST.get('parentId')
               if parentId == '':
                    form = BlogComment(comment=form, user=user, post=post)
                    form.save()
                    messages.success(request, f'Your comment has been posted successfully')
               else:
                    parent = BlogComment.objects.get(id=parentId)
                    form = BlogComment(comment=form, user=user, post=post, parent=parent)
                    form.save()
                    messages.success(request, f'Your reply has been posted successfully')
          
               return redirect('post-detail', pk=post.pk)
     else:
        form = CommentForm()

     return render(request, 'post-detail', {'form':form})

def LikeView(request, pk):
     post = Post.objects.get(id=pk)
     liked = False

     if post.likes.filter(id=request.user.id).exists():
         post.likes.remove(request.user)
         liked = False
     else:
          post.likes.add(request.user)
          liked = True

     return HttpResponseRedirect(reverse('post-detail', args=[str(pk)]))
 
def about(request):
     return render(request, 'blog/about.html', {'title':'About'})
