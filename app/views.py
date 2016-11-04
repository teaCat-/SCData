# -*- coding: utf-8 -*-
# Create your views here.

from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect
from models import *
from datetime import datetime
from urlparse import *
import xlrd
import xlwt
from django import forms


class Object(object):
    pass

class FileUploadedForm(forms.Form):
    uploaded_file = forms.FileField(required=False)


def index(request):
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)

    curruser = None
    entered = 0
    curruserName = request.session.get("curUser", False)
    if curruserName:
        curruser = User.objects.get(username = curruserName)
        if curruser.groups.filter(name="chief"):
            entered = "chief"
        if curruser.groups.filter(name="worker"):
            entered = "worker"
        if curruser.groups.filter(name="invest-manager"):
            entered = "invest-manager"
    userSch = None
    try:
        userSch = tUserSch.objects.get(user = curruser)
    except:
        pass

    selTable = request.POST.get("selQSch", None)

    queryList = []
    val = ""
    if userSch is not None:
        if selTable == "startuper":
            val = request.POST.get("tbQSch", None)
            tmpStups = tStartuper.objects.filter(surname__icontains = val)
            if not (entered == "chief" and userSch.school.city == u"Київ"):
                tmpStups = tmpStups.filter(school = userSch.school)
            for item in tmpStups:
                tmpObj = Object()
                tmpObj.startuper = item
                tmpprj = tTeam.objects.filter(startuperID = item)
                if len(tmpprj)>0:
                    tmpObj.projects = tmpprj
                queryList.append(tmpObj)

        if selTable == "project" or selTable is None:
            val = request.POST.get("tbQSch", "")
            tmpRez = tProject.objects.filter(title__icontains = val)
            if not (entered == "chief" and userSch.school.city == u"Київ"):
                tmpRez = tmpRez.filter(school = userSch.school)
            queryList.extend(tmpRez)

        if selTable == "investor":
            val = request.POST.get("tbQSch", None)
            tmpRez = tInvestor.objects.filter(investor__icontains = val)
            if not (entered == "chief" and userSch.school.city == u"Київ"):
                tmp2Rez = tmpRez.filter(school = None)
                tmpRez = tmpRez.filter(school = userSch.school)
                queryList.extend(tmp2Rez)
            queryList.extend(tmpRez)

        if selTable == "mentor":
            val = request.POST.get("tbQSch", None)
            tmpRez = tMentor.objects.filter(surname__icontains = val)
            if not (entered == "chief" and userSch.school.city == u"Київ"):
                tmpRez = tmpRez.filter(school = userSch.school)
            queryList.extend(tmpRez)

        if selTable == "event":
            val = request.POST.get("tbQSch", None)
            tmpRez = tActivities.objects.filter(title__icontains=val)
            if not (entered == "chief" and userSch.school.city == u"Київ"):
                tmpRez = tmpRez.filter(school=userSch.school)
            queryList.extend(tmpRez)

    else:

        if selTable == "project" or selTable is None:
            val = request.POST.get("tbQSch", "")
            tmpRez = tProject.objects.filter(title__icontains = val)
            queryList.extend(tmpRez)

    return render(request, "index.html", {"name":curruser,
                                          "entered":entered,
                                          "queryList":queryList,
                                          "schVal":val,
                                          "selTable":selTable,
                                          })

def auth(request):
    id = request.session.get("curUser", None)
    logErr = 0
    login = request.POST.get("txtLogin",False)
    passwd = request.POST.get("txtPasswd",False)
    user = authenticate(username = login, password = passwd)
    if request.POST:
        if user is not None:
            request.session["curUser"] = user.username
            return redirect("index")
        else:
            logErr = 1
    return render(request, "auth.html", {"logErr":logErr})

def regi(request):
    nameErr = None
    mailErr = None
    passErr = None
    repassErr = None
    if request.session.get("curUser", None) != None:
        currUser = User.objects.get(username=request.session.get("curUser", None))
        if not currUser.groups.filter(name = "chief"):
            return redirect("index")
    else:
            return redirect("index")
    school = Object()
    try:
        school = tUserSch.objects.get(user = currUser)
    except:
        print ("Error getting region. Contact admin or developer...")

    message = ""
    login = request.POST.get("txtLogin",False)
    mail = request.POST.get("txtMail",False)
    passwd = request.POST.get("txtPasswd",False)
    repasswd = request.POST.get("txtRePasswd",False)
    gname = request.POST.get("selGroup",False)
    if request.POST:
        if passwd != repasswd:
            repassErr = ("Пароли не совпадают").decode("utf-8")
        if User.objects.filter(username=login):
            nameErr = ("Логин уже занят").decode("utf-8")
        if User.objects.filter(email=mail):
            mailErr = ("E-mail уже занят").decode("utf-8")
        if passwd != False and login != False and nameErr == None and mailErr == None and mail != False and repasswd != False and repasswd == passwd:
            if Group.objects.filter(name=gname):
                group = Group.objects.get(name=gname)
            else:
                group = Group.objects.create(name=gname)
                group.save()
            user = User.objects.create_user(username=login, email=mail, password=passwd)
            user.groups.add(group)
            user.save()
            userSch = tUserSch.objects.create(user = user, school = school.school)
            userSch.save()
            message = u"Користувач '"+login+u"' додан!"
    return render(request, "regi.html", {"nameErr":nameErr,
                                                    "mailErr":mailErr,
                                                    "passErr":passErr,
                                                    "repassErr":repassErr,
                                                    "message":message,
                                         })

def logout(request):
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id != None:
            request.session["curUser"] = None
            return redirect("index")
        else:
            return redirect("auth")


def fillFormsStartuper(excelList, excelKeys):
    rezList = []
    i=1
    for startuper in excelList:
        newStartuper = Object()
        newStartuper.num = i
        if u"ім'я" in excelKeys:
            newStartuper.name = startuper[excelKeys.index(u"ім'я")]
        if u"прізвище" in excelKeys:
            newStartuper.surname = startuper[excelKeys.index(u"прізвище")]
        if u"побатькові" in excelKeys:
            newStartuper.midname = startuper[excelKeys.index(u"побатькові")]
        if u"телефон" in excelKeys:
            newStartuper.phone = startuper[excelKeys.index(u"телефон")]
        if u"пошта" in excelKeys:
            newStartuper.mail = startuper[excelKeys.index(u"пошта")]
        if u"1ступень" in excelKeys:
            if startuper[excelKeys.index(u"1ступень")] == u"да":
                newStartuper.fgrade = True
            else:
                newStartuper.fgrade = False
        if u"2ступень" in excelKeys:
            if startuper[excelKeys.index(u"2ступень")] == u"да":
                newStartuper.sgrade = True
            else:
                newStartuper.sgrade = False
        if u"рікзакінчення" in excelKeys:
            newStartuper.finyear = startuper[excelKeys.index(u"рікзакінчення")]
        rezList.append(newStartuper)
        i+=1
    return rezList

def addStartuperToDB(request, index, projectID, school):
    samephones = tStartuper.objects.filter(phone = request.POST.getlist('tbPhone')[index]).exclude(phone = "")
    if len(samephones) != 0:
        return request.POST.getlist('tbSurname')[index] + " " + request.POST.getlist('tbName')[index] + " " + request.POST.getlist('tbMidname')[index] + (
            " не був добавлен. Стартапер с таким номером телефона вже є в базі.").decode("utf-8")
    samemail = tStartuper.objects.filter(mail = request.POST.getlist('tbMail')[index]).exclude(mail = "")
    if len(samemail) != 0:
        return request.POST.getlist('tbSurname')[index] + " " + request.POST.getlist('tbName')[index] + " " + request.POST.getlist('tbMidname')[index] + (
            " не був добавлен. Стартапер с такой поштой вже є в базі.").decode("utf-8")

    tmpFgrade = request.POST.get('cbFgrade'+str(index+1),False)
    tmpSgrade = request.POST.get('cbSgrade'+str(index+1),False)
    newStartuper = tStartuper.objects.create(
        name = request.POST.getlist('tbName')[index],
        surname = request.POST.getlist('tbSurname')[index],
        midname = request.POST.getlist('tbMidname')[index],
        phone = request.POST.getlist('tbPhone')[index],
        mail = request.POST.getlist('tbMail')[index],
        fgrade = tmpFgrade,
        sgrade = tmpSgrade,
        finyear = request.POST.get('tbFinYear'+str(index+1), "-"),
        school=school.school
    )

    form = FileUploadedForm(request.POST, request.FILES)
    if form.is_valid():
        input_file = request.FILES.get('fAvatar'+str(index+1), None)
        if input_file != None:
            tmpFName = input_file.name.split(".")
            tmpFName = tmpFName.pop()
            if input_file.size < 100000:
                if tmpFName == "jpg" or tmpFName == "jepg" or tmpFName == "png" or tmpFName == "gif":
                    newStartuper.avatar = input_file
                else:
                    return newStartuper.name + " " + newStartuper.surname + " " + newStartuper.midname + (
                    " додан до бази! Помилка при доданні зображення. Зображення має невірний формат").decode("utf-8")
            else:
                newStartuper.save()
                return newStartuper.name+" "+newStartuper.surname+" "+newStartuper.midname+(
                    " додан до бази! Помилка при доданні зображення. Розмір зображення привищує 100кб").decode("utf-8")
    newStartuper.save()
    if projectID != "False":
        project = tProject.objects.get(id = projectID)
        team = tTeam.objects.create(startuperID = newStartuper, projectID = project)
        team.save()
    return newStartuper.name+" "+newStartuper.surname+" "+newStartuper.midname+(" додан до бази!").decode("utf-8")

def fillFormsProject(excelList, excelKeys):
    rezList = []
    i=1
    for project in excelList:
        newProject = Object()
        newProject.num = i
        if u"назва" in excelKeys:
            newProject.title = project[excelKeys.index(u"назва")]
        if u"головнийстартапер" in excelKeys:
            newProject.leader = project[excelKeys.index(u"головнийстартапер")]
        if u"галузь" in excelKeys:
            newProject.sector = project[excelKeys.index(u"галузь")]
        if u"опис" in excelKeys:
            newProject.descr = project[excelKeys.index(u"опис")]
        if u"ментор" in excelKeys:
            newProject.mentor = project[excelKeys.index(u"ментор")]
        if u"видпродукції" in excelKeys:
            newProject.type = project[excelKeys.index(u"видпродукції")]
        if u"формапродукції" in excelKeys:
            newProject.isreal = project[excelKeys.index(u"формапродукції")]
        if u"розмірфінансування" in excelKeys:
            newProject.financeScale = project[excelKeys.index(u"розмірфінансування")]
        if u"школа" in excelKeys:
            newProject.school = project[excelKeys.index(u"школа")]
        rezList.append(newProject)
        i+=1
    return rezList

def addProjectToDB(request, index, startuperID, school):
    projIsExhist = 0
    try:
        projIsExhist = tProject.objects.filter(title = request.POST.getlist('tbTitle')[index])
    except:
        pass
    if len(projIsExhist) >= 1:
        return "Проект з такою назвою вже є у базі."
    else:
        mailLead = request.POST.getlist('tbLeader')[index]
        try:
            lead = tStartuper.objects.get(id=mailLead)
        except:
            return request.POST.getlist('tbTitle')[index]+u". Стартапер с такой почтой не обнаружен. Выберете из списк или создайте нового."
        mailMent = request.POST.getlist('tbMentor')[index]
        try:
            mentor = tMentor.objects.get(id=mailMent)
        except:
            return request.POST.getlist('tbTitle')[index]+u". Ментор с такой почтой не обнаружен. Выберете из списк или создайте нового."
        newProject = tProject.objects.create(
            title = request.POST.getlist('tbTitle')[index],
            sector = request.POST.getlist('tbSector')[index],
            descr = request.POST.getlist('taDescr')[index],
            type = request.POST.getlist('selType')[index],
            isreal = request.POST.getlist('selIsReal')[index],
            financeScale = request.POST.getlist('tbFinScale')[index],
            school = school.school,
        )
        if startuperID != "False":
            startuper = tStartuper.objects.get(id = startuperID)
            team = tTeam.objects.create(startuperID = startuper, projectID = newProject)
            team.save()
        newProject.save()
        team = tTeam.objects.create(projectID = newProject, startuperID = lead, role="Головний стартапер", islead = True)
        team.save()
        members = request.POST.getlist('tbMem'+(index+1).__str__())
        for item in members:
            tTeam.objects.get_or_create(projectID = newProject, startuperID = tStartuper.objects.get(id = item))
            aa = tTeam.objects.get(projectID = newProject, startuperID = tStartuper.objects.get(id = item))
            print aa
        mentoproj = tMentoproj.objects.create(mentorID = mentor, projectID = newProject, date = datetime.strptime(datetime.now().date().__format__('%d.%m.%Y, %H:%M').__str__(), "%d.%m.%Y, %H:%M"))
        mentoproj.save()
        taglist = request.POST.get("selTags"+str(index+1), None).replace(", ", " ").replace(","," ").split(" ")
        keywordList= tKeyWord.objects.filter(word__in = taglist)
        for item in taglist:
            keyword = tKeyWord.objects.get_or_create(word = item)
            keyword = tKeyWord.objects.get(word = item)
            tKeyWordToProject.objects.create(word = keyword, projectID = newProject)
        return newProject.title+(" додан до бази!").decode("utf-8")

def fillFormsInvestor(excelList, excelKeys):
    rezList = []
    i=1
    for investor in excelList:
        newInvestor = Object()
        newInvestor.num = i
        if u"інвестор" in excelKeys:
            newInvestor.title = investor[excelKeys.index(u"інвестор")]
        if u"опис" in excelKeys:
            newInvestor.descr = investor[excelKeys.index(u"опис")]
        i+=1
    return rezList

def addInvestorToDB(request, index, school, curruser):
    invtype = request.POST.get('selInvType')
    newInvestor = tInvestor.objects.create(
        investor = request.POST.getlist('tbInvestor')[index],
        descr = request.POST.getlist('taDescr')[index],
    )
    if invtype == "local":
        newInvestor.school = school.school
    if invtype == "personal":
        newInvestor.user = curruser
        newInvestor.message = request.POST.get("taMsg")
    newInvestor.save()
    return newInvestor.investor+(" додан до бази!").decode("utf-8")

def fillFormsInvContacts(excelList, excelKeys):
    rezList = []
    i=1
    for investor in excelList:
        newInvestor = Object()
        newInvestor.num = i
        if u"ім'я" in excelKeys:
            newInvestor.name = investor[excelKeys.index(u"ім'я")]
        if u"прізвище" in excelKeys:
            newInvestor.surname = investor[excelKeys.index(u"прізвище")]
        if u"побатькові" in excelKeys:
            newInvestor.midname = investor[excelKeys.index(u"побатькові")]
        if u"телефон" in excelKeys:
            newInvestor.phone = investor[excelKeys.index(u"телефон")]
        if u"пошта" in excelKeys:
            newInvestor.mail = investor[excelKeys.index(u"пошта")]
        if u"должність" in excelKeys:
            newInvestor.mail = investor[excelKeys.index(u"должність")]
        if u"посада" in excelKeys:
            newInvestor.mail = investor[excelKeys.index(u"посада")]
        rezList.append(newInvestor)
        i+=1
    return rezList

def addInvContToDB(request, id, index, school):
    newInvCont = tInvestorContacts.objects.create(
        investorID = id,
        name = request.POST.getlist('tbName')[index],
        surname = request.POST.getlist('tbSurname')[index],
        midname = request.POST.getlist('tbMidname')[index],
        phone = request.POST.getlist('tbPhone')[index],
        mail = request.POST.getlist('tbMail')[index],
        company = request.POST.getlist('tbCompany')[index],
        position = request.POST.getlist('tbPosition')[index],
        school = school.school
    )

    newInvCont.save()
    return newInvCont.surname+" "+newInvCont.name+" "+newInvCont.midname+(" додан до бази!").decode("utf-8")

def fillFormsMentor(excelList, excelKeys):
    rezList = []
    i=1
    for mentor in excelList:
        newMentor = Object()
        newMentor.num = i
        if u"ім'я" in excelKeys:
            newMentor.name = mentor[excelKeys.index(u"ім'я")]
        if u"прізвище" in excelKeys:
            newMentor.surname = mentor[excelKeys.index(u"прізвище")]
        if u"побатькові" in excelKeys:
            newMentor.midname = mentor[excelKeys.index(u"побатькові")]
        if u"телефон" in excelKeys:
            newMentor.phone = mentor[excelKeys.index(u"телефон")]
        if u"пошта" in excelKeys:
            newMentor.mail = mentor[excelKeys.index(u"пошта")]
        rezList.append(newMentor)
        i+=1
    return rezList

def addMentorToDB(request, index, projectID, school):
    samemail=tMentor.objects.filter(mail=request.POST.getlist('tbMail')[index])
    if len(samemail) != 0:
        return request.POST.getlist('tbSurname')[index] + " " + request.POST.getlist('tbName')[index] + " " + request.POST.getlist('tbMidname')[index] + (
            " не був додан до бази. Ментор с такой почтой вже є у базі.").decode("utf-8")
    newMent = tMentor.objects.create(
        name = request.POST.getlist('tbName')[index],
        surname = request.POST.getlist('tbSurname')[index],
        midname = request.POST.getlist('tbMidname')[index],
        phone = request.POST.getlist('tbPhone')[index],
        mail = request.POST.getlist('tbMail')[index],
        school = school.school
    )
    if projectID != "False":
        project = tProject.objects.get(id = projectID)
        sig = tMentoproj.objects.create(mentorID = newMent, projectID = project, date = datetime.now())
        sig.save()
    newMent.save()
    return newMent.surname+" "+newMent.name+" "+newMent.midname+(" додан до бази!").decode("utf-8")

def add(request):
    """Worker validation"""
    entered = 0
    curruser = None
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
            if curruser.groups.filter(name="invest-manager"):
                entered = "invest-manager"
    if entered != "worker" and entered != "invest-manager":
        return redirect("index")
    school = Object()
    try:
        school = tUserSch.objects.get(user = curruser)
    except:
        print ("Error getting region. Contact admin or developer...")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    obj = urldata.get('obj', None)
    if obj != None:
        obj = obj.pop()
    added = urldata.get('added', False)
    if added != False:
        added = added.pop()
    startuperID = urldata.get('startuperID', False)
    if startuperID != False:
        startuperID = startuperID.pop()
    projectID = urldata.get('projectID', False)
    if projectID != False:
        projectID = projectID.pop()


    """Adding data to froms & database"""
    inputList = []
    inputsQty = int(request.POST.get("tbQuantity",1))
    resultList = []
    schoolList = []
    possibleLeaders = []
    mentors = []
    taglist = []
    loaded = False
    inputOpt = 0
    memberStr = ""

    """Loading and getting data from excel file"""
    excelKeys = []
    excelList = []
    try:
        if request.method == 'POST':
            form = FileUploadedForm(request.POST, request.FILES)
            if form.is_valid():
                input_file = request.FILES.get('excelImport')
                if input_file != None:
                    tmpFName = input_file.name.split(".")
                    tmpFName = tmpFName.pop()
                    if tmpFName == "xlsx" or tmpFName == "xls":
                        wb = xlrd.open_workbook(file_contents=input_file.read())
                        wb_sheet = wb.sheet_by_index(0)
                        row = wb_sheet.row_values(0)
                        for item in row:
                            excelKeys.append(unicode(item).lower().replace(" ",""))
                        for rownum in range(1, wb_sheet.nrows):
                            row = wb_sheet.row_values(rownum)
                            row.append(rownum)
                            excelList.append(row)
                            inputsQty = 0
    except:
        pass

    if obj == "startuper":
        if entered == "invest-manager":
            return redirect("index")
        obj = "стартапера"
        if request.FILES.get('excelImport', False):
            inputList = fillFormsStartuper(excelList, excelKeys)
            loaded = True
            inputOpt = 1

        for x in range(0,inputsQty):
            tmpObj = Object()
            tmpObj.num = x+1
            inputList.append(tmpObj)
            loaded = True
            inputOpt = 1

        if request.method == 'POST' and added == 'true':
            tmpList = request.POST.getlist('tbSurname')
            for item in tmpList:
                resultList.append(addStartuperToDB(request, request.POST.getlist('tbSurname').index(item),projectID, school))

    if obj == "project":
        if entered == "invest-manager":
            return redirect("index")
        schoolList = tSchool.objects.all()
        possibleLeaders = tStartuper.objects.all().order_by("surname","name")
        for item in possibleLeaders:
            memberStr += item.name+" "+item.surname+"|"+item.id.__str__()+","
        memberStr = memberStr[:-1]
        mentors = tMentor.objects.all().order_by("surname","name")
        obj = "проект"
        taglist = tKeyWord.objects.all()

        if request.FILES.get('excelImport', False):
            inputList = fillFormsProject(excelList, excelKeys)
            loaded = True
            inputOpt = 2

        for x in range(0,inputsQty):
            tmpObj = Object()
            tmpObj.num = x+1
            inputList.append(tmpObj)
            loaded = True
            inputOpt = 2

        if request.method == 'POST' and added == 'true':
            tmpList = request.POST.getlist('tbTitle')
            for item in tmpList:
                resultList.append(addProjectToDB(request, request.POST.getlist('tbTitle').index(item), startuperID, school))

    if obj == "investor":
        if entered == "worker":
            return redirect("index")
        obj = "інвестора"
        if request.FILES.get('excelImport', False):
            inputList = fillFormsInvestor(excelList, excelKeys)
            loaded = True
            inputOpt = 3

        for x in range(0,inputsQty):
            tmpObj = Object()
            tmpObj.num = x+1
            inputList.append(tmpObj)
            loaded = True
            inputOpt = 3

        if request.method == 'POST' and added == 'true':
            tmpList = request.POST.getlist('tbInvestor')
            for item in tmpList:
                resultList.append(addInvestorToDB(request, request.POST.getlist('tbInvestor').index(item), school, curruser))

    if obj == "mentor":
        if entered == "invest-manager":
            return redirect("index")
        obj = "ментора"
        if request.FILES.get('excelImport', False):
            inputList = fillFormsMentor(excelList, excelKeys)
            loaded = True
            inputOpt = 4

        for x in range(0,inputsQty):
            tmpObj = Object()
            tmpObj.num = x+1
            inputList.append(tmpObj)
            loaded = True
            inputOpt = 4

        if request.method == 'POST' and added == 'true':
            tmpList = request.POST.getlist('tbSurname')
            for item in tmpList:
                resultList.append(addMentorToDB(request, request.POST.getlist('tbSurname').index(item),projectID, school))

    err = 0
    for item in resultList:
        if "!" not in item:
            err = 1
            break

    return render(request, "adding/add.html", {"obj": obj,
                                        "name":curruser,
                                        "entered":entered,
                                        "inputList":inputList,
                                        "loaded":loaded,
                                        "inputOpt":inputOpt,
                                        "added":added,
                                        "resultList":resultList,
                                        "startuperID":startuperID,
                                        "projectID":projectID,
                                        "possibleLeaders":possibleLeaders,
                                        "mentors":mentors,
                                        "inputsQty":inputsQty,
                                        "err":err,
                                        "taglist":taglist,
                                        "schoolList":schoolList,
                                        "memberStr":memberStr,
                                        })



def search(request):
    """Worker validation"""
    entered = 0
    curruser = None
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
            if curruser.groups.filter(name="chief"):
                entered = "chief"
            if curruser.groups.filter(name="invest-manager"):
                entered = "invest-manager"
    if entered != "worker" and entered != "chief" and entered != "invest-manager":
        return redirect("index")


    return render(request, "search/search.html", {"name":curruser,
                                          "entered":entered,
                                          })

def startupersearch(request):
    """Worker validation"""
    entered = 0
    curruser = None
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
            if curruser.groups.filter(name="chief"):
                entered = "chief"
            if curruser.groups.filter(name="invest-manager"):
                entered = "invest-manager"
    if entered != "worker" and entered != "chief" and entered != "invest-manager":
        return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        pass

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    export = urldata.get('export', None)
    if export != None:
        export = export.pop()

    queryList = []
    resultList = []
    searchObj = Object()
    file=datetime.now().time().__format__("%H%M%S").__str__()
    if request.method == "POST":
        searchObj.surname = request.POST.get("tbSurname", "")
        searchObj.name = request.POST.get("tbName", "")
        searchObj.midname = request.POST.get("tbMidname", "")
        searchObj.phone = request.POST.get("tbPhone", "")
        searchObj.mail = request.POST.get("tbMail", "")
        searchObj.finyear = request.POST.get("tbFinYear", "")
        searchObj.fgrade = bool(request.POST.get("cbFgrade", False))
        searchObj.sgrade = bool(request.POST.get("cbSgrade", False))
        searchObj.projects = request.POST.getlist("tbProjects", "")

        projectIDs = tProject.objects.filter(title__in=searchObj.projects)
        teamIDs = tTeam.objects.filter(projectID__in = projectIDs)
        tmpTeamIDs =[]
        for item in teamIDs:
            tmpTeamIDs.append(item.startuperID.id)
        resultList = tStartuper.objects.filter(
            surname__icontains = searchObj.surname,
            name__icontains = searchObj.name,
            midname__icontains = searchObj.midname,
            phone__icontains = searchObj.phone,
            mail__icontains = searchObj.mail,
            finyear__icontains = searchObj.finyear
        )
        if len(tmpTeamIDs) != 0:
            resultList = resultList.filter(id__in=tmpTeamIDs,)
        if bool(searchObj.fgrade) == True:
            resultList = resultList.filter(fgrade=True)
        if bool(searchObj.sgrade) == True:
            resultList = resultList.filter(sgrade=True)

        if not (entered == "chief" and userSch.school.city == u"Київ"):
            resultList = resultList.filter(school = userSch.school)

        for item in resultList:
            tmpObj = Object()
            tmpObj.startuper = item
            tmpprj = tTeam.objects.filter(startuperID = item)
            if len(tmpprj)>0:
                tmpObj.projects = tmpprj
            queryList.append(tmpObj)

        if export == "true":

            wb = xlwt.Workbook()
            ws = wb.add_sheet('Startupers')

            ws.write(0, 0, u"Призвіще")
            ws.write(0, 1, u"Ім'я")
            ws.write(0, 2, u"По батькові")
            ws.write(0, 3, u"Телефон")
            ws.write(0, 4, u"Пошта")
            ws.write(0, 5, u"1 ступень")
            ws.write(0, 6, u"2 ступень")
            ws.write(0, 7, u"Рік закінчення")

            tmpRowCnt = 1
            for item in resultList:
                ws.write(int(tmpRowCnt), 0, item.surname)
                ws.write(int(tmpRowCnt), 1, item.name)
                ws.write(int(tmpRowCnt), 2, item.midname)
                ws.write(int(tmpRowCnt), 3, item.phone)
                ws.write(int(tmpRowCnt), 4, item.mail)
                if item.fgrade is True:
                    ws.write(int(tmpRowCnt), 5, u"да")
                else:
                    ws.write(int(tmpRowCnt), 5, u"нет")
                if item.sgrade is True:
                    ws.write(int(tmpRowCnt), 6, u"да")
                else:
                    ws.write(int(tmpRowCnt), 6, u"нет")
                ws.write(int(tmpRowCnt), 7, item.finyear)
                tmpRowCnt += 1
            wb.save("files/export/export"+file+".xls")

    return render(request, "search/startupersearch.html", {"name":curruser,
                                          "entered":entered,
                                          "resultList":queryList,
                                          "searchObj":searchObj,
                                          "export":export,
                                          "file":file,
                                          })

def projectsearch(request):
    """Worker validation"""
    entered = 0
    curruser = None
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
            if curruser.groups.filter(name="chief"):
                entered = "chief"
            if curruser.groups.filter(name="invest-manager"):
                entered = "invest-manager"
    if entered != "worker" and entered != "chief" and entered != "invest-manager":
        return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        pass

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    export = urldata.get('export', None)
    if export != None:
        export = export.pop()

    resultList = []
    schoolList = tSchool.objects.all()
    searchObj = Object
    file=datetime.now().time().__format__("%H%M%S").__str__()

    taglist = tKeyWord.objects.all()
    if request.method == "POST":
        searchObj.title = request.POST.get("tbTitle", "")
        searchObj.sector = request.POST.get("tbSector", "")
        searchObj.type = request.POST.get("selType", "")
        searchObj.isreal = request.POST.get("selIsReal", "")
        searchObj.descr = request.POST.get("tbDescr", "")

        resultList = tProject.objects.filter(
            title__icontains = searchObj.title,
            sector__icontains = searchObj.sector,
            type__icontains = searchObj.type,
            isreal__icontains = searchObj.isreal,
            descr__icontains = searchObj.descr,
        )

        if not (entered == "chief" and userSch.school.city == u"Київ"):
            resultList = resultList.filter(school = userSch.school)

        if request.POST.get("selSchool", "zero") != "zero":
            searchObj.school = tSchool.objects.get(id = request.POST.get("selSchool", 0))
            resultList = resultList.filter(school = searchObj.school)
        else:
            searchObj.school = None


        tags = tKeyWord.objects.filter(id__in=request.POST.getlist("selTags", ""))
        projWithTags = tKeyWordToProject.objects.filter(word__in=tags)
        for item in tags:
            projWithTags = projWithTags.filter(word=item)
        tmpProjIDs = []
        for item in projWithTags:
            tmpProjIDs.append(item.projectID.id)
        if len(tmpProjIDs)!=0:
            resultList = resultList.filter(id__in=tmpProjIDs)

        tmpMent = Object()
        tmpMent.mail = ""

        tmpLead = Object()
        tmpLead.mail = ""


        if export == "true":
            wb = xlwt.Workbook()
            ws = wb.add_sheet('Projects')

            ws.write(0, 0, u"Назва")
            ws.write(0, 1, u"Галузь")
            ws.write(0, 2, u"Вид продукції")
            ws.write(0, 3, u"Форма продукції")
            ws.write(0, 4, u"Ментора")
            ws.write(0, 5, u"Головний стартапер")
            ws.write(0, 6, u"Опис")

            tmpRowCnt = 1
            for item in resultList:
                ws.write(int(tmpRowCnt), 0, item.title)
                ws.write(int(tmpRowCnt), 1, item.sector)
                ws.write(int(tmpRowCnt), 2, item.type)
                ws.write(int(tmpRowCnt), 3, item.isreal)

                tmpMent = tMentoproj.objects.filter(projectID = item.id).order_by("-date")
                if len(tmpMent) !=0:
                    tmpMent = tmpMent[0].mentorID
                ws.write(int(tmpRowCnt), 4, tmpMent.mail)

                tmpLead = tTeam.objects.filter(projectID=item.id, islead=True)
                if len(tmpLead) != 0:
                    tmpLead = tmpLead[0].startuperID
                ws.write(int(tmpRowCnt), 5, tmpLead.mail)

                ws.write(int(tmpRowCnt), 6, item.descr)
                tmpRowCnt += 1
            wb.save("files/export/export"+file+".xls")

    return render(request, "search/projectsearch.html", {"name":curruser,
                                          "entered":entered,
                                          "resultList":resultList,
                                          "searchObj":searchObj,
                                          "taglist":taglist,
                                          "export":export,
                                          "file":file,
                                          "schoolList":schoolList,
                                          })

def investorsearch(request):
    """Worker validation"""
    entered = 0
    curruser = None
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
            if curruser.groups.filter(name="chief"):
                entered = "chief"
            if curruser.groups.filter(name="invest-manager"):
                entered = "invest-manager"
    if entered != "worker" and entered != "chief" and entered != "invest-manager":
        return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        pass

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    export = urldata.get('export', None)
    if export != None:
        export = export.pop()

    resultList = []
    searchObj = Object
    file=datetime.now().time().__format__("%H%M%S").__str__()
    if request.method == "POST":
        searchObj.investor = request.POST.get("tbInvestor", "")
        searchObj.descr = request.POST.get("tbDescr", "")

        tmpList = tInvestor.objects.filter(
            investor__icontains = searchObj.investor,
            descr__icontains = searchObj.descr,
        )

        if not (entered == "chief" and userSch.school.city == u"Київ"):
            tmpListWithNone = tmpList.filter(school = None)
            tmpList = tmpList.filter(school = userSch.school)
            resultList.extend(tmpList)
            resultList.extend(tmpListWithNone)

        if export == "true":

            wb = xlwt.Workbook()
            ws = wb.add_sheet('Investors')

            ws.write(0, 0, u"Інвестор")
            ws.write(0, 1, u"Опис")

            tmpRowCnt = 1
            for item in resultList:
                ws.write(int(tmpRowCnt), 0, item.investor)
                ws.write(int(tmpRowCnt), 1, item.descr)
                tmpRowCnt += 1
            wb.save("files/export/export"+file+".xls")

    return render(request, "search/investorsearch.html", {"name":curruser,
                                          "entered":entered,
                                          "resultList":resultList,
                                          "searchObj":searchObj,
                                          "export":export,
                                          "file":file
                                          })

def mentorsearch(request):
    """Worker validation"""
    entered = 0
    curruser = None
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
            if curruser.groups.filter(name="chief"):
                entered = "chief"
            if curruser.groups.filter(name="invest-manager"):
                entered = "invest-manager"
    if entered != "worker" and entered != "chief" and entered != "invest-manager":
        return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        pass

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    export = urldata.get('export', None)
    if export != None:
        export = export.pop()

    resultList = []
    searchObj = Object
    file=datetime.now().time().__format__("%H%M%S").__str__()
    if request.method == "POST":
        searchObj.surname = request.POST.get("tbSurname", "")
        searchObj.name = request.POST.get("tbName", "")
        searchObj.midname = request.POST.get("tbMidname", "")
        searchObj.phone = request.POST.get("tbPhone", "")
        searchObj.mail = request.POST.get("tbMail", "")
        searchObj.projects = request.POST.getlist("tbProjects", "")

        projectIDs = tProject.objects.filter(title__in=searchObj.projects)
        teamIDs = tMentoproj.objects.filter(projectID__in=projectIDs)
        tmpTeamIDs = []
        for item in teamIDs:
            tmpTeamIDs.append(item.mentorID.id)
        resultList = tMentor.objects.filter(
            surname__icontains=searchObj.surname,
            name__icontains=searchObj.name,
            midname__icontains=searchObj.midname,
            phone__icontains=searchObj.phone,
            mail__icontains=searchObj.mail,
        )
        if len(tmpTeamIDs) != 0:
            resultList = resultList.filter(id__in=tmpTeamIDs, )

        if not (entered == "chief" and userSch.school.city == u"Київ"):
            resultList = resultList.filter(school = userSch.school)

        if export == "true":

            wb = xlwt.Workbook()
            ws = wb.add_sheet('Mentors')

            ws.write(0, 0, u"Призвище")
            ws.write(0, 1, u"Ім'я")
            ws.write(0, 2, u"По батькові")
            ws.write(0, 3, u"Телефон")
            ws.write(0, 4, u"Пошта")

            tmpRowCnt = 1
            for item in resultList:
                ws.write(int(tmpRowCnt), 0, item.surname)
                ws.write(int(tmpRowCnt), 1, item.name)
                ws.write(int(tmpRowCnt), 2, item.midname)
                ws.write(int(tmpRowCnt), 3, item.phone)
                ws.write(int(tmpRowCnt), 4, item.mail)
                tmpRowCnt += 1
            wb.save("files/export/export"+file+".xls")

    return render(request, "search/mentorsearch.html", {"name":curruser,
                                          "entered":entered,
                                          "resultList":resultList,
                                          "searchObj":searchObj,
                                          "export":export,
                                          "file":file,
                                          })

def eventsearch(request):
    """Worker validation"""
    entered = 0
    curruser = None
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
            if curruser.groups.filter(name="chief"):
                entered = "chief"
            if curruser.groups.filter(name="invest-manager"):
                entered = "invest-manager"
    if entered != "worker" and entered != "chief" and entered != "invest-manager":
        return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        pass

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    export = urldata.get('export', None)
    if export != None:
        export = export.pop()

    resultList = []
    searchObj = Object
    file=datetime.now().time().__format__("%H%M%S").__str__()
    if request.method == "POST":
        searchObj.title = request.POST.get("tbTitle", "")
        searchObj.date = request.POST.get("tbDate", "")

        resultList = tActivities.objects.filter(
            title__icontains = searchObj.title,
            date = datetime.strptime(searchObj.date, "%d.%m.%Y"),
        )

        if not (entered == "chief" and userSch.school.city == u"Київ"):
            resultList = resultList.filter(school = userSch.school)

        if export == "true":

            wb = xlwt.Workbook()
            ws = wb.add_sheet('Investors')

            ws.write(0, 0, u"Назва")
            ws.write(0, 1, u"Дата")

            tmpRowCnt = 1
            for item in resultList:
                ws.write(int(tmpRowCnt), 0, item.title)
                ws.write(int(tmpRowCnt), 1, item.date.__format__("%d.%m.%Y").__str__())
                tmpRowCnt += 1
            wb.save("files/export/export"+file+".xls")

    return render(request, "search/eventsearch.html", {"name":curruser,
                                          "entered":entered,
                                          "resultList":resultList,
                                          "searchObj":searchObj,
                                          "export":export,
                                          "file":file
                                          })


def infostartuper(request):
    curruser = 0
    entered = 0
    staff = False
    curruserName = request.session.get("curUser", False)
    if curruserName == None:
        return redirect("index")
    if curruserName:
        curruser = User.objects.get(username=curruserName)
        if curruser.groups.filter(name="chief"):
            entered = "chief"
            staff = True
        if curruser.groups.filter(name="worker"):
            entered = "worker"
            staff = True
        if curruser.groups.filter(name="invest-manager"):
            entered = "invest-manager"
            staff = True
        if staff is not True:
            return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        print ("Error getting region. Contact admin or developer...")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    _print = urldata.get('print', None)
    if _print != None:
        _print = _print.pop()
    startuper = ""
    teams = []
    projects = []
    docs = []
    addfile =""
    if _id != None:
        _id = _id.pop()
        addfile = urldata.get('addfile', "")
        if addfile != "":
            addfile = addfile.pop()
        try:
            startuper = tStartuper.objects.get(id = _id)
            if startuper.avatar == "":
                startuper.avatar = "files/imgs/avatars/noimg.png"
            teams = tTeam.objects.filter(startuperID = _id)
            for party in teams:
                projects.extend(tProject.objects.filter(id = party.projectID.id))

            docs.extend(tDoc.objects.filter(startuperID = _id))
        except:
            pass

        if startuper.school != userSch.school:
            if not (entered == "chief" and userSch.school.city == u"Київ"):
                return render(request, "nopermission.html", {"name":curruser,})

    if _print == "true":
        return render(request, "info/printstartuper.html", {"name":curruser,
                                              "entered":entered,
                                              "startuper":startuper,
                                              "teams":teams,
                                              "projects":projects,
                                              "docs":docs,
                                              "addfile":addfile,
                                              "staff":staff,
                                              })

    return render(request, "info/infostartuper.html", {"name":curruser,
                                          "entered":entered,
                                          "startuper":startuper,
                                          "teams":teams,
                                          "projects":projects,
                                          "docs":docs,
                                          "addfile":addfile,
                                          "staff":staff,
                                          })

def infoproject(request):
    curruser = None
    entered = 0
    staff = False
    curruserName = request.session.get("curUser", False)
    if curruserName:
        curruser = User.objects.get(username=curruserName)
        if curruser.groups.filter(name="chief"):
            entered = "chief"
            staff = True
        if curruser.groups.filter(name="worker"):
            entered = "worker"
            staff = True
        if curruser.groups.filter(name="invest-manager"):
            entered = "invest-manager"
            staff = True
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        pass

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    _print = urldata.get('print', None)
    if _print != None:
        _print = _print.pop()
    project = ""
    teams = []
    startupers = []
    investitions =[]
    addInfo = []
    status = []
    investors =[]
    activities = []
    mentors = []
    taglist = []
    if _id != None:
        _id = _id.pop()
        project = tProject.objects.get(id = _id)

        teams = tTeam.objects.filter(projectID = _id)
        for party in teams:
            startupers.extend(tStartuper.objects.filter(id = party.startuperID.id))
            if party.islead == True:
                project.leader = party.startuperID

        investitions = tInvestition.objects.filter(projectID = _id)
        for investition in investitions:
            investors.extend(tInvestor.objects.filter(id = investition.investorID.id))

        addInfo.extend(tAddInfoProj.objects.filter(projectID = _id))
        status.extend(tStatus.objects.filter(projectID = _id).order_by("date"))
        activities.extend(tActProj.objects.filter(projectID = _id))
        mentors.extend(tMentoproj.objects.filter(projectID = _id).order_by("-date"))

        taglist = tKeyWordToProject.objects.filter(projectID = project)

        if project.school != userSch.school:
            if not (entered == "chief" and userSch.school.city == u"Київ") and entered is not 0:
                return render(request, "nopermission.html", {"name":curruser,})

    currStat = ""
    if len(status) > 0:
        currStat = status.pop()
    currMent = ""
    if len(mentors) > 0:
        currMent = mentors[0]

    if _print == "true":
        return render(request, "info/printproject.html", {"name":curruser,
                                              "entered":entered,
                                              "project":project,
                                              "teams":teams,
                                              "startupers":startupers,
                                              "investitions":investitions,
                                              "investors":investors,
                                              "addInfo":addInfo,
                                              "status":status,
                                              "activities":activities,
                                              "currStat":currStat,
                                              "mentors":mentors,
                                              "currMent":currMent,
                                              "taglist":taglist,
                                              "staff":staff,
                                              })
    return render(request, "info/infoproject.html", {"name":curruser,
                                          "entered":entered,
                                          "project":project,
                                          "teams":teams,
                                          "startupers":startupers,
                                          "investitions":investitions,
                                          "investors":investors,
                                          "addInfo":addInfo,
                                          "status":status,
                                          "activities":activities,
                                          "currStat":currStat,
                                          "mentors":mentors,
                                          "currMent":currMent,
                                          "taglist":taglist,
                                          "staff":staff,
                                          })

def infoinvestor(request):
    curruser = 0
    entered = 0
    staff = False
    curruserName = request.session.get("curUser", False)
    if curruserName == None:
        return redirect("index")
    if curruserName:
        curruser = User.objects.get(username=curruserName)
        if curruser.groups.filter(name="chief"):
            entered = "chief"
            staff = True
        if curruser.groups.filter(name="worker"):
            entered = "worker"
            staff = True
        if curruser.groups.filter(name="invest-manager"):
            entered = "invest-manager"
            staff = True
        if staff is not True:
            return redirect("index")
    userSch = Object()
    userSch.school = Object()
    userSch.school.city = ""
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        print ("Error getting region. Contact admin or developer...")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    _print = urldata.get('print', None)
    if _print != None:
        _print = _print.pop()
    investor = ""
    investitions = []
    projects = []
    contacts = []
    addInfo = []
    if _id != None:
        _id = _id.pop()
        try:
            investor = tInvestor.objects.get(id = _id)
            investitions = tInvestition.objects.filter(investorID = _id)
            for inv in investitions:
                projects.extend(tProject.objects.filter(id = inv.investorID.id))

            contacts.extend(tInvestorContacts.objects.filter(investorID = _id))
            addInfo.extend(tAddInfoInv.objects.filter(investorID = _id))
        except:
            pass


        if investor.school != None:
            if investor.school != userSch.school:
                if not (entered == "chief" and userSch.school.city == u"Київ"):
                    return render(request, "nopermission.html", {"name":curruser,})
        if investor.user != None:
            if curruser != investor.user:
                return render(request, "nopermission.html", {"name":curruser,
                                                             "message":investor.message})

    if _print == "true":
        return render(request, "info/printinvestor.html", {"name":curruser,
                                                  "entered":entered,
                                                  "investor":investor,
                                                  "investitions":investitions,
                                                  "projects":projects,
                                                  "contacts":contacts,
                                                  "addInfo":addInfo,
                                                  "staff":staff,
                                                  })
    tVisitors.objects.create(investorID = investor, userID = curruser, date = datetime.now())
    return render(request, "info/infoinvestor.html", {"name":curruser,
                                          "entered":entered,
                                          "investor":investor,
                                          "investitions":investitions,
                                          "projects":projects,
                                          "contacts":contacts,
                                          "addInfo":addInfo,
                                          "staff":staff,
                                          })

def infoinvcontact(request):
    curruser = 0
    entered = 0
    staff = False
    curruserName = request.session.get("curUser", False)
    if curruserName == None:
        return redirect("index")
    if curruserName:
        curruser = User.objects.get(username=curruserName)
        if curruser.groups.filter(name="chief"):
            entered = "chief"
            staff = True
        if curruser.groups.filter(name="worker"):
            entered = "worker"
            staff = True
        if curruser.groups.filter(name="invest-manager"):
            entered = "invest-manager"
            staff = True
        if staff is not True:
            return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        print ("Error getting region. Contact admin or developer...")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    _print = urldata.get('print', None)
    if _print != None:
        _print = _print.pop()
    contact = ""
    if _id != None:
        _id = _id.pop()
        try:
            contact = tInvestorContacts.objects.get(id = _id)
        except:
            pass

        if contact.school != userSch.school:
            if not (entered == "chief" and userSch.school.city == u"Київ"):
                return render(request, "nopermission.html", {"name":curruser,})

    if _print == "true":
        return render(request, "info/printinvcontact.html", {"name":curruser,
                                                  "entered":entered,
                                                  "contact":contact,
                                                  })

    return render(request, "info/infoinvcontact.html", {"name":curruser,
                                          "entered":entered,
                                          "contact":contact,
                                          })

def infomentor(request):
    curruser = 0
    entered = 0
    staff = False
    curruserName = request.session.get("curUser", False)
    if curruserName == None:
        return redirect("index")
    if curruserName:
        curruser = User.objects.get(username=curruserName)
        if curruser.groups.filter(name="chief"):
            entered = "chief"
            staff = True
        if curruser.groups.filter(name="worker"):
            entered = "worker"
            staff = True
        if curruser.groups.filter(name="invest-manager"):
            entered = "invest-manager"
            staff = True
        if staff is not True:
            return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        print ("Error getting region. Contact admin or developer...")


    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    _print = urldata.get('print', None)
    if _print != None:
        _print = _print.pop()
    mentor = ""
    projects=[]

    if _id != None:
        _id = _id.pop()
        try:
            mentor = tMentor.objects.get(id = _id)
            projects = tMentoproj.objects.filter(mentorID = mentor)
        except:
            pass

        if mentor.school != userSch.school:
            if not (entered == "chief" and userSch.school.city == u"Київ"):
                return render(request, "nopermission.html", {"name":curruser,})

    if _print == "true":
        return render(request, "info/printmentor.html", {"name":curruser,
                                                  "entered":entered,
                                                  "mentor":mentor,
                                                  "projects":projects,
                                                  })
    return render(request, "info/infomentor.html", {"name":curruser,
                                          "entered":entered,
                                          "mentor":mentor,
                                          "projects":projects,
                                          })

def infoevent(request):
    curruser = 0
    entered = 0
    staff = False
    curruserName = request.session.get("curUser", False)
    if curruserName == None:
        return redirect("index")
    if curruserName:
        curruser = User.objects.get(username=curruserName)
        if curruser.groups.filter(name="chief"):
            entered = "chief"
            staff = True
        if curruser.groups.filter(name="worker"):
            entered = "worker"
            staff = True
        if curruser.groups.filter(name="invest-manager"):
            entered = "invest-manager"
            staff = True
        if staff is not True:
            return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        print ("Error getting region. Contact admin or developer...")


    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    _print = urldata.get('print', None)
    if _print != None:
        _print = _print.pop()
    event = ""
    projects=[]

    if _id != None:
        _id = _id.pop()
        try:
            event = tActivities.objects.get(id = _id)
            projects = tActProj.objects.filter(eventID = event)
        except:
            pass

        if event.school != userSch.school:
            if not (entered == "chief" and userSch.school.city == u"Київ"):
                return render(request, "nopermission.html", {"name":curruser,})

    if _print == "true":
        return render(request, "info/printevent.html", {"name":curruser,
                                                  "entered":entered,
                                                  "event":event,
                                                  "projects":projects,
                                                  })
    return render(request, "info/infoevent.html", {"name":curruser,
                                          "entered":entered,
                                          "event":event,
                                          "projects":projects,
                                          })

def infovisitors(request):
    curruser = 0
    entered = 0
    staff = False
    curruserName = request.session.get("curUser", False)
    if curruserName == None:
        return redirect("index")
    if curruserName:
        curruser = User.objects.get(username=curruserName)
        if curruser.groups.filter(name="chief"):
            entered = "chief"
            staff = True
        if curruser.groups.filter(name="worker"):
            entered = "worker"
            staff = True
        if curruser.groups.filter(name="invest-manager"):
            entered = "invest-manager"
            staff = True
        if staff is not True:
            return redirect("index")
    userSch = Object()
    userSch.school = Object()
    userSch.school.city = ""
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        print ("Error getting region. Contact admin or developer...")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    page = urldata.get('page', None)
    if page != None:
        page = int(page.pop())
    investor = ""
    queryListCount = 0
    if _id != None:
        _id = _id.pop()
        try:
            investor = tInvestor.objects.get(id = _id)
        except:
            pass

        if investor.school != None:
            if investor.school != userSch.school:
                if not (entered == "chief" and userSch.school.city == u"Київ"):
                    return render(request, "nopermission.html", {"name":curruser,})
        if investor.user != None:
            if curruser != investor.user:
                return render(request, "nopermission.html", {"name":curruser,
                                                             "message":investor.message})
    start = (page - 1) * 10
    end = 10 * page
    queryList = tVisitors.objects.filter(investorID = investor, )[start:end]
    queryListCount = len(queryList)
    return render(request, "info/infovisitors.html", {"name":curruser,
                                          "entered":entered,
                                          "investor":investor,
                                          "page":page,
                                          "prevpage":int(page-1),
                                          "nextpage":int(page+1),
                                          "queryList":queryList,
                                          "queryListCount":queryListCount,
                                          "staff":staff,
                                          })


def signadd(request):
    """Worker validation"""
    entered = 0
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
    if entered != "worker":
        return redirect("index")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    _entity = urldata.get('entity', None)
    redir = urldata.get('redir', None)
    if redir != None:
        redir = redir.pop()
    result = "Событие добавлено!"
    added = False

    if _id != None:
        _id = _id.pop()
        if _entity is not None:
            _entity = _entity.pop()

        if request.method == "POST":
            project = tProject.objects.get(id = _id)
            if _entity == "act":
                try:
                    act = tActivities.objects.create(projectID=project, date = datetime.strptime(
                        request.POST.get("tbDate", datetime.now().date().__format__('%d.%m.%Y').__str__()), "%d.%m.%Y"))
                    act.title = request.POST.get("tbTitle", "")
                    act.save()
                    added = True
                except:
                    pass

            if _entity == "stat":
                stat = tStatus.objects.create(projectID=project, date=datetime.strptime(
                    request.POST.get("tbDate", datetime.now().date().__format__('%d.%m.%Y, %H:%M').__str__()), "%d.%m.%Y, %H:%M"))
                stat.title = request.POST.get("tbTitle", "")
                stat.save()
                added = True
                result = "Статус добавлен!"

        if redir == "true":
            return redirect("/infoproject?id="+_id)


    return render(request, "adding/signadd.html", {"name":curruser,
                                          "entered":entered,
                                          "id":_id,
                                          "added":added,
                                          "result":result,
                                          "entity":_entity,
                                          })

def eventadd(request):
    """Worker validation"""
    entered = 0
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
    if entered != "worker":
        return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        print ("Error getting region. Contact admin or developer...")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    projid = urldata.get('projid', None)
    redir = urldata.get('redir', None)
    if redir != None:
        redir = redir.pop()
    if projid != None:
        projid = projid.pop()
    result = "Захід додано!"
    added = False

    if request.method == "POST":
        act = tActivities.objects.create(school = userSch.school, date = datetime.strptime(
            request.POST.get("tbDate", datetime.now().date().__format__('%d.%m.%Y').__str__()), "%d.%m.%Y"))
        act.title = request.POST.get("tbTitle", "")
        act.save()
        added = True
        if projid is not None:
            newBound = tActProj.objects.create(eventID=act, projectID=tProject.objects.get(id = projid))
            newBound.save()


    if redir == "true":
        return redirect("/")


    return render(request, "adding/eventadd.html", {"name":curruser,
                                          "entered":entered,
                                          "id":_id,
                                          "added":added,
                                          "result":result,
                                          })

def addfile(request):
    """Worker validation"""
    entered = 0
    curruser = 0
    id = None
    addurl = ""
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
    if entered != "worker":
        return redirect("index")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    _entity = urldata.get('entity', None)
    addurl = urldata.get('addurl', "")
    if addurl != "":
        addurl = addurl.pop()
    result = "Файл додан!"
    added = False

    if _id != None:
        _id = _id.pop()
        if _entity is not None:
            _entity = _entity.pop()

        if _entity == "startuper":
            startuper = tStartuper.objects.get(id = _id)
            if request.method == "POST":
                if addurl == "":
                    form = FileUploadedForm(request.POST, request.FILES)
                    if form.is_valid():
                        input_file = request.FILES.get('loadFile')
                        if input_file != None:
                            if input_file.size < 500000:
                                doc = tDoc.objects.create(startuperID=startuper, date = datetime.now().date())
                                doc.document = input_file
                                tmpFName = input_file.name.split(".")[0]
                                doc.title = tmpFName
                                doc.save()
                                added = True
                            else:
                                result = "Розмір Файлу більше 5мб!"
                else:
                    someUrl = tDoc.objects.create(startuperID=startuper,)
                    someUrl.title = request.POST.get("tbTitle")
                    someUrl.url = request.POST.get("tbUrl")
                    someUrl.save()
                    added = True
                    result = "Посилання додано!"

        if _entity == "project":
            project = tProject.objects.get(id = _id)
            if request.method == "POST":
                if  addurl == "":
                    form = FileUploadedForm(request.POST, request.FILES)
                    if form.is_valid():
                        input_file = request.FILES.get('loadFile')
                        if input_file != None:
                            if input_file.size < 500000:
                                file = tAddInfoProj.objects.create(projectID=project,)
                                file.file = input_file
                                file.text = input_file.name.split(".")[0]
                                file.save()
                                added = True
                            else:
                                result = "Розмір Файлу більше 5мб!"
                else:
                    someUrl = tAddInfoProj.objects.create(projectID=project,)
                    someUrl.text = request.POST.get("tbTitle")
                    someUrl.url = request.POST.get("tbUrl")
                    someUrl.save()
                    added = True
                    result = "Посилання додано!"

        if _entity == "investor":
            investor = tInvestor.objects.get(id = _id)
            if request.method == "POST":
                if addurl == "":
                    form = FileUploadedForm(request.POST, request.FILES)
                    if form.is_valid():
                        input_file = request.FILES.get('loadFile')
                        if input_file != None:
                            if input_file.size < 500000:
                                file = tAddInfoInv.objects.create(investorID=investor,)
                                file.file = input_file
                                file.text = input_file.name.split(".")[0]
                                file.save()
                                added = True
                            else:
                                result = "Розмір Файлу більше 5мб!"
                else:
                    someUrl = tAddInfoInv.objects.create(investorID=investor,)
                    someUrl.text = request.POST.get("tbTitle")
                    someUrl.url = request.POST.get("tbUrl")
                    someUrl.save()
                    added = True
                    result = "Посилання додано!"

    return render(request, "adding/addfile.html", {"name":curruser,
                                          "entered":entered,
                                          "id":_id,
                                          "added":added,
                                          "addurl":addurl,
                                          "result":result,
                                          "entity":_entity,
                                          })



def startuperstoproject(request):
    """Worker validation"""
    entered = 0
    curruser = 0
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
    if entered != "worker":
        return redirect("index")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    if _id != None:
        _id = _id.pop()
    page = urldata.get('page', None)
    if page != None:
        page = int(page.pop())
    entity = urldata.get('entity', None)
    if entity != None:
        entity = entity.pop()
    queryList = []
    queryListCount = 0
    added = False
    blackIDs=[]
    project = Object()
    startuper = Object()
    val = request.POST.get("tbQSch", "")

    if entity == "project":
        project = tProject.objects.get(id = _id)

        if _id != None:
            if request.method == "POST":
                valToAdd = request.POST.getlist("cbChoosed", None)
                if valToAdd != []:
                    for item in valToAdd:
                        startuper = tStartuper.objects.get(id = item)
                        _role = request.POST.get("tbRole"+str(item),None)
                        if list(tTeam.objects.filter(startuperID = startuper, projectID = project)) == [] :
                            tmp = tTeam.objects.create(startuperID = startuper, projectID = project, role = _role)
                            tmp.save()
                    redir = urldata.get('redirect', None)
                    if redir != None:
                        redir = redir.pop()
                    if redir == "true":
                        return  redirect("/infoproject?id="+_id )

        start=(page-1)*10
        end =10*page
        curPrjMembersIDs = tTeam.objects.filter(projectID = project)
        for item in curPrjMembersIDs:
            blackIDs.append(item.startuperID.id)
        queryList = tStartuper.objects.exclude(id__in = blackIDs,).filter(surname__icontains = val)[start:end]
        queryListCount = len(tStartuper.objects.exclude(id__in = blackIDs,).filter(surname__icontains = val)[start:end+1])



    if entity == "startuper":
        startuper = tStartuper.objects.get(id = _id)

        if _id != None:
            if request.method == "POST":
                valToAdd = request.POST.getlist("cbChoosed", None)
                if valToAdd != []:
                    for item in valToAdd:
                        project = tProject.objects.get(id = item)
                        _role = request.POST.get("tbRole"+str(item),None)
                        if list(tTeam.objects.filter(startuperID = startuper, projectID = project)) == [] :
                            tmp = tTeam.objects.create(startuperID = startuper, projectID = project, role = _role)
                            tmp.save()
                    redir = urldata.get('redirect', None)
                    if redir != None:
                        redir = redir.pop()
                    if redir == "true":
                        return redirect("/infostartuper?id="+_id)

        start=(page-1)*10
        end =10*page
        curPrjMembersIDs = tTeam.objects.filter(startuperID = startuper)
        for item in curPrjMembersIDs:
            blackIDs.append(item.projectID.id)
        queryList = tProject.objects.exclude(id__in = blackIDs,).filter(title__icontains = val)[start:end]
        queryListCount = len(tProject.objects.exclude(id__in = blackIDs,).filter(title__icontains = val)[start:end+1])

    schVal = request.POST.get("tbQSch", "")
    return render(request, "adding/startupertoproject.html", {
                                          "name":curruser,
                                          "entered":entered,
                                          "entity":entity,
                                          "id":_id,
                                          "queryList":queryList,
                                          "queryListCount":queryListCount,
                                          "page":page,
                                          "prevpage":int(page-1),
                                          "nextpage":int(page+1),
                                          "added":added,
                                          "project":project,
                                          "startuper":startuper,
                                          "schVal":schVal,
                                          })

def mentorstoproject(request):
    """Worker validation"""
    entered = 0
    curruser = 0
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
    if entered != "worker":
        return redirect("index")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    if _id != None:
        _id = _id.pop()
    page = urldata.get('page', None)
    if page != None:
        page = int(page.pop())
    entity = urldata.get('entity', None)
    if entity != None:
        entity = entity.pop()
    queryList = []
    queryListCount = 0
    added = False
    blackIDs=[]
    project = Object()
    startuper = Object()
    val = request.POST.get("tbQSch", "")

    if entity == "project":
        project = tProject.objects.get(id = _id)

        if _id != None:
            if request.method == "POST":
                valToAdd = request.POST.getlist("cbChoosed", None)
                if valToAdd != []:
                    for item in valToAdd:
                        mentor = tMentor.objects.get(id = item)
                        _date = Object
                        _date.date = request.POST.get("tbDate"+str(item), datetime.now().date())
                        _date.time = datetime.now().time().__format__("%H:%M")
                        if list(tMentoproj.objects.filter(mentorID = mentor, projectID = project)) == [] :
                            tmp = tMentoproj.objects.create(mentorID = mentor, projectID = project, date = datetime.strptime(_date.date.__str__()+", "+_date.time.__str__(), "%d.%m.%Y, %H:%M"))
                            tmp.save()
                    redir = urldata.get('redirect', None)
                    if redir != None:
                        redir = redir.pop()
                    print redir
                    if redir == "true":
                        return redirect("/infoproject?id="+_id)

        start=(page-1)*10
        end =10*page
        curPrjMembersIDs = tMentoproj.objects.filter(projectID = project)
        for item in curPrjMembersIDs:
            blackIDs.append(item.mentorID.id)
        queryList = tMentor.objects.exclude(id__in = blackIDs,).filter(surname__icontains = val)[start:end]
        queryListCount = len(tMentor.objects.exclude(id__in = blackIDs,).filter(surname__icontains = val)[start:end+1])

    schVal = request.POST.get("tbQSch", "")
    return render(request, "adding/mentortoproject.html", {
                                          "name":curruser,
                                          "entered":entered,
                                          "entity":entity,
                                          "id":_id,
                                          "queryList":queryList,
                                          "queryListCount":queryListCount,
                                          "page":page,
                                          "prevpage":int(page-1),
                                          "nextpage":int(page+1),
                                          "added":added,
                                          "project":project,
                                          "startuper":startuper,
                                          "schVal":schVal,
                                          })

def eventtoproj(request):
    """Worker validation"""
    entered = 0
    curruser = 0
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
    if entered != "worker":
        return redirect("index")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    if _id != None:
        _id = _id.pop()
    page = urldata.get('page', None)
    if page != None:
        page = int(page.pop())
    entity = urldata.get('entity', None)
    if entity != None:
        entity = entity.pop()
    queryList = []
    queryListCount = 0
    added = False
    blackIDs=[]
    project = Object()
    event = Object()
    val = request.POST.get("tbQSch", "")

    if entity == "project":
        project = tProject.objects.get(id = _id)

        if _id != None:
            if request.method == "POST":
                valToAdd = request.POST.getlist("cbChoosed", None)
                if valToAdd != []:
                    for item in valToAdd:
                        event = tActivities.objects.get(id = item)
                        if list(tActProj.objects.filter(eventID = event, projectID = project)) == [] :
                            tmp = tActProj.objects.create(eventID = event, projectID = project)
                            tmp.save()
                    redir = urldata.get('redirect', None)
                    if redir != None:
                        redir = redir.pop()
                    print redir
                    if redir == "true":
                        return redirect("/infoproject?id="+_id)

        start=(page-1)*10
        end =10*page
        curPrjMembersIDs = tActProj.objects.filter(projectID = project)
        for item in curPrjMembersIDs:
            blackIDs.append(item.eventID.id)
        queryList = tActivities.objects.exclude(id__in = blackIDs,).filter(title__icontains = val)[start:end]
        queryListCount = len(tActivities.objects.exclude(id__in = blackIDs,).filter(title__icontains = val)[start:end+1])

    if entity == "event":
        event = tActivities.objects.get(id=_id)

        if _id != None:
            if request.method == "POST":
                valToAdd = request.POST.getlist("cbChoosed", None)
                if valToAdd != []:
                    for item in valToAdd:
                        project = tProject.objects.get(id=item)
                        if list(tActProj.objects.filter(eventID=event, projectID=project)) == []:
                            tmp = tActProj.objects.create(eventID=event, projectID=project)
                            tmp.save()
                    redir = urldata.get('redirect', None)
                    if redir != None:
                        redir = redir.pop()
                    print redir
                    if redir == "true":
                        return redirect("/infoevent?id=" + _id)

        start = (page - 1) * 10
        end = 10 * page
        curPrjMembersIDs = tActProj.objects.filter(eventID=event)
        for item in curPrjMembersIDs:
            blackIDs.append(item.projectID.id)
        queryList = tProject.objects.exclude(id__in=blackIDs, ).filter(title__icontains=val)[start:end]
        queryListCount = len(tProject.objects.exclude(id__in=blackIDs, ).filter(title__icontains=val)[start:end+1])

    schVal = request.POST.get("tbQSch", "")
    return render(request, "adding/eventtoproj.html", {
                                          "name":curruser,
                                          "entered":entered,
                                          "entity":entity,
                                          "id":_id,
                                          "queryList":queryList,
                                          "queryListCount":queryListCount,
                                          "page":page,
                                          "prevpage":int(page-1),
                                          "nextpage":int(page+1),
                                          "added":added,
                                          "project":project,
                                          "event":event,
                                          "schVal":schVal,
                                          })


def invcontactsadd(request):
    """Worker validation"""
    entered = 0
    curruser = 0
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="invest-manager"):
                entered = "invest-manager"
    if entered != "invest-manager":
        return redirect("index")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    added = urldata.get('added', False)
    if added != False:
        added = added.pop()
    _id = urldata.get('id', None)
    if _id != None:
        _id = _id.pop()


    inputList = []
    resultList = []
    loaded = False
    investor = Object()
    if _id != None:
        investor = tInvestor.objects.get(id = _id)

        """Loading and getting data from excel file"""
        excelKeys = []
        excelList = []
        if request.method == 'POST':
            form = FileUploadedForm(request.POST, request.FILES)
            if form.is_valid():
                input_file = request.FILES.get('excelImport')
                if input_file != None:
                    tmpFName = input_file.name.split(".")
                    tmpFName = tmpFName.pop()
                    if tmpFName == "xlsx" or tmpFName == "xls":
                        wb = xlrd.open_workbook(file_contents=input_file.read())
                        wb_sheet = wb.sheet_by_index(0)
                        row = wb_sheet.row_values(0)
                        for item in row:
                            excelKeys.append(unicode(item).lower().replace(" ", ""))
                        for rownum in range(1, wb_sheet.nrows):
                            row = wb_sheet.row_values(rownum)
                            row.append(rownum)
                            excelList.append(row)

        """Adding data to froms & database"""
        if request.FILES.get('excelImport', False):
            inputList = fillFormsInvContacts(excelList, excelKeys)
            loaded = True

        else:
            for x in range(0, 1):
                tmpObj = Object()
                tmpObj.num = x + 1
                inputList.append(tmpObj)
                loaded = True

        if request.method == 'POST' and added == 'true':
            tmpList = request.POST.getlist('tbSurname')
            for item in tmpList:
                resultList.append(addInvContToDB(request, investor, request.POST.getlist('tbSurname').index(item)))

    return render(request, "adding/invcontactsadd.html", {
                                          "name":curruser,
                                          "entered":entered,
                                          "id":_id,
                                          "investor":investor,
                                          "inputList":inputList,
                                          "added":added,
                                          "loaded":loaded,
                                          "resultList":resultList,
                                          })

def investitions(request):
    """Worker validation"""
    entered = 0
    curruser = 0
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="invest-manager"):
                entered = "invest-manager"
    if entered != "invest-manager":
        return redirect("index")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    added = urldata.get('added', False)
    if added != False:
        added = added.pop()
    _id = urldata.get('id', None)
    if _id != None:
        _id = _id.pop()
    redir = urldata.get('redirect', None)
    if redir != None:
        redir = redir.pop()

    inputList=[]

    inputList = []
    resultList = []
    loaded = False
    projErr=""
    investor = Object()
    if _id != None:
        investor = tInvestor.objects.get(id = _id)
        if request.method == 'POST':
            try:
                investition = tInvestition.objects.create(
                    investorID = tInvestor.objects.get(id = _id),
                    projectID = tProject.objects.get(title = request.POST.get("tbProject", None)),
                    date = datetime.strptime(request.POST.get("tbDate", None), '%d.%m.%Y, %H:%M'),
                    type = request.POST.get("selType", None),
                    res = request.POST.get("tbRes", None),
                    sum = request.POST.get("tbSum", None),
                    descr = request.POST.get("taDescr", None),
                )
                investition.save()
                if redir == "true":
                    return  redirect("/infoinvestor?id="+_id )
            except:
                projErr="Такого проекта нет."
                pass

    projects = tProject.objects.all()
    return render(request, "adding/investitions.html", {
                                          "name":curruser,
                                          "entered":entered,
                                          "id":_id,
                                          "investor":investor,
                                          "inputList":inputList,
                                          "added":added,
                                          "resultList":resultList,
                                          "now":datetime.now().__format__('%d.%m.%Y, %H:%M'),
                                          "projects":projects,
                                          "projErr":projErr,
                                          })

def editstartuper(request):
    curruser = None
    entered = 0
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
    if entered != "worker":
        return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        print ("Error getting region. Contact admin or developer...")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    startuper = ""
    teams = []
    projects = []
    docs = []
    if _id != None:
        _id = _id.pop()
        startuper = tStartuper.objects.get(id = _id)
        teams = tTeam.objects.filter(startuperID = startuper)
        docs = tDoc.objects.filter(startuperID = startuper)
        if request.method == "POST":
            if request.POST.get("tbFIO", "") != "":
                fio = request.POST.get("tbFIO", None)
                fio = fio.split(" ")
                if len(fio)>=1:
                    startuper.surname = fio[0]
                else:
                    startuper.surname = ""
                if len(fio)>=2:
                    startuper.name = fio[1]
                else:
                    startuper.name = ""
                if len(fio)>=3:
                    startuper.midname = fio[2]
                else:
                    startuper.midname = ""
            if request.POST.get("tbTel", "") != "":
                startuper.phone = request.POST.get("tbTel", "")
            if request.POST.get("tbMail", "") != "":
                startuper.mail = request.POST.get("tbMail", "")
            startuper.fgrade = bool(request.POST.get("cbFgrade", False))
            startuper.sgrade = bool(request.POST.get("cbSgrade", False))
            if request.POST.get("tbFinYear", "") != "":
                startuper.finyear = request.POST.get("tbFinYear", False)
            form = FileUploadedForm(request.POST, request.FILES)
            if form.is_valid():
                input_file = request.FILES.get('fAvatar', None)
                if input_file != None:
                    tmpFName = input_file.name.split(".")
                    tmpFName = tmpFName.pop()
                    if input_file.size < 100000:
                        if tmpFName == "jpg" or tmpFName == "jepg" or tmpFName == "png" or tmpFName == "gif":
                            startuper.avatar = input_file
            startuper.save()
            for item in teams:
                if request.POST.get("tbRole"+str(item.id), "") != "":
                    item.role = request.POST.get("tbRole"+str(item.id), "")
                item.save()
            for item in teams:
                if request.POST.get("cbDel"+str(item.id), False):
                    item.delete()
            for item in docs:
                if request.POST.get("cbDelFile"+str(item.id), False):
                    item.delete()

            return redirect("/infostartuper?id="+_id)

        if startuper.school != userSch.school:
            if not (entered == "chief" and userSch.school.city == u"Київ"):
                return render(request, "nopermission.html", {"name":curruser,})

    return render(request, "editing/editstartuper.html", {"name":curruser,
                                          "entered":entered,
                                          "startuper":startuper,
                                          "teams":teams,
                                          "projects":projects,
                                          "docs":docs,
                                          })

def editproject(request):
    curruser = None
    entered = 0
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
    if entered != "worker":
        return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        print ("Error getting region. Contact admin or developer...")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    redir = urldata.get('redirect', None)
    if redir != None:
        redir = redir.pop()
    project = ""
    teams = []
    addInfo = []
    activities = []
    status = []
    mentors = []
    possibleLeaders = []
    mentorlist = []
    schoolList = []
    mentor = ""
    fioLead = ""
    errLead = ""
    currMent = ""
    errMent = ""
    tagstr = ""
    if _id != None:
        _id = _id.pop()
        project = tProject.objects.get(id = _id)

        teams = tTeam.objects.filter(projectID = project)
        for item in teams:
            if item.islead == True:
                fioLead = item.startuperID
        addInfo = tAddInfoProj.objects.filter(projectID = project)
        status = tStatus.objects.filter(projectID = project).order_by("date")
        activities = tActProj.objects.filter(projectID = project)
        mentors = tMentoproj.objects.filter(projectID = project).order_by("-date")
        possibleLeaders = tStartuper.objects.all().order_by("surname","name")
        mentorlist = tMentor.objects.all().order_by("surname","name")
        schoolList = tSchool.objects.all()

        tags = tKeyWordToProject.objects.filter(projectID=project)
        for item in tags:
            tagstr += item.word.word+" "
        if len(mentors) != 0:
            mentor = mentors[0]
            currMent = mentor.mentorID
        if request.method == "POST":
            mailLead = request.POST.get("tbLeader", "")
            if mailLead != "":
                leader = tStartuper.objects.filter(id = mailLead)
                if len(leader) == 0:
                    errLead = "Стартапер с такими ФИО не обнаружен."
                    redir = False
                else:
                    leader = leader[0]
                    if len(tTeam.objects.filter(projectID = project, startuperID = leader)) == 0:
                        prevLid = tTeam.objects.filter(projectID = project, islead = True)
                        if len(prevLid) != 0:
                            prevLid = prevLid[0]
                            prevLid.islead = False
                            prevLid.save()
                        newLead = tTeam.objects.create(projectID = project, startuperID = leader, role="Главный стартапер", islead = True)
                        newLead.save()
                    else:
                        prevLid = tTeam.objects.filter(projectID = project, islead = True)
                        if len(prevLid) != 0:
                            prevLid = prevLid[0]
                            prevLid.islead = False
                            prevLid.save()
                        tmpTeam = tTeam.objects.get(projectID = project, startuperID = leader)
                        tmpTeam.islead = True
                        tmpTeam.save()

            currMentMail = request.POST.get("tbMentor", "")
            if currMentMail != "":
                ment = tMentor.objects.filter(id = currMentMail)
                if len(ment) == 0:
                    errMent = "Ментор с такими ФИО не обнаружен."
                    redir = False
                else:
                    ment = ment[0]
                    newMent = tMentoproj.objects.create(mentorID = ment, projectID = project, date = datetime.now())
                    newMent.save()


            if len(request.POST.get("tbTags", "").replace(", ", " ").replace(",", " ").split(" ")) > 0:
                tmptags = request.POST.get("tbTags", "").replace(", ", " ").replace(",", " ").split(" ")
                tKeyWordToProject.objects.filter(projectID = project).delete()
                for item in tmptags:
                    keyword = tKeyWord.objects.get_or_create(word = item)
                    keyword = tKeyWord.objects.get(word = item)
                    tKeyWordToProject.objects.create(word = keyword, projectID = project)
            if request.POST.get("tbTitle", "") != "":
                project.title = request.POST.get("tbTitle", "")
            if request.POST.get("tbSector", "") != "":
                project.sector = request.POST.get("tbSector", "")
            if request.POST.get("tbFinScale", "") != "":
                project.financeScale = request.POST.get("tbFinScale", "")
            if request.POST.get("sbActive", "") != "":
                if request.POST.get("sbActive", "") == "True":
                    project.isactive = True
                else:
                    project.isactive = False
            if request.POST.get("tbDescr", "") != "":
                project.descr = request.POST.get("tbDescr", "")
            if request.POST.get("selType", "") != "":
                project.type = request.POST.get("selType", "")
            if request.POST.get("selIsReal", "") != "":
                project.isreal = request.POST.get("selIsReal", "")
            if request.POST.get("selSchool", "") != "":
                project.school = tSchool.objects.get(id = request.POST.get("selSchool", ""))

            project.save()
            for item in teams:
                if request.POST.get("tbRole"+str(item.id), "") != "":
                    item.role = request.POST.get("tbRole"+str(item.id), "")
                    item.save()
            for item in status:
                if request.POST.get("tbStatDate"+str(item.id), "") != "":
                    item.date = datetime.strptime(request.POST.get("tbStatDate"+str(item.id),  datetime.now().date().__str__()) + ", "+datetime.now().time().__format__("%H:%M").__str__(), '%d.%m.%Y, %H:%M')
                if request.POST.get("tbStatTit" + str(item.id), "") != "":
                    item.title = request.POST.get("tbStatTit"+str(item.id), "")
                item.save()
            for item in activities:
                if request.POST.get("tbActDate"+str(item.id), "") != "":
                    item.date = datetime.strptime(request.POST.get("tbActDate"+str(item.id),  datetime.now().date().__format__('%d.%m.%Y').__str__()), '%d.%m.%Y')
                if request.POST.get("tbActTit"+str(item.id), "") != "":
                    item.title = request.POST.get("tbActTit"+str(item.id), "")
                item.save()
            for item in mentors:
                if request.POST.get("tbMentDate"+str(item.id), "") != "":
                    item.date = datetime.strptime(request.POST.get("tbMentDate"+str(item.id),  datetime.now().date().__str__()) + ", "+datetime.now().time().__format__("%H:%M").__str__(), '%d.%m.%Y, %H:%M')
                item.save()

            for item in teams:
                if request.POST.get("cbStartDel"+str(item.id), False):
                    item.delete()
            for item in status:
                if request.POST.get("cbStatDel"+str(item.id), False):
                    item.delete()
            for item in activities:
                if request.POST.get("cbActDel"+str(item.id), False):
                    item.delete()
            for item in addInfo:
                if request.POST.get("cbAddInfoDel"+str(item.id), False):
                    item.delete()
            for item in mentors:
                if request.POST.get("cbMentDel"+str(item.id), False):
                    item.delete()

            if redir == "true":
                return redirect("/infoproject?id="+_id)

        if project.school != userSch.school:
            if not (entered == "chief" and userSch.school.city == u"Київ"):
                return render(request, "nopermission.html", {"name":curruser,})

    return render(request, "editing/editproject.html", {"name":curruser,
                                          "entered":entered,
                                          "project":project,
                                          "teams":teams,
                                          "addInfo":addInfo,
                                          "status":status,
                                          "activities":activities,
                                          "mentors":mentors,
                                          "mentor":mentor,
                                          "possibleLeaders":possibleLeaders,
                                          "mentorlist":mentorlist,
                                          "fioLead":fioLead,
                                          "errLead":errLead,
                                          "currMent":currMent,
                                          "errMent":errMent,
                                          "schoolList":schoolList,
                                          "tagstr":tagstr,
                                          })

def editinvestor(request):
    curruser = None
    entered = 0
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="invest-manager"):
                entered = "invest-manager"
    if entered != "invest-manager":
        return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        print ("Error getting region. Contact admin or developer...")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    investor = ""
    addInfo = []
    contacts = []
    investitions = []
    if _id != None:
        _id = _id.pop()
        investor = tInvestor.objects.get(id = _id)
        investitions = tInvestition.objects.filter(investorID = investor)
        addInfo = tAddInfoInv.objects.filter(investorID = investor)
        contacts = tInvestorContacts.objects.filter(investorID = investor)
        if request.method == "POST":
            if request.POST.get("tbInv", "") != "":
                investor.investor = request.POST.get("tbInv", "")
            if request.POST.get("taDescr", "") != "":
                investor.descr = request.POST.get("taDescr", "")
            tmpInvType = request.POST.get("selInvType","")
            if tmpInvType != "":
                if tmpInvType == "global":
                    investor.school = None
                    investor.user = None
                    investor.message = ""
                if tmpInvType == "local":
                    investor.school = userSch.school
                    investor.user = None
                    investor.message = ""
                if tmpInvType == "personal":
                    investor.school = None
                    investor.user = curruser
                    investor.message = request.POST.get("invTypeMsg","")

            investor.save()
            for item in investitions:
                if request.POST.get("tbInvsDate"+str(item.id), "") != "":
                    item.date = datetime.strptime(request.POST.get("tbInvsDate"+str(item.id),  datetime.now().date().__format__('%d.%m.%Y, %H:%M').__str__()), '%d.%m.%Y, %H:%M')
                if request.POST.get("tbInvsRes"+str(item.id), "") != "":
                    item.res = request.POST.get("tbInvsRes" + str(item.id), "")
                if request.POST.get("tbInvsSum"+str(item.id), "") != "":
                    item.sum = request.POST.get("tbInvsSum"+str(item.id), "")
                if request.POST.get("taInvsDescr"+str(item.id), "") != "":
                    item.descr = request.POST.get("taInvsDescr" + str(item.id), "")
                if request.POST.get("tbType"+str(item.id), "") != "":
                    item.type = request.POST.get("tbType" + str(item.id), "")
                item.save()
            for item in contacts:
                if request.POST.get("cbContDel"+str(item.id), False):
                    item.delete()
            for item in investitions:
                if request.POST.get("cbInvsDel"+str(item.id), False):
                    item.delete()
            for item in addInfo:
                if request.POST.get("cbAddInfoDel"+str(item.id), False):
                    item.delete()

            return redirect("/infoinvestor?id="+_id)

        if investor.school != None:
            if investor.school != userSch.school:
                if not (entered == "chief" and userSch.school.city == u"Київ"):
                    return render(request, "nopermission.html", {"name": curruser,})
        if investor.user != None:
            if curruser != investor.user:
                return render(request, "nopermission.html", {"name": curruser,
                                                             "message": investor.message})

    return render(request, "editing/editinvestor.html", {"name":curruser,
                                          "entered":entered,
                                          "investor":investor,
                                          "addInfo":addInfo,
                                          "contacts":contacts,
                                          "investitions":investitions,
                                          })

def editinvcontact(request):
    curruser = None
    entered = 0
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
    if entered != "worker":
        return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        print ("Error getting region. Contact admin or developer...")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    contact = ""
    addInfo = []
    contacts = []
    investitions = []
    if _id != None:
        _id = _id.pop()
        contact = tInvestorContacts.objects.get(id = _id)
        if request.method == "POST":
            if request.POST.get("tbFIO", "") != "":
                fio = request.POST.get("tbFIO", None)
                fio = fio.split(" ")
                if len(fio)>=1:
                    contact.surname = fio[0]
                else:
                    contact.surname = ""
                if len(fio)>=2:
                    contact.name = fio[1]
                else:
                    contact.name = ""
                if len(fio)>=3:
                    contact.midname = fio[2]
                else:
                    contact.midname = ""

            if request.POST.get("tbPhone", "") != "":
                contact.phone = request.POST.get("tbPhone", "")
            if request.POST.get("tbMail", "") != "":
                contact.mail = request.POST.get("tbMail", "")
            if request.POST.get("tbCompany", "") != "":
                contact.company = request.POST.get("tbCompany", "")
            if request.POST.get("tbPosition", "") != "":
                contact.position = request.POST.get("tbPosition", "")
            contact.save()

            return redirect("/infoinvcontact?id="+_id)

        if contact.school != userSch.school:
            if not (entered == "chief" and userSch.school.city == u"Київ"):
                return render(request, "nopermission.html", {"name":curruser,})

    return render(request, "editing/editinvcontact.html", {"name":curruser,
                                          "entered":entered,
                                          "contact":contact,
                                          "addInfo":addInfo,
                                          "contacts":contacts,
                                          "investitions":investitions,
                                          })

def editmentor(request):
    curruser = None
    entered = 0
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
    if entered != "worker":
        return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        print ("Error getting region. Contact admin or developer...")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    contact = ""
    mentor = []
    projects = []


    if _id != None:
        _id = _id.pop()
        mentor = tMentor.objects.get(id = _id)
        projects = tMentoproj.objects.filter(mentorID=mentor)
        if request.method == "POST":
            if request.POST.get("tbFIO", "") != "":
                fio = request.POST.get("tbFIO", None)
                fio = fio.split(" ")
                if len(fio)>=1:
                    mentor.surname = fio[0]
                else:
                    mentor.surname = ""
                if len(fio)>=2:
                    mentor.name = fio[1]
                else:
                    mentor.name = ""
                if len(fio)>=3:
                    mentor.midname = fio[2]
                else:
                    mentor.midname = ""
            if request.POST.get("tbPhone", "") != "":
                mentor.phone = request.POST.get("tbPhone", "")
            if request.POST.get("tbMail", "") != "":
                mentor.mail = request.POST.get("tbMail", "")
            mentor.save()

            for item in projects:
                if request.POST.get("tbProjDate"+str(item.id), "") != "":
                    item.date = datetime.strptime(request.POST.get("tbProjDate"+str(item.id),  datetime.now().date().__str__()) + ", "+datetime.now().time().__format__("%H:%M").__str__(), '%d.%m.%Y, %H:%M')
                item.save()

            for item in projects:
                if request.POST.get("cbProjDel"+str(item.id), False):
                    item.delete()

            return redirect("/infomentor?id="+_id)

        if mentor.school != userSch.school:
            if not (entered == "chief" and userSch.school.city == u"Київ"):
                return render(request, "nopermission.html", {"name":curruser,})


    return render(request, "editing/editmentor.html", {"name":curruser,
                                          "entered":entered,
                                          "contact":contact,
                                          "mentor":mentor,
                                          "projects":projects,
                                          })

def editevent(request):
    curruser = None
    entered = 0
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
    if entered != "worker":
        return redirect("index")
    userSch = Object()
    userSch.school = Object()
    try:
        userSch = tUserSch.objects.get(user=curruser)
    except:
        print ("Error getting region. Contact admin or developer...")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    _id = urldata.get('id', None)
    contact = ""
    event = []
    projects = []


    if _id != None:
        _id = _id.pop()
        event = tActivities.objects.get(id = _id)
        projects = tActProj.objects.filter(eventID=event)
        if request.method == "POST":
            if request.POST.get("tbTitle", "") != "":
                event.title = request.POST.get("tbTitle", "")
            if request.POST.get("tbDate", "") != "":
                event.date = datetime.strptime(request.POST.get("tbDate", datetime.now().date().__format__('%d.%m.%Y').__str__()), "%d.%m.%Y")
            event.save()

            for item in projects:
                if request.POST.get("cbActDel"+str(item.id), False):
                    item.delete()

            return redirect("/infoevent?id="+_id)

        if event.school != userSch.school:
            if not (entered == "chief" and userSch.school.city == u"Київ"):
                return render(request, "nopermission.html", {"name":curruser,})


    return render(request, "editing/editevent.html", {"name":curruser,
                                          "entered":entered,
                                          "contact":contact,
                                          "event":event,
                                          "projects":projects,
                                          })


def tagadd(request):
    """Worker validation"""
    entered = 0
    curruser = None
    id = None
    try:
        id = request.session["curUser"]
    finally:
        if id == None:
            return redirect("index")
        else:
            curruserName = request.session.get("curUser", False)
            curruser = User.objects.get(username=curruserName)
            if curruser.groups.filter(name="worker"):
                entered = "worker"
    if entered != "worker":
        return redirect("index")

    """Getting data from url"""
    path = urlparse(request.get_full_path())
    query = path.query
    urldata = parse_qs(query)
    obj = urldata.get('obj', None)
    if obj != None:
        obj = obj.pop()
    added = urldata.get('added', False)
    if added != False:
        added = added.pop()
    startuperID = urldata.get('startuperID', False)
    if startuperID != False:
        startuperID = startuperID.pop()
    projectID = urldata.get('projectID', False)
    if projectID != False:
        projectID = projectID.pop()


    """Adding data to database"""
    tag = request.POST.get("tbTag", None)
    tags = tKeyWord.objects.filter(word = tag)
    message = ""
    if request.method == "POST":
        if len(tags) == 0:
            newTag = tKeyWord.objects.create(word = tag)
            newTag.save()
            message = "Тэг '".decode("utf-8")+tag+("' добавлен!").decode("utf-8")
        else:
            message = "Тэг '".decode("utf-8")+tag+"' уже существует в базе данных.".decode("utf-8")


    return render(request, "adding/tagadd.html", {"obj": obj,
                                        "name":curruser,
                                        "entered":entered,
                                        "message":message,
                                        })
