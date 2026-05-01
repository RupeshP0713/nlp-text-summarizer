import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .forms import KeywordRequestForm, SummarizeRequestForm
from .services import create_summary, extract_keywords


@require_GET
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "summarizer/index.html")


@require_POST
def summarize_api(request: HttpRequest) -> JsonResponse:
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "errors": {"body": [{"message": "Invalid JSON payload"}]}}, status=400)
    form = SummarizeRequestForm(payload)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors.get_json_data()}, status=400)

    result = create_summary(
        text=form.cleaned_data["text"],
        mode=form.cleaned_data["mode"],
        length_ratio=form.cleaned_data["length_ratio"],
        keywords=form.cleaned_data["keywords"],
    )
    return JsonResponse(
        {
            "ok": True,
            "summary": result.summary,
            "stats": {"words": result.stats.words, "sentences": result.stats.sentences},
        }
    )


@require_POST
def keywords_api(request: HttpRequest) -> JsonResponse:
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "errors": {"body": [{"message": "Invalid JSON payload"}]}}, status=400)
    form = KeywordRequestForm(payload)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors.get_json_data()}, status=400)
    return JsonResponse({"ok": True, "keywords": extract_keywords(form.cleaned_data["text"])})
