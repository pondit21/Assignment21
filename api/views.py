import uuid

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Category,
    Comment,
    ContactMessage,
    Education,
    Experience,
    Post,
    PostLike,
    PostView,
    Profile,
    Project,
    Skill,
    Tag,
    Visitor,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    ContactMessageSerializer,
    EducationSerializer,
    ExperienceSerializer,
    PostSerializer,
    ProfileSerializer,
    ProjectSerializer,
    SkillSerializer,
    UserSerializer,
)


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if hasattr(obj, 'owner') and obj.owner_id == request.user.id:
            return True
        if hasattr(obj, 'author') and obj.author_id == request.user.id:
            return True
        if hasattr(obj, 'user') and obj.user_id == request.user.id:
            return True
        return False


def ensure_profile(user):
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={
            'full_name': user.get_full_name() or user.username,
            'headline': 'Full-stack developer',
            'bio': 'I build with Django REST and React.',
            'email': user.email or f'{user.username}@example.com',
            'location': 'Remote',
            'is_available_for_hire': True,
        },
    )
    return profile


@api_view(['POST'])
@permission_classes([AllowAny])
def auth_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'detail': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
    refresh = RefreshToken.for_user(user)
    ensure_profile(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': UserSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth_logout(request):
    return Response({'detail': 'Logged out successfully.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_me(request):
    profile = ensure_profile(request.user)
    return Response({
        'user': UserSerializer(request.user).data,
        'profile': ProfileSerializer(profile).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth_change_password(request):
    current = request.data.get('current_password')
    new = request.data.get('new_password')
    if not request.user.check_password(current):
        return Response({'detail': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(new or '') < 8:
        return Response({'detail': 'Password must be at least 8 characters.'}, status=status.HTTP_400_BAD_REQUEST)
    request.user.set_password(new)
    request.user.save()
    return Response({'detail': 'Password changed successfully.'})


@api_view(['GET', 'PATCH'])
@permission_classes([AllowAny])
def profile_detail(request):
    if request.method == 'GET':
        profile = Profile.objects.order_by('id').first()
        if not profile:
            user = User.objects.filter(username='admin').first() or User.objects.first()
            if user is None:
                return Response({'detail': 'No profile found.'}, status=status.HTTP_404_NOT_FOUND)
            profile = ensure_profile(user)
        return Response(ProfileSerializer(profile).data)

    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    profile = request.user.profile
    serializer = ProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def skills_list(request):
    if request.method == 'GET':
        return Response(SkillSerializer(Skill.objects.order_by('display_order', 'id'), many=True).data)
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = SkillSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def skill_detail(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if skill.owner_id != request.user.id and not request.user.is_staff:
        return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'PATCH':
        serializer = SkillSerializer(skill, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    skill.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def experiences_list(request):
    if request.method == 'GET':
        queryset = Experience.objects.order_by('display_order', 'start_date')
        return Response(ExperienceSerializer(queryset, many=True).data)
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = ExperienceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def experience_detail(request, pk):
    experience = get_object_or_404(Experience, pk=pk)
    if experience.owner_id != request.user.id and not request.user.is_staff:
        return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'PATCH':
        serializer = ExperienceSerializer(experience, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    experience.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def education_list(request):
    if request.method == 'GET':
        queryset = Education.objects.order_by('display_order', 'start_year')
        return Response(EducationSerializer(queryset, many=True).data)
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = EducationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def education_detail(request, pk):
    education = get_object_or_404(Education, pk=pk)
    if education.owner_id != request.user.id and not request.user.is_staff:
        return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'PATCH':
        serializer = EducationSerializer(education, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    education.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def categories_list(request):
    return Response(CategorySerializer(Category.objects.order_by('name'), many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def projects_list(request):
    queryset = Project.objects.order_by('-display_order', '-completed_date', '-created_at')
    category = request.query_params.get('category')
    search = request.query_params.get('search')
    if category:
        queryset = queryset.filter(category__icontains=category)
    if search:
        queryset = queryset.filter(Q(title__icontains=search) | Q(summary__icontains=search) | Q(description__icontains=search))
    return Response(ProjectSerializer(queryset, many=True).data)


@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([AllowAny])
def project_detail(request, slug=None):
    if request.method == 'GET':
        project = get_object_or_404(Project, slug=slug)
        return Response(ProjectSerializer(project).data)
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    project = Project.objects.filter(slug=slug).first()
    if project and project.owner_id != request.user.id and not request.user.is_staff:
        return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'POST':
        if project is not None:
            return Response({'detail': 'Project already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if project is None:
        return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProjectSerializer(project, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def posts_list(request):
    queryset = Post.objects.filter(status='PUBLISHED').order_by('-published_at', '-views_count')
    category = request.query_params.get('category')
    tag = request.query_params.get('tag')
    search = request.query_params.get('search')
    if category:
        queryset = queryset.filter(category__slug=category)
    if tag:
        queryset = queryset.filter(tags__slug=tag)
    if search:
        queryset = queryset.filter(Q(title__icontains=search) | Q(excerpt__icontains=search) | Q(content__icontains=search))
    queryset = queryset.distinct()
    return Response(PostSerializer(queryset, many=True).data)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'GET':
        visitor_id = request.META.get('HTTP_X_VISITOR_ID') or request.COOKIES.get('visitor_id')
        if not visitor_id:
            visitor_id = str(uuid.uuid4())
        visitor, _ = Visitor.objects.get_or_create(visitor_id=visitor_id)
        if not PostView.objects.filter(post=post, visitor=visitor).exists():
            PostView.objects.create(post=post, visitor=visitor)
            post.views_count += 1
            post.save(update_fields=['views_count'])
        return Response(PostSerializer(post).data)

    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
    if post.author_id != request.user.id and not request.user.is_staff:
        return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = PostSerializer(post, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def post_like(request, slug):
    post = get_object_or_404(Post, slug=slug)
    visitor_id = request.META.get('HTTP_X_VISITOR_ID') or request.COOKIES.get('visitor_id')
    if not visitor_id:
        visitor_id = str(uuid.uuid4())
    visitor, _ = Visitor.objects.get_or_create(visitor_id=visitor_id)
    like, created = PostLike.objects.get_or_create(post=post, visitor=visitor)
    if created:
        post.likes_count = PostLike.objects.filter(post=post).count()
        post.save(update_fields=['likes_count'])
    return Response({'liked': created, 'likes_count': post.likes_count})


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def comments_list(request):
    if request.method == 'GET':
        queryset = Comment.objects.filter(is_approved=True).order_by('-created_at')
        return Response(CommentSerializer(queryset, many=True).data)

    post_id = request.data.get('post')
    post = get_object_or_404(Post, pk=post_id)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def contact_create(request):
    serializer = ContactMessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contact_list(request):
    queryset = ContactMessage.objects.order_by('-created_at')
    return Response(ContactMessageSerializer(queryset, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    return Response({
        'total_posts': Post.objects.count(),
        'published_posts': Post.objects.filter(status='PUBLISHED').count(),
        'draft_posts': Post.objects.filter(status='DRAFT').count(),
        'total_projects': Project.objects.count(),
        'total_skills': Skill.objects.count(),
        'total_comments': Comment.objects.filter(is_approved=True).count(),
        'total_messages': ContactMessage.objects.count(),
    })
