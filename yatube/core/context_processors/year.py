from datetime import date


def year(request):
    """Добавляет переменную с текущим годом."""
    current_date = date.today()
    current_year = current_date.year
    return {
        'year': current_year
    }
