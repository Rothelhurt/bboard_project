from .models import SubRubric


# Создаем свой обработчик контекста, внутри которого создается переменна,
# содержащая список рубрик.
# Это сделано для того, чтобы не создавать эту переменную в каждом контроллере.
# UPD:
# В обработчик контекста добавленны параметры keyword и page.
# Они служат для корректного возврата поиска на страницу с объявлениями,
# на нужную страницу пагинатора и/или с заданым ключевым словом для поиска.
def bboard_context_processor(request):
    """Создает в контексте переменную rubrics, keyword и page."""
    context = {}
    context['rubrics'] = SubRubric.objects.all()
    context['keyword'] = ''
    context['all'] = ''
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            context['keyword'] = '?keyword=' + keyword
            context['all'] = context['keyword']
    if 'page' in request.GET:
        page = request.GET['page']
        if page != '1':
            if context['all']:
                context['all'] += '&page' + page
            else:
                context['all'] += '&page' + page
    return context
