from django.shortcuts import render
from django.http import HttpResponseRedirect
from lxml import etree
from .forms import filterForm, textForm
from .models import (
    Article,
    Authors,
    Categories,
    KeyWords,
    OriginalAuthors,
)
from re import search
from django.db.utils import OperationalError
from django.core.paginator import Paginator

# Create your views here.


def redirect(request):
    return HttpResponseRedirect("articles/1")


def index(request, page = 0):
    selected_label = request.GET.get("selected_label", None)
    direction_sort = request.GET.get("sorting", 0)
    if direction_sort not in {"0", "1"}:
        direction_sort = 0
    sort_by = "date" if int(direction_sort) else "-date"
    try:
        if selected_label in {"Develop", "Other"}:
            category = "Разработка" if selected_label == "Develop" else "Другое"
            articles = Article.objects.filter(label=selected_label)
        else:
            articles = Article.objects.all()
            category = "Все"
        pages = Paginator(list(articles.order_by(sort_by)), 10)
        page_obj = pages.get_page(page)
        return render(
            request,
            "index.html",
            {
                "articles": page_obj,
                "count": articles.count(),
                "filter_form": filterForm,
                "category": category,
            },
        )
    except OperationalError:
        return render(
            request,
            "errors.html",
            {"text": "Отсутствует соединение с базой данных","code":503},
            status=503
        )


def parseFile(request, file):
    if not search("\.xml", file.name):
        return render(
            request,
            "errors.html",
            {"text": "Выбран файл с неподдерживаемым расширением","code":422},
            status=422
        )
    with open("schema.xsd", "r") as f:
        schema_root = etree.XML(f.read())
    parser = etree.XMLParser(schema=etree.XMLSchema(schema_root))
    try:
        tree = etree.parse(file, parser)
    except etree.XMLSyntaxError:
        return render(
            request,
            "errors.html",
            {"text": "Ошибка валидации xml-документа","code":422},
            status=422
        )
    root = tree.getroot()
    label = root.findall(".//label")[0].text
    title = root.findall(".//title")[0].text
    date = root.findall(".//date")[0].text.replace(",", "")
    link = root.findall(".//link")[0].text
    text = root.findall(".//text")[0].text
    original_authors = checksubElemsInDB(
        OriginalAuthors,
        [item.text for item in root.findall(".//original_author/item")],
    )
    key_words = checksubElemsInDB(
        KeyWords, [item.text for item in root.findall(".//key_words/item")]
    )
    categories = checksubElemsInDB(
        Categories, [item.text for item in root.findall(".//categories/item")]
    )
    authors = checksubElemsInDB(
        Authors, [item.text for item in root.findall(".//author/item")]
    )
    current_article = Article.objects.filter(title=title, text=text, date=date)
    if not current_article:
        current_article = Article(
            label=label, title=title, date=date, link=link, text=text
        )
        current_article.save()
        current_article.author.add(*[author.id for author in authors])
        current_article.key_words.add(*[key_word.id for key_word in key_words])
        current_article.categories.add(
            *[category.id for category in categories]
        )
        if original_authors:
            current_article.original_author.add(
                *[original_author.id for original_author in original_authors]
            )
            current_article.save()
    return HttpResponseRedirect("/")


def checksubElemsInDB(table, items: list) -> list:
    return [
        table.objects.get_or_create(name=item)[0]
        for item in items
        if item != ""
    ]


def saveFileInDB(request):
    if request.method == "POST":
        file = request.FILES.get("name", None)
        if file:
            try:
                return parseFile(request, file)
            except OperationalError:
                return render(
                    request,
                    "errors.html",
                    {"text": "Отсутствует соединение с базой данных","code": 503},
                    status=503
                )
        return render(
            request,
            "errors.html",
            {"text": "Файл не выбран","code": 422},
            status=422
        )
    else:
        return render(request, "add_form.html")


def removeArticle(request, id):
    if not id:
        return render(
            request,
            "errors.html",
            {"text": "Статья не выбрана","code": 422},
            status=422
        )
    if int(id) < 0:
        return render(
            request,
            "errors.html",
            {"text": "Выбран некорректный идентификатор статьи","code": 422},
            status=422
        )
    try:
        selected_article = Article.objects.get(id=id)
        if request.method == "POST":
            selected_article.delete()
            return render(request,
                "delete_res.html",
                {"title": selected_article.title}
            )
        else:
            return render(request,
                "delete_text_form.html",
                {"title": selected_article.title}
            )
    except OperationalError:
        return render(
            request,
            "errors.html",
            {"text": "Отсутствует соединение с базой данных","code": 503},
            status=503
        )


def getTextFromArticle(request, id):
    if not id:
        return render(
            request,
            "errors.html",
            {"text": "Статья не выбрана","code": 422},
            status=422
        )
    if int(id) < 0:
        return render(
            request,
            "errors.html",
            {"text": "Выбран некорректный идентификатор статьи","code": 422},
            status=422
        )
    try:
        article = Article.objects.get(id=id)
        if request.method == "POST":
            new_text = request.POST.get("text")
            article.text = new_text
            article.save()
            return HttpResponseRedirect("/")
        else:
            form = textForm(initial={"text": article.text})
            return render(request, "text_form.html", {"form": form})
    except OperationalError:
        return render(
            request,
            "errors.html",
            {"text": "Отсутствует соединение с базой данных","code": 503},
            status=503
        )
