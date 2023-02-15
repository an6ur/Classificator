from django.shortcuts import render
from main_app.models import Article
from django.http import HttpResponseRedirect
from .models import Svc_model
from django.db.utils import OperationalError
from main_app.forms import textForm

# Create your views here.


def train(request):
    global svc_model
    try:
        svc_model = Svc_model.createModelFromData(Article.objects.all())
    except OperationalError:
        render(
            request,
            "errors.html",
            {"text": "Отсутствует соединение с базой данных","code": 503},
            status=503
        )
    return render(request, "train_is_complete.html")


def classificate(request):
    if "svc_model" not in globals():
        global svc_model
        try:
            svc_model = Svc_model.loadModelFromFile()
        except FileNotFoundError:
            code = 503
            return render(
                request,
                "errors.html",
                {"text": "Сначала обучите классификатор","code": code},
                status=code
            )
    if request.method == "POST":
        text = request.POST.get("text")
        result = svc_model.classificateText(text)[0]
        res = {"Develop": "Разработка", "Other": "Другое"}
        return render(request, "predict_res.html", {"category": res[result]})
    else:
        form = textForm()
        return render(request, "text_predict.html", {"form": form})
