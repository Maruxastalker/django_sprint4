from django import forms
from django.core.mail import send_mail
from django.core.exceptions import ValidationError

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)

    def clean(self):
        super().clean()
        text = self.cleaned_data.get('text', '')
        if text and len(text.split()) == 1:
            send_mail(
                subject='Однословное сообщение',
                message=f'Юзер опубликовал однословное сообщение: "{text}"!',
                from_email='birthday_form@acme.not',
                recipient_list=['admin@acme.not'],
                fail_silently=True,
            )
            raise ValidationError(
                'Сообщение должно содержать более одного слова. '
            )
