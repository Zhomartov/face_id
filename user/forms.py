from django import forms
from .models import Student, Teacher, Group , UserAccounts
import face_recognition
import numpy as np


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

class UserForm(forms.ModelForm):
    image = forms.ImageField(label="Фото пользователя")

    class Meta:
        model = UserAccounts
        fields = ['image']

    def save(self, commit=True):
        image_file = self.cleaned_data['image']
        img = face_recognition.load_image_file(image_file)
        encodings = face_recognition.face_encodings(img)

        if not encodings:
            raise forms.ValidationError("Лицо не найдено на фото.")

        face_encoding = np.array(encodings[0], dtype=np.float64)
        self.instance.face_encode = face_encoding.tobytes()
        return super().save(commit=commit)
