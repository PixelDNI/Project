from django.forms import ModelForm
from django import forms
from adminMathTrainer.models import *


class CreateCourseForm(ModelForm):
    class Meta:
        model = MathCourse
        fields = ('title', 'course_image', 'description', 'course_content', 'course_length',)


class CreateModuleForm(ModelForm):
    class Meta:
        model = CourseModule
        exclude = ('math_course', 'is_passed', 'order')


class CreateLectureForm(ModelForm):
    class Meta:
        model = Lecture
        fields = ['title', 'lecture_image', 'description', 'paragraph']
        widgets = {
            'title': forms.TextInput(attrs={'required': 'required'}),
        }


class CreateCommonTestForm(ModelForm):
    class Meta:
        model = CommonTest
        exclude = ('lecture',)


class CreateChoiceTestForm(ModelForm):
    class Meta:
        model = ChoiceTest
        exclude = ('lecture',)



class CreateAnswerForm(ModelForm):
    class Meta:
        model = Answer
        exclude = ('choice_test',)


class UpdateProfile(ModelForm):
    class Meta:
        model = AuthorProfile
        exclude = ('author','reputation','subscribers', )


