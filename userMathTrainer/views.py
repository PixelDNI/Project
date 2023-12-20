from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from adminMathTrainer.models import *
from .forms import *
from django.core.paginator import Paginator, EmptyPage
from django.dispatch import receiver
from django.db.models.signals import post_save

import json


class MyPaginator(Paginator):
    def validate_number(self, number):
        try:
            return super().validate_number(number)
        except EmptyPage:
            if int(number) > 1:
                # return the last page
                return self.num_pages
            elif int(number) < 1:
                # return the first page
                return 1
            else:
                raise


def simplified_path(path: str):
    return f'userMathTrainer/{path}.html'


def StartPageView(request):
    user_auth = request.user.is_authenticated
    user = request.user if user_auth else None

    if user_auth and request.user.is_author:
        return redirect('content_creator_dashboard')
    if user is None:
        return redirect('courses')

    if request.user.is_authenticated:
        return redirect('my_education', pk=request.user.id)
    else:
        return redirect('catalog')

    context = {'user': user, 'user_auth': user_auth}
    return render(request, simplified_path('startPage'), context)


class ShowAllCourses(ListView):
    template_name = simplified_path('allCourses')
    model = MathCourse
    paginate_by = 6
    paginator_class = MyPaginator

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            user = self.request.user
            queryset = queryset.exclude(course_user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        page = self.request.GET.get('page', 1)
        courses = MathCourse.objects.all()
        user = self.request.user
        if user.is_authenticated:
            courses = courses.exclude(course_user=user)
        paginator = self.paginator_class(courses, self.paginate_by)
        courses = paginator.page(page)

        context['courses'] = courses

        return context


class AboutUsView(TemplateView):
    template_name = simplified_path('aboutUs')


class ContactsView(TemplateView):
    template_name = simplified_path('contacts')


# @receiver(post_save, sender=User)
# def create_author_profile(sender, instance, created, **kwargs):
#     if created and not hasattr(instance, 'profile'):
#         AuthorProfile.objects.create(author=instance)
class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signUp.html'
    success_url = '/login/'

    def form_valid(self, form):
        response = super().form_valid(form)

        user = form.save()

        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user=user)

        if not hasattr(user, 'archive'):
            Archive.objects.create(user=user)

        return response


from django.shortcuts import redirect

class NewUserProfileView(DetailView):
    template_name = simplified_path('profile')
    model = User
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = UserProfile.objects.filter(user=self.object).first()

        if profile:
            subscriber_count = profile.subscribers.count()
        else:
            subscriber_count = 0

        context['profile'] = profile
        form = UpdateUserProfile()

        context['subscriber_count'] = subscriber_count
        context['form'] = form

        return context

    def post(self, request, *args, **kwargs):
        form = UpdateUserProfile(request.POST, request.FILES)
        if form.is_valid():
            # Retrieve the user profile associated with the current user
            profile = UserProfile.objects.get(user=self.request.user)

            # Update the profile photo
            profile.profile_photo = form.cleaned_data['profile_photo']
            profile.save()

            # Redirect to the my_education page
            return redirect('my_education', pk=self.request.user.id)

        # If the form is not valid, re-render the profile template with the form
        return self.render_to_response(self.get_context_data(form=form))
@receiver(post_save, sender=User)
def create_author_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        AuthorProfile.objects.create(author=instance)


class AuthorSignUpView(CreateView):
    form_class = AuthorCreationForm
    template_name = 'registration/signUp.html'
    success_url = '/login/'

    def form_valid(self, form):
        form.instance.is_author = True

        response = super().form_valid(form)

        user = form.save()

        if not hasattr(user, 'profile'):
            AuthorProfile.objects.create(author=user)

        return response


class LectureDetailView(DetailView):
    template_name = simplified_path('lectureDetail')
    model = Lecture


class CourseDetail(DetailView):
    template_name = simplified_path('course_detail')
    model = MathCourse
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user
        modules = CourseModule.objects.filter(math_course=course)
        lectures = Lecture.objects.filter(course_module__in=modules)

        comments = Comment.objects.filter(course=course)

        is_favorite = False
        if user.is_authenticated:
            favorites = user.liked_courses.filter(pk=course.pk)
            if favorites.exists():
                is_favorite = True

        is_enrolled = False
        if user.is_authenticated:
            if course.course_user.filter(pk=user.pk).exists():
                is_enrolled = True

        context['modules'] = modules
        context['is_favorite'] = is_favorite
        context['lectures'] = lectures
        context['is_enrolled'] = is_enrolled

        context['form'] = CommentForm()
        context['comments'] = comments

        return context


def module_detail(request, pk):
    module = get_object_or_404(CourseModule, id=pk)
    context = {'lectures_list': Lecture.objects.filter(course_module=module)}

    return render(request, simplified_path('moduleDetail'), context)


class UserProfileView(DetailView):
    template_name = simplified_path('userProfile')
    model = User


@login_required
def GetCourse(request, pk):
    course = get_object_or_404(MathCourse, id=pk)
    course.course_user.add(request.user)
    return redirect('courses')


@login_required
def ToFavorites(request, pk):
    course = get_object_or_404(MathCourse, id=pk)
    course.user_favorites.add(request.user)
    return redirect('courses')


def remove_favorites(request, pk):
    course = get_object_or_404(MathCourse, id=pk)
    course.user_favorites.remove(request.user)
    return redirect('courses')


def create_course_with_modules_and_lectures(request):
    math_course = MathCourse.objects.create(
        title="Math Course 1",
        description="This is a math course.",
        author=1,
    )

    module1 = CourseModule.objects.create(
        title="Module 1",
        description="This is module 1 of the math course.",
        math_course=math_course,
    )

    module2 = CourseModule.objects.create(
        title="Module 2",
        description="This is module 2 of the math course.",
        math_course=math_course,
    )

    for module in [module1, module2]:
        for i in range(2):
            Lecture.objects.create(
                title=f"Lecture {i + 1} for {module.title}",
                description=f"This is small description of  lecture {i + 1} for {module.title}.",
                paragraph=f"This is paragraph {i + 1} for {module.title}. I am fairly new to django and creating a website that involves account creation. The standard form UserCreationForm is fairly ugly. My main issue with it is that it displays a list of information under the password field. It displays the code in html as follows:",
                course_module=module,
            )

    return redirect('start_page')


class UserCoursesView(ListView):
    template_name = simplified_path('myEducation')
    model = MathCourse

    def get_queryset(self):
        user_id = self.request.user.id
        courses = MathCourse.objects.filter(course_user=user_id)
        # archive_courses = Archive.objects.filter(user_id=user_id).values('course')
        # not_archive = courses.exclude(id__in=archive_courses)

        return courses

class UserFavoriteCoursesView(ListView):
    template_name = simplified_path('myEducation')
    model = MathCourse

    def get_queryset(self):
        user_id = self.request.user.id
        return MathCourse.objects.filter(user_favorites=user_id)


class MyEducationView(PermissionsMixin, ListView):
    template_name = simplified_path('userCourses')
    model = MathCourse

    def get_queryset(self):
        user_id = self.request.user.id
        courses = MathCourse.objects.filter(course_user=user_id)
        archive_courses = Archive.objects.filter(user_id=user_id).values('course')
        not_archive = courses.exclude(id__in=archive_courses)

        return not_archive




def search_course(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            searched = form.cleaned_data['searched']
            is_free = form.cleaned_data['is_free']
            courses = MathCourse.objects.filter(title__contains=searched)
            print(is_free)

            if is_free:
                print('como')
                courses = courses.filter(price=0)
                print(courses)

            return render(request, simplified_path('courseList'), {
                "form": form,
                "searched": searched,
                "courses": courses
            })
    else:
        form = SearchForm()

    return render(request, simplified_path('courseList'), {"form": form})


class ReadCourse(DetailView):
    template_name = simplified_path('purchasedCourseDetail')
    model = MathCourse
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user
        modules = CourseModule.objects.filter(math_course=course).order_by('order')
        first_module = modules.first()
        if first_module:
            first_lecture = Lecture.objects.filter(course_module=first_module).order_by('id').first()
            context['first_lecture'] = first_lecture

        lectures = Lecture.objects.filter(course_module__in=modules)

        is_favorite = False
        if user.is_authenticated:
            favorites = user.liked_courses.filter(pk=course.pk)
            if favorites.exists():
                is_favorite = True

        is_enrolled = False
        if user.is_authenticated:
            if course.course_user.filter(pk=user.pk).exists():
                is_enrolled = True

        context['is_favorite'] = is_favorite
        context['is_enrolled'] = is_enrolled
        context['modules'] = modules
        context['lectures'] = lectures
        return context


class ReadLecture(DetailView):
    template_name = simplified_path('readLecture')
    model = Lecture
    context_object_name = 'lecture'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lecture = self.object

        common_tests = CommonTest.objects.filter(lecture=lecture)
        choice_tests = ChoiceTest.objects.filter(lecture=lecture)
        choice_test_ids = choice_tests.values_list('id', flat=True)
        answers = Answer.objects.filter(choice_test__in=choice_test_ids)

        course_module = lecture.course_module

        lectures_in_module = Lecture.objects.filter(course_module=course_module)

        next_lecture = None
        found_current_lecture = False

        for l in lectures_in_module:
            if found_current_lecture:
                next_lecture = l
                break
            if l.id == lecture.id:
                found_current_lecture = True

        next_module = CourseModule.objects.filter(math_course=course_module.math_course,
                                                  id__gt=course_module.id).order_by('id').first()
        context['next_module'] = next_module

        context['common_tests'] = common_tests
        context['choice_tests'] = choice_tests
        context['answers'] = answers
        context['lectures_in_module'] = lectures_in_module
        context['next_lecture'] = next_lecture

        return context

    def post(self, request, *args, **kwargs):
        # Retrieve the lecture and tests
        lecture = self.get_object()
        common_tests = CommonTest.objects.filter(lecture=lecture)
        choice_tests = ChoiceTest.objects.filter(lecture=lecture)
        answers = Answer.objects.filter(choice_test__in=choice_tests)

        # Get the submitted answers from the request
        submitted_answers = {}
        for test in common_tests:
            answer_key = f"answer_{test.id}"
            submitted_answers[test.id] = request.POST.get(answer_key)

        for answer in answers:
            answer_key = f"choice_{answer.id}"
            submitted_answer = request.POST.get(answer_key)
            if submitted_answer:
                submitted_answers[answer.choice_test_id] = True
            else:
                submitted_answers[answer.choice_test_id] = False

        # Create or update UserAnswer object for the current user
        user = request.user
        user_answer, created = UserAnswer.objects.get_or_create(user=user)
        user_answer.answers = submitted_answers
        user_answer.save()

        # Redirect the user to the same lecture page
        return redirect('show_results',id=lecture.id,  pk=user_answer.id)


def show_results(request, id, pk):
    user_answer = get_object_or_404(UserAnswer, id=pk)
    lecture = get_object_or_404(Lecture, id=id)
    common_tests = CommonTest.objects.filter(lecture=lecture)
    choice_tests = ChoiceTest.objects.filter(lecture=lecture)

    results = []

    # Iterate over common tests
    for common_test in common_tests:
        result = {}
        result['question'] = common_test.question
        result['answers'] = [
            {'answer': common_test.answer, 'is_right': True}
        ]
        results.append(result)

    # Iterate over choice tests
    for choice_test in choice_tests:
        result = {}
        result['question'] = choice_test.question
        result['answers'] = [
            {'answer': answer.answer, 'is_right': answer.is_right}
            for answer in Answer.objects.filter(choice_test=choice_test)
        ]
        results.append(result)

    context = {
        'user_answer': user_answer,
        'question_answer': results,
        'lecture': id,
    }

    return render(request, simplified_path('results'), context)




def remove_from_favorites(request):
    course = get_object_or_404(MathCourse, user_favorites=request.user.id)
    course.user_favorites.remove()
    return redirect(reverse('my_education', args=[request.user.id]))


def check_test(request, pk):
    lecture = Lecture.objects.get(id=pk)
    common_tests = CommonTest.objects.filter(lecture=lecture)
    choice_tests = ChoiceTest.objects.filter(lecture=lecture)
    answers = Answer.objects.filter(choice_test__in=choice_tests)

    question_answers = []
    test_result = []

    if request.method == 'POST':
        submitted_answers = []

        # Retrieve answers for common_tests

        for test in common_tests:
            question_answers.append(test.answer)
            answer_key = f"answer_{test.id}"
            submitted_answers.append(request.POST.get(answer_key))

        for answer in answers:
            question_answers.append(answer.is_right)
            answer_key = f"choice_{answer.id}"
            submitted_answer = request.POST.get(answer_key)
            if submitted_answer:
                submitted_answers.append(True)
            else:
                submitted_answers.append(False)

        for i in range(len(submitted_answers)):
            if submitted_answers[i] == question_answers[i]:
                test_result.append(True)
            else:
                test_result.append(False)
        print(test_result)
        print(submitted_answers)
        print(question_answers)
        return redirect(reverse('read_lecture', args=[pk]))  # Replace 'results' with the appropriate URL name

    context = {
        'lecture': lecture,
        'common_tests': common_tests,
        'choice_tests': choice_tests,
        'answers': answers,
    }

    return render(request, 'your_template.html', context)


class UpdateProfile(UpdateView):
    template_name = simplified_path('updateProfile')
    model = User
    fields = ('username', 'email',)

    def get_success_url(self):
        return reverse('user_profile', kwargs={'pk': self.request.user.id})


class AuthorProfileView(DetailView):
    template_name = simplified_path('authorProfile')
    model = User
    context_object_name = 'author'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(AuthorProfile, author=self.object)
        context["profile"] = profile
        courses_count = MathCourse.objects.filter(author=self.object).count()
        subscribers = profile.subscribers.count()
        courses = MathCourse.objects.filter(author=self.object)
        is_subscribed = False
        if self.request.user.is_authenticated:
            user_subs = AuthorProfile.objects.filter(subscribers=self.request.user)
            if profile.id in user_subs.values_list('id', flat=True):
                is_subscribed = True
            else:
                is_subscribed = False

        reputation_users_count = User.objects.filter(reputation=profile).count()
        context['reputation'] = reputation_users_count
        context['courses_count'] = courses_count
        context['subscribers'] = subscribers
        context['courses'] = courses
        context['is_subscribed'] = is_subscribed

        return context


def subscribe_user(request, pk):
    profile = AuthorProfile.objects.get(id=pk)
    user = request.user
    profile.subscribers.add(user)
    profile.save()
    return HttpResponse("Successfully subscribed!")


def unsubscribe_user(request, pk):
    profile = AuthorProfile.objects.get(id=pk)
    user = request.user
    profile.subscribers.remove(user)
    profile.save()
    return HttpResponse("Successfully unsubscribed!")


class SubscriptionsList(ListView):
    template_name = simplified_path('subscriptions')
    model = AuthorProfile
    context_object_name = 'profile'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        authors_profiles = AuthorProfile.objects.filter(subscribers=user)

        context['profiles'] = authors_profiles
        return context


def add_comment(request, pk):
    course = get_object_or_404(MathCourse, pk=pk)
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'POST':
            text_field = request.POST.get('text_field')
            comment = Comment.objects.create(course=course, user=user, text_field=text_field)

            return redirect('user_course_detail', pk=pk)
    else:

        return redirect('user_course_detail', pk=pk)


def put_is_passed(request, pk, next_lecture):
    lecture = get_object_or_404(Lecture, id=pk)
    lecture.is_passed = True
    lecture.save()
    return redirect(reverse('read_lecture', args=[next_lecture]))


def next_module(request, pk):
    last_lecture = get_object_or_404(Lecture, pk=pk)
    course_module = last_lecture.course_module
    course = course_module.math_course

    next_module = CourseModule.objects.filter(math_course=course, order__gt=course_module.order).order_by(
        'order').first()

    if next_module:
        next_lecture = Lecture.objects.filter(course_module=next_module).order_by('order').first()
        if next_lecture:
            return redirect('read_lecture', pk=next_lecture.pk)
        else:
            return redirect('read_lecture', pk=pk)
    else:
        return redirect('read_lecture', pk=pk)


def in_archive(request, pk):
    user_id = request.user.id
    archive = get_object_or_404(Archive, user=user_id)

    lecture = get_object_or_404(Lecture, pk=pk)
    module = get_object_or_404(CourseModule, id=lecture.course_module.id)
    course = get_object_or_404(MathCourse, id=module.math_course.id)
    lecture.is_passed = True
    lecture.save()

    modules = CourseModule.objects.filter(math_course=course)
    lectures = Lecture.objects.filter(course_module__in=modules)

    # fully_iterated = True
    #
    # for lecture in lectures:
    #     if not lecture.is_passed:
    #         fully_iterated = False
    #         return redirect('my_education', pk=request.user.id)
    #
    # if fully_iterated:
    archive.course.add(course)
    archive.save()
    return redirect('my_education', pk=request.user.id)


class ShowArchiveView(ListView):
    template_name = simplified_path('archive')
    model = Archive

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        archive = get_object_or_404(Archive, user=user)
        archive_courses = archive.course.all()
        context['archive'] = archive
        context['courses'] = archive_courses

        return context


def put_rate(request, pk):
    ...


def remove_course(request, pk):
    user = request.user

    course = get_object_or_404(MathCourse, id=pk)
    course.course_user.remove(user)

    return redirect('my_education', pk=pk)

class ArchiveView(ListView):
    template_name = simplified_path('archive')
    model = Archive

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        archive = get_object_or_404(Archive, user=user.id)
        courses = archive.course.all()
        context['courses'] = courses
        return context

def test_answers(request, pk):
    ...

