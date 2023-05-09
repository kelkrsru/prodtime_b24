from django import forms


class ReportDealsForm(forms.Form):
    """Форма для применения фильтра отчета по сделкам."""

    DATE_CODE_CHOICES = [
        ('ufCrm1652693659', 'Дата предоплаты'),
        ('ufCrm1679829767', 'Дата постоплаты'),
        ('ufCrm1679829674', 'Дата отправки КП'),
        ('closedate', 'Дата завершения сделки'),
    ]
    STAGES_DEALS_CHOICES = [
        ('A', 'Все'),
        ('P', 'В работе'),
        ('S', 'Выигранные'),
        ('F', 'Проигранные'),
    ]

    date_code = forms.ChoiceField(
        label='Выберите дату фильтра',
        choices=DATE_CODE_CHOICES,
    )

    start_date = forms.DateField(
        label='Начальная дата',
        widget=forms.widgets.DateInput(attrs={
            'type': 'date',
            'class': 'form-control datepicker-input',
        }),
        error_messages={'required': 'Укажите дату начала'}
    )

    end_date = forms.DateField(
        label='Конечная дата',
        widget=forms.widgets.DateInput(attrs={
            'type': 'date',
            'class': 'form-control datepicker-input',
        }),
        error_messages={'required': 'Укажите дату окончания'}
    )

    stages_deals = forms.ChoiceField(
        label='Выберите стадии сделки',
        choices=STAGES_DEALS_CHOICES,
    )

    show_parent_dir = forms.BooleanField(
        label='Показывать папку товара',
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if end_date < start_date:
            raise forms.ValidationError(
                "Конечная дата не может быть меньше начальной даты.")


