
import imp
import profile
import re
import django
import time
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required

from home.models import UserProfile, CriminalMasterData
from myapp.settings import TIME_ZONE

from .forms import RegistrationForm


def registerPage(request):
    form = RegistrationForm()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            # user = UserProfile.objects.create_user(email=form.cleaned_data.get('email'),username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password1'))
            # user.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            auth = authenticate(username)
            
            messages.success(request, 'Account was created for ' + username )
            
                

            return redirect('crim:login')



    context = {'form' :form}
    return render(request, 'register.html', context)


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username , password=password)

        if user is not None:
            login(request, user)
            return redirect('crim:home')

        else:
            username = request.POST['username']
            messages.info(request, 'Username or Password is incorrect')
            return render(request, 'login.html', {'username': username})
    context ={}
    return render(request, 'login.html', context)


@login_required(login_url='/login/')
def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='/login/')
def index(request):
    role = request.user.groups.all()[0].name
    print(role)
    crim_data = CriminalMasterData.objects.all().values_list('criminal_name', 'criminal_age', 'criminal_dob', 'crime', 'created_by__username')

    # return render(request, 'home.html', {'crim_data': crim_data})
    return render(request, 'home.html', {'crim_data': crim_data})



@login_required(login_url='/login/')
def add_criminal_data(request):
    """Add student profile picture"""

    if request.POST:
        profile_pic = request.FILES.get('profile_pic')
        crim_name = request.POST.get('crim_name')
        crim_age = request.POST.get('crim_age')
        crim_dob = request.POST.get('crim_dob')
        crime = request.POST.get('crime')
        print(profile_pic)
        print(request.FILES)
        fs=FileSystemStorage()
        filename = fs.save(profile_pic.name, profile_pic)
        url = fs.url(filename)
        add_crim = CriminalMasterData(criminal_name=crim_name, criminal_age=crim_age, criminal_dob=crim_dob, criminal_image=url, crime=crime, created_by=request.user)
        add_crim.save()
        con = True
    
    return render(request, 'home.html', {'con': con})


def findEncodings(images):
    encodeList = []
    
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


@login_required(login_url='/login/')
def criminal_face_recognition(request):
    """Recoginise the face"""
    lecSche = request.GET.get('lecSche')
    path = 'media'
    images = []
    classNames = []
    myList = os.listdir(path)
    print(myList)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    print(classNames)

    # print(u.profile_pic.name == '/media/'+str(myList[0]))

    encodeListKnown = findEncodings(images)
    print('Encoding Complete')

    cap = cv2.VideoCapture(0)
    name = None
    # while True:
    success, img = cap.read()
    # img = captureScreen()
    print(success)
    print(img)
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
# print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex]
# print(name)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
        #     time.sleep(5)
        # break
    index = classNames.index(name)
    u = UserProfile.objects.get(profile_pic='/media/'+str(myList[index]))
    # res = addLogs(u,lecSche)

    cv2.imshow('Webcam', img)
    cv2.waitKey(1)

    return render(request, 'home.html', {'con':res})


# def addLogs(stu_obj, lec_obj):
#     """Mark the attendance"""
#     lecture = LectureScheduler.objects.get(id=lec_obj)
#     start_time = datetime.strptime(lecture.start_time)
#     tym_diff = (datetime.now() - start_time).seconds
#     if tym_diff > 750:
#         attendance = LectureAttendance(student=stu_obj,lecture_schedule=lecture,is_present='L')
#     else:
#         attendance = LectureAttendance(student=stu_obj,lecture_schedule=lecture)
#     attendance.save()
#     return True

    
    

