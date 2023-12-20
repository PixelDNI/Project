from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import *
from django.core.paginator import Paginator
from contentCreator.forms import *
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin


def simplified_path(path: str):
    return f'contentCreator/{path}.html'


# Create your views here.
class StartPageView(ListView):
    template_name = simplified_path('startPage')
    model = MathCourse
    context_object_name = 'courses_list'

    def get_queryset(self):
        user_id = self.request.user.id
        return MathCourse.objects.filter(author=user_id)


def CreateNewCourseView(request):
    if request.method == 'POST':
        print('AAAAA')
        form = CreateCourseForm(request.POST, request.FILES)
        if form.is_valid():
            print('BBBBB')
            course = form.save(commit=False)
            course.author = request.user
            print(course)
            course.save()
            return redirect('add_module', course.id)
        else:
            print(form.errors)
    else:
        form = CreateCourseForm()

    return render(request, simplified_path('createCoursePage'), {'form': form})


def CreateModuleView(request, pk):
    if request.method == 'POST':
        form = CreateModuleForm(request.POST, request.FILES)
        if form.is_valid():
            module = form.save(commit=False)
            math_course = get_object_or_404(MathCourse, id=pk)
            module.math_course = math_course

            all_modules = CourseModule.objects.filter(math_course=math_course).count()

            module.order = all_modules + 1

            module.save()
            print(module.order)

            return redirect('add_lecture', id=pk, pk=module.id)

    else:
        form = CreateModuleForm()

    return render(request, simplified_path('createModulePage'), {'form': form})


class UpdateModuleView(UpdateView):
    template_name = simplified_path('updateModule')
    model = CourseModule
    fields = ('title', 'module_image', 'description',)

    def get_success_url(self):
        course_id = self.kwargs['id']
        return reverse('course_detail', args=[course_id])


class DeleteModuleView(DeleteView):
    template_name = simplified_path('deleteModule')
    model = CourseModule
    success_url = reverse_lazy('content_creator_dashboard')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Delete all lectures associated with the CourseModule
        Lecture.objects.filter(course_module=self.object).delete()

        success_url = self.get_success_url()
        self.object.delete()

        return HttpResponseRedirect(success_url)


def AddLectureView(request, pk, id):
    if request.method == 'POST':
        form = CreateLectureForm(request.POST, request.FILES)
        if form.is_valid():
            lecture = form.save(commit=False)
            module = get_object_or_404(CourseModule, id=pk)
            lecture.course_module = module

            all_lectures = Lecture.objects.filter(course_module=module).count()

            lecture.order = all_lectures + 1

            lecture.save()
            print(lecture.order)
            return redirect('course_detail', pk=id)

    else:
        form = CreateLectureForm()

    return render(request, simplified_path('addLecture'), {'form': form})


def AddCommonTestView(request, pk):
    if request.method == 'POST':
        form = CreateCommonTestForm(request.POST, request.FILES)

        if form.is_valid():
            test = form.save(commit=False)
            lecture = get_object_or_404(Lecture, id=pk)
            test.lecture = lecture
            test.save()
            return redirect(reverse('lecture_detail', args=[lecture.id]))
        else:
            print(form.errors)

    else:
        form = CreateCommonTestForm(request.POST, request.FILES)
    return render(request, simplified_path('addCommonTest'), {'form': form})


def AddChoiceTestView(request, pk):
    if request.method == 'POST':
        form = CreateChoiceTestForm(request.POST, request.FILES)

        if form.is_valid():
            test = form.save(commit=False)
            lecture = get_object_or_404(Lecture, id=pk)
            test.lecture = lecture
            test.save()
            return redirect(reverse('add_answer', args=[test.id]))

    else:
        form = CreateChoiceTestForm(request.POST, request.FILES)
    return render(request, simplified_path('addChoiceTest'), {'form': form})


class ChoiceTestDetail(UpdateView):
    template_name = simplified_path("choiceTestDetail")
    model = ChoiceTest
    form_class = CreateChoiceTestForm
    context_object_name = 'choice_test'
    success_url = reverse_lazy('content_creator_dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        answers = Answer.objects.filter(choice_test=self.object)
        context['answers'] = answers
        return context

    # def get_success_url(self):
    #     lecture_id = self.kwargs['pk']
    #
    #     return reverse('lecture_detail', args=[lecture_id])



def AddAnswerView(request, pk):
    if request.method == 'POST':
        form = CreateAnswerForm(request.POST)

        if form.is_valid():
            answer = form.save(commit=False)
            choice_test = get_object_or_404(ChoiceTest, id=pk)
            answer.choice_test = choice_test
            answer.save()
            return redirect(reverse('choice_test_detail', args=[choice_test.id]))

    else:
        form = CreateAnswerForm(request.POST, request.FILES)
    return render(request, simplified_path('addAnswer'), {'form': form})


class LectureDetailView(DetailView):
    template_name = simplified_path('lectureDetail')
    model = Lecture
    context_object_name = 'lecture'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tests = CommonTest.objects.filter(lecture=self.object)
        choice_tests = ChoiceTest.objects.filter(lecture=self.object)
        answers = Answer.objects.filter(choice_test__in=choice_tests)
        context['tests'] = tests
        context['choice_tests'] = choice_tests
        context['answers'] = answers
        return context


class AllAuthorCoursesView(ListView):
    template_name = simplified_path('allAuthorCourses')
    model = MathCourse

    def get_queryset(self):
        user_id = self.request.user.id
        return MathCourse.objects.filter(author=user_id)


class AuthorDetailCourseView(DetailView):
    template_name = simplified_path('authorCourseDetail')
    model = MathCourse
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object

        modules = CourseModule.objects.filter(math_course=course)
        lectures = Lecture.objects.filter(course_module__in=modules)

        context['modules'] = modules
        context['lectures'] = lectures
        return context


class ModuleDetailView(DetailView):
    template_name = simplified_path('moduleDetail')
    model = CourseModule
    context_object_name = 'module'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module = self.object

        lectures = Lecture.objects.filter(course_module=module)

        context['lectures'] = lectures
        return context


class DeleteCourseView(DeleteView):
    template_name = simplified_path('deleteCourse')
    model = MathCourse
    success_url = reverse_lazy('content_creator_dashboard')


class UpdateCourseView(UpdateView):
    template_name = simplified_path('updateCourse')
    model = MathCourse
    fields = ('title', 'course_image', 'description', 'price',)

    def get_success_url(self):
        return reverse_lazy('content_creator_dashboard')


#
# def createTestView(request, pk):
#     if request.method == "POST":
#         form = CreateLectureForm(request.POST, request.FILES)
#         if form.is_valid():
#             test = form.save(commit=False)
#             test.lecture = pk
#             test.save()
#
#             return redirect('content_creator_dashboard')
#     else:
#         form = CreateLectureForm
#     return render(request, simplified_path('createLecturePage'), {'form': form})


def delete_answer(request, pk):
    answer = get_object_or_404(Answer, id=pk)
    answer.delete()
    return HttpResponse(status=204)


class UpdateAnswerView(UpdateView):
    template_name = simplified_path('addAnswer')
    model = Answer
    fields = ('answer', 'is_right',)
    success_url = reverse_lazy('content_creator_dashboard')


class UpdateLectureView(UpdateView):
    template_name = simplified_path('updateLecture')
    model = Lecture
    fields = ('title', 'lecture_image', 'description', 'paragraph',)

    def get_success_url(self):
        lecture_id = self.kwargs['pk']
        return reverse('lecture_detail', args=[lecture_id])


def delete_lecture(request, pk):
    lecture = get_object_or_404(Lecture, id=pk)
    lecture.delete()
    author = request.user.id

    return redirect(reverse('all_author_courses', args=[author]))


# class UpdateModuleView()
class Profile(UpdateView):
    template_name = simplified_path('profile')
    model = AuthorProfile
    form_class = UpdateProfile
    success_url = reverse_lazy('content_creator_dashboard')

    def get_object(self, queryset=None):
        author_id = self.kwargs.get('pk')

        author_profile = get_object_or_404(AuthorProfile, author_id=author_id)

        return author_profile


def Deletequestion(request, pk, id):
    test = get_object_or_404(CommonTest, pk=pk)
    test.delete()
    return redirect('lecture_detail', pk=id)


def ChoiceDeletequestion(request, pk, id):
    test = get_object_or_404(ChoiceTest, pk=pk)
    test.delete()
    return redirect('lecture_detail', pk=id)
