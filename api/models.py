from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=120)
    headline = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    resume = models.FileField(upload_to='resume/', blank=True, null=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    is_available_for_hire = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name or self.user.username


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('FRONTEND', 'Frontend'),
        ('BACKEND', 'Backend'),
        ('DATABASE', 'Database'),
        ('TOOLS', 'Tools'),
        ('SOFT_SKILL', 'Soft Skill'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills', null=True, blank=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='FRONTEND')
    proficiency = models.PositiveSmallIntegerField(default=80, validators=[MinValueValidator(1), MaxValueValidator(100)])
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Experience(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experiences', null=True, blank=True)
    company = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    location = models.CharField(max_length=120, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.role} @ {self.company}'


class Education(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='education', null=True, blank=True)
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True)
    start_year = models.PositiveIntegerField(blank=True, null=True)
    end_year = models.PositiveIntegerField(blank=True, null=True)
    grade = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.degree} @ {self.institution}'


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects', null=True, blank=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.TextField(blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='projects/', blank=True, null=True)
    live_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    category = models.CharField(max_length=100, default='General')
    tags = models.ManyToManyField(Tag, blank=True)
    is_featured = models.BooleanField(default=False)
    completed_date = models.DateField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
    ]
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    cover_image = models.ImageField(upload_to='posts/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    published_at = models.DateTimeField(blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=5)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Visitor(models.Model):
    visitor_id = models.CharField(max_length=80, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.visitor_id


class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'visitor')


class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views')
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='post_views')
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    name = models.CharField(max_length=120)
    email = models.EmailField()
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} on {self.post.title}'


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}: {self.subject}'
