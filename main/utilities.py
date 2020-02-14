from datetime import datetime
from os.path import splitext
from django.template.loader import render_to_string
from django.core.signing import Signer

from bboard.settings import ALLOWED_HOSTS

# Создание цифровой подписи по средством класса Signer().
signer = Signer()


def send_activation_notification(user):
    """Функция отправки писем для активации учетной записи."""
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://localhost:8000'
    context = {'user': user, 'host': host,
               'sign':signer.sign(user.username)}
    subject = render_to_string('email/activation_letter_subject.txt',
                               context)
    body_text = render_to_string('email/activation_letter_body.txt',
                                 context)
    user.email_user(subject, body_text)


def get_timestamp_path(instance, filename):
    """Генерирует имена сохраняемых в модели файлов."""
    return '%s%s' % (datetime.now().timestamp(), splitext(filename)[1])


def send_new_comment_notification(comment):
    """Функция отправки уведобмелния о новом комментарии на почту."""
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://localhost:8000'
    author = comment.bb.author
    context = {'author': author, 'host': host, 'comment': comment}
    subject = render_to_string('email/new_comment_letter_subject.txt',
                               context)
    body_text = render_to_string('email/new_comment_letter_body.txt',
                                 context)
    author.email_user(subject, body_text)
