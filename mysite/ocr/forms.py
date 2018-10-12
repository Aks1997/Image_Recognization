from django import forms
class DocumentForm(forms.Form):
    docfile = forms.FileField(label='Select a file',)
    top_left_width = forms.IntegerField()
    top_left_height = forms.IntegerField()
    bottom_right_width = forms.IntegerField()
    bottom_right_height = forms.IntegerField()
