from django import forms


class addForm(forms.Form):
    path_to_file = forms.FileField(label="Загружаемый файл", required=True)


class textForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 20, "cols": 160}),
        label="Текст"
    )


class filterForm(forms.Form):
    selected_label = forms.ChoiceField(
        choices=(("All", "Все"), ("Develop", "Разработка"), ("Other", "Статьи")),
        label="Фильтрация по категории",
        required=False,
        initial="All",
    )
    sorting = forms.ChoiceField(
        choices=((0, "Сначала более новые"), (1, "Сначала более старые")),
        initial=0,
        label="Сортировка по дате",
    )
