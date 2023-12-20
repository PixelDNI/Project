from django.contrib import admin
from adminMathTrainer.models import *
from django.contrib.auth.admin import UserAdmin
# Register your models here.


admin.site.register(User)
admin.site.register(AuthorProfile)
admin.site.register(UserProfile)
admin.site.register(Archive)
admin.site.register(UserAnswer)
admin.site.register(ChoiceTest)
admin.site.register(Answer)
admin.site.register(CommonTest)
