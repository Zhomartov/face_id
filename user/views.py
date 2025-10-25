from django.views import View
from django.shortcuts import render
import cv2
import numpy as np
from django.http import StreamingHttpResponse
from .models import UserAccounts , Student, Teacher
import face_recognition
import dlib
from django.http import JsonResponse
from .forms import StudentForm, TeacherForm, GroupForm


class Home_view(View):
    template_name = "user/home_view.html"

    def get(self, request, *args, **kwargs):  # <- обязательно request + *args, **kwargs
        context = {}
        return render(request, self.template_name, context)


class Video_stream(View):
    last_recognized_user = None  
    def __init__(self):
        super().__init__()
        # Загружаем известных пользователей
        self.known_face_encodings = []
        self.known_face_names = []

        users = UserAccounts.objects.all()
        for u in users:
            encoding = np.frombuffer(u.face_encode, dtype=np.float64)
            self.known_face_encodings.append(encoding)
            self.known_face_names.append(str(u.uuid))

        # Инициализация dlib моделей Обязательно изменить под свой
        self.face_detector = dlib.get_frontal_face_detector()
        self.shape_predictor = dlib.shape_predictor(
            "/home/olzhas/Desktop/project/Face_id/face_recognition_models/face_recognition_models/models/shape_predictor_68_face_landmarks.dat")
        self.face_rec_model = dlib.face_recognition_model_v1(
            "/home/olzhas/Desktop/project/Face_id/face_recognition_models/face_recognition_models/models/dlib_face_recognition_resnet_model_v1.dat")

    def generate_frames(self):
        video_capture = cv2.VideoCapture(0)
        process_this_frame = True

        try:
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break

                face_names = []

                if process_this_frame:
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    rgb_small_frame = small_frame[:, :, ::-1]

                    # Находим лица
                    dets = self.face_detector(rgb_small_frame, 1)
                    face_encodings = []

                    for det in dets:
                        shape = self.shape_predictor(rgb_small_frame, det)
                        frame_uint8 = rgb_small_frame.astype(np.uint8)
                        encoding = np.array(self.face_rec_model.compute_face_descriptor(frame_uint8, shape))
                        face_encodings.append(encoding)


                    # Сравниваем с базой
                    for face_encoding in face_encodings:
                        matches = np.linalg.norm(np.array(self.known_face_encodings) - face_encoding, axis=1)
                        name = "Unknown"

                        if len(self.known_face_encodings) > 0:
                            best_match_index = np.argmin(matches)
                            if matches[best_match_index] < 0.6:  # порог для распознавания
                                name = self.known_face_names[best_match_index]

                        face_names.append(name)

                    # Координаты для рамок (dlib.rect -> top, right, bottom, left)
                    face_locations = [(det.top(), det.right(), det.bottom(), det.left()) for det in dets]
                else:
                    face_locations = []

                process_this_frame = not process_this_frame

                for (top, right, bottom, left), uuid in zip(face_locations, face_names):
                    padding = 50
                    top = max(0, top*4 - padding)
                    right = right*4 + padding
                    bottom = bottom*4 + padding
                    left = max(0, left*4 - padding)

                    name = "Unknown"
                    try:
                        if uuid != 'Unknown':
                            student = Student.objects.get(user=uuid)
                            name = student.first_name
                            Video_stream.last_recognized_user = student
                    except Student.DoesNotExist:
                        try:
                            teacher = Teacher.objects.get(user=uuid)
                            name = teacher.first_name
                            Video_stream.last_recognized_user = teacher
                        except Teacher.DoesNotExist:
                            Video_stream.last_recognized_user = None
                            pass

                    if name == 'Unknown':
                        cv2.rectangle(frame, (left, top), (right, bottom), ( 0, 0 , 255), 2)
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0 , 255), cv2.FILLED)
                    else:
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)                # Кодируем и отправляем кадр
                
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue

                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        finally:
            video_capture.release()

    def get(self, request, *args, **kwargs):
        return StreamingHttpResponse(
            self.generate_frames(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )

def check_recognition(request):
    user = Video_stream.last_recognized_user
    if user:
        return JsonResponse({"found": True, "name": user.first_name})
    return JsonResponse({"found": False})


class Class_view(View):
    def get(self, request):
        user = Video_stream.last_recognized_user
        
        # Если пользователя нет (например, переход вручную)
        if not user:
            return redirect('home')

        # Сохраняем данные в контексте
        context = {'user': user}

        # После отображения страницы сбрасываем, чтобы не перенаправляло снова
        Video_stream.last_recognized_user = None

        return render(request, 'user/class_view.html', context)

class Add_view(View):
    def get(self, request):
        student_form = StudentForm()
        teacher_form = TeacherForm()
        group_form = GroupForm()
        return render(request, 'user/add_view.html', {
            'student_form': student_form,
            'teacher_form': teacher_form,
            'group_form': group_form
        })
