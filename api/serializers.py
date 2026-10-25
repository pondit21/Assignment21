from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    Category,
    Comment,
    ContactMessage,
    Education,
    Experience,
    Post,
    Profile,
    Project,
    Skill,
    Tag,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'full_name', 'headline', 'bio', 'email', 'phone', 'location',
            'avatar', 'resume', 'github_url', 'linkedin_url', 'website_url',
            'is_available_for_hire', 'created_at', 'updated_at'
        )


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id', 'owner', 'name', 'category', 'proficiency', 'is_featured', 'display_order')


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ('id', 'owner', 'company', 'role', 'location', 'start_date', 'end_date', 'is_current', 'description', 'display_order')


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ('id', 'owner', 'institution', 'degree', 'field_of_study', 'start_year', 'end_year', 'grade', 'description', 'display_order')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class ProjectSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Project
        fields = ('id', 'owner', 'title', 'slug', 'summary', 'description', 'cover_image', 'live_url', 'github_url', 'category', 'tags', 'tag_ids', 'is_featured', 'completed_date', 'display_order')

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        project = Project.objects.create(**validated_data)
        project.tags.set(tag_ids)
        return project

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        return instance


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'post', 'parent', 'name', 'email', 'content', 'is_approved', 'created_at')


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    tag_ids = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Post
        fields = (
            'id', 'author', 'title', 'slug', 'excerpt', 'content', 'cover_image',
            'category', 'category_id', 'tags', 'tag_ids', 'status', 'published_at',
            'views_count', 'likes_count', 'reading_time', 'is_featured', 'created_at', 'updated_at'
        )

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        category_id = validated_data.pop('category_id', None)
        post = Post.objects.create(**validated_data)
        if category_id:
            post.category_id = category_id
            post.save(update_fields=['category'])
        post.tags.set(tag_ids)
        return post

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        category_id = validated_data.pop('category_id', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if category_id is not None:
            instance.category_id = category_id
        instance.save()
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        return instance


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ('id', 'name', 'email', 'subject', 'message', 'is_read', 'created_at')
