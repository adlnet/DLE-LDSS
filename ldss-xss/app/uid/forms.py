from django import forms
from .models import Provider # Import Neo4j models directly

class ProviderForm(forms.ModelForm):
    name = forms.CharField(max_length=255)

    def save(self):
        name = self.cleaned_data['name']
        provider = Provider.create_provider(name)
        provider.save()
        return provider

    class Meta:
        model = Provider
        fields = ['name'] # UID is self generated

# Search Forms
class SearchForm(forms.Form):
    search_term = forms.CharField(max_length=255, required=True, label="Search Term")
    search_type = forms.ChoiceField(
        choices=[
            ('alias', 'Search by Alias'),
            ('definition', 'Search by Definition'),
            ('context', 'Search by Context'),
        ], 
        required=True, 
        label="Search Type"
    )
    context = forms.CharField(label='Context', required=False, max_length=255)
