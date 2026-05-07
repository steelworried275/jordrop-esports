from django import forms
from django.utils.text import slugify
from .models import EditRequest, Page


class EditRequestForm(forms.ModelForm):
    proposed_content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 20, 'class': 'markdown-editor'}),
        label='Proposed content (Markdown)',
    )

    class Meta:
        model = EditRequest
        fields = ['proposed_content', 'edit_summary']
        widgets = {
            'edit_summary': forms.TextInput(attrs={'placeholder': 'Briefly describe your change…'}),
        }

    def __init__(self, *args, initial_content='', **kwargs):
        super().__init__(*args, **kwargs)
        if not self.data:  # Only pre-fill on GET, not POST
            self.fields['proposed_content'].initial = initial_content


class PageForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 20, 'class': 'markdown-editor'}),
        label='Content (Markdown)',
    )

    class Meta:
        model = Page
        fields = ['title', 'slug', 'is_published']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['slug'].help_text = 'Leave blank to auto-generate from title.'

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title', '')
        return slug or slugify(title)
