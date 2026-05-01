from django import forms


class SummarizeRequestForm(forms.Form):
    text = forms.CharField(max_length=20000, strip=True)
    mode = forms.ChoiceField(choices=(("paragraph", "paragraph"), ("bullet", "bullet")))
    length_ratio = forms.FloatField(min_value=0.15, max_value=0.85)
    keywords = forms.CharField(required=False, max_length=500)

    def clean_keywords(self) -> list[str]:
        raw = self.cleaned_data.get("keywords", "")
        tokens = [word.strip().lower() for word in raw.split(",") if word.strip()]
        uniq = []
        seen = set()
        for token in tokens:
            if token not in seen and token.isascii():
                uniq.append(token)
                seen.add(token)
            if len(uniq) == 12:
                break
        return uniq


class KeywordRequestForm(forms.Form):
    text = forms.CharField(max_length=20000, strip=True)
