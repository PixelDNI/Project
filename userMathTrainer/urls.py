from django.urls import path
from userMathTrainer.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', StartPageView, name='start_page'),
    path('court_us/', AboutUsView.as_view(), name='about_us'),
    path('course_detail/<int:pk>/', CourseDetail.as_view(), name='user_course_detail'),
    path('about_us/', ContactsView.as_view(), name='contacts'),
    path('all_courses/', ShowAllCourses.as_view(), name='courses'),
    path('lecture_detail/<int:pk>/', LectureDetailView.as_view(), name='lecture_detail'),
    path('module_detail/<int:pk>/', module_detail, name='module_detail'),
    path('add_data/', create_course_with_modules_and_lectures, name='add'),
    path('sign_up/', SignUpView.as_view(), name='sign_up'),
    path('profile/<int:pk>/', NewUserProfileView.as_view(), name='user_profile'),
    path('show_my_courses/<int:pk>/', UserCoursesView.as_view(), name='user_courses'),
    path('get_course/<int:pk>/', GetCourse, name='get_course'),
    path('my_education/<int:pk>/', UserCoursesView.as_view(), name='my_education'), 
    path('to_favorites/<int:pk>/', ToFavorites, name='to_favorites'),
    path('remove_favorites/<int:pk>/', remove_favorites, name='remove_favorites'),
    path('favorite_courses/<int:pk>/', UserFavoriteCoursesView.as_view(), name='favorite_courses'),
    path('author_sign_up', AuthorSignUpView.as_view(), name='author_sign_up'),
    path('search_course/', search_course, name='search_course'),
    path('purchased_course_detail/<int:pk>/', ReadCourse.as_view(), name='read_course'),
    path('readLecture/<int:pk>/', ReadLecture.as_view(), name='read_lecture'),
    path('remove_from_favorites/', remove_from_favorites, name='remove_from_favorites'),
    # path('check_test/<int:pk>/', check_test, name='check_test'),
    path('next_lecture/<int:pk>/<int:next_lecture>/', put_is_passed, name='next_lecture'),
    path('update_profile/<int:pk>/', UpdateProfile.as_view(), name='update_profile'),
    path('author_profile/<int:pk>/', AuthorProfileView.as_view(), name='author_profile'),
    path('subscribe/<int:pk>/', subscribe_user, name='subscribe'),
    path('unsubscribe/<int:pk>/', unsubscribe_user, name='unsubscribe'),
    path('subscriptions/<int:pk>/', SubscriptionsList.as_view(), name='subscriptions'),
    path('add_comment/<int:pk>/', add_comment, name='add_comment'),
    path('next_module/<int:pk>/', next_module, name='next_module'),
    path('in_archive/<int:pk>/', in_archive, name='in_archive'),
    path('remove/course/<int:pk>/', remove_course, name='remove_course'),
    # path('finish_course/<int:pk>/', in_archive, name='finish_course')
    path('archive/<int:pk>/', ArchiveView.as_view(), name='archive'),
    path('archive/<int:id>/<int:pk>/', show_results, name='show_results'),


]
