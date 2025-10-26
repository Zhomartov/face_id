import uuid
from django.db import models

class UserAccounts(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Храним бинарно 128-мерный float64 вектор
    face_encode = models.BinaryField()

    def __str__(self):
        return str(self.uuid)

class Teacher(models.Model):
    user = models.ForeignKey(UserAccounts, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=50, blank=True, null=True)
    major = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


# --- Группы студентов ---
class Group(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="groups")

    def __str__(self):
        return self.name


# --- Студенты ---
class Student(models.Model):
    COURSE_CHOICES = [
        ('1', 'Первый курс'),
        ('2', 'Второй курс'),
        ('3', 'Третий курс'),
        ('4', 'Четвертый курс'),
    ]

    user = models.ForeignKey(UserAccounts, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=50, blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.CharField(max_length=1, choices=COURSE_CHOICES, default='1')

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


# --- Предметы ---
class Subject(models.Model):
    name = models.CharField(max_length=255)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# --- Расписание ---
class Schedule(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()

    def __str__(self):
        return f"{self.subject.name} — {self.group.name} ({self.time_start:%d.%m %H:%M})"


# --- Посещаемость ---
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    present = models.BooleanField(default=False)
    recognized_by_face = models.BooleanField(default=False)

    def __str__(self):
        status = "✅" if self.present else "❌"
        return f"{self.student} — {self.schedule.subject.name} ({status})"
