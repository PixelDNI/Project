from django.db import models

from django.contrib.auth.models import Group, Permission

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
from ckeditor.fields import RichTextField


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):

        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):

        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_author = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    groups = models.ManyToManyField(Group, related_name='custom_user', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user', blank=True)

    def __str__(self):
        return str(self.email)

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def is_content_creator(self):
        if self.is_author:
            return True
        return False


class MathCourse(models.Model):
    title = models.CharField(max_length=255, blank=True)
    course_image = models.ImageField(null=True, upload_to='mathCourseImg/')
    description = RichTextField()
    course_content = RichTextField(default='')
    price = models.IntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    course_user = models.ManyToManyField(User, related_name='enrolled_courses')
    user_favorites = models.ManyToManyField(User, related_name='liked_courses')
    course_length = models.IntegerField()
    course_discount = models.IntegerField(validators=[
        MaxValueValidator(100),
        MinValueValidator(1)
    ], default=0)
    is_passed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.title)


class CourseModule(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    math_course = models.ForeignKey(MathCourse, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    is_passed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Lecture(models.Model):
    title = models.CharField(max_length=550, null=True)
    lecture_image = models.ImageField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    paragraph = RichTextField()
    course_module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, blank=True)
    is_passed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title


class CommonTest(models.Model):
    question = RichTextField(null=True, blank=True)
    image = models.ImageField(null=True, upload_to='questionImg/', blank=True)
    answer = models.CharField(max_length=550)
    explanation = RichTextField(null=True, blank=True)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)

    def __str__(self):
        return self.question


class ChoiceTest(models.Model):
    question = RichTextField(null=True, blank=True)
    image = models.ImageField(null=True, upload_to='questionImg/', blank=True)
    explanation = models.TextField(null=True, blank=True)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)

    def __str__(self):
        return self.question


class Answer(models.Model):
    answer = RichTextField()
    is_right = models.BooleanField()
    choice_test = models.ForeignKey(ChoiceTest, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.answer


class CourseRate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course = models.OneToOneField(MathCourse, on_delete=models.CASCADE)
    rate = models.IntegerField(
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0),
        ]
    )


class AuthorProfile(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    author_profile_image = models.ImageField(upload_to='authorProfileImg/', null=True, blank=True)
    description_image = models.ImageField(upload_to='descriptionImg/', null=True, blank=True)
    description = RichTextField(null=True, blank=True)
    reputation = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reputation', null=True, blank=True)
    subscribers = models.ManyToManyField(User, related_name='subscribed_profiles', null=True, blank=True)

    def __str__(self):
        return f'{self.author}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    profile_photo = models.ImageField(upload_to='userProfileImg/', null=True, blank=True)
    subscribers = models.ManyToManyField(User, related_name='subscribers', default=0)

    def __str__(self):
        return f"{self.user}"


class Comment(models.Model):
    course = models.ForeignKey(MathCourse, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_date = models.DateField(auto_now=True)
    text_field = models.TextField()

    def __str__(self):
        return self.user


class Archive(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course = models.ManyToManyField(MathCourse, blank=True)

    def __str__(self):
        return str(self.user)


class UserAnswer(models.Model):
    answers = models.CharField(max_length=1000, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.answers
