from django import forms
from .models import Student, Teacher, Group

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['user','first_name', 'last_name', 'father_name', 'group', 'course']

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['user','first_name', 'last_name', 'father_name', 'major']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'teacher']
