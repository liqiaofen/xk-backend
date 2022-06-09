from django.views.generic import TemplateView


class FrontendIndexView(TemplateView):
    template_name = "frontend/index.html"


class PersonalView(TemplateView):
    template_name = "frontend/account/personal.html"


class WriteView(TemplateView):
    template_name = "frontend/account/write.html"


class BackendIndexView(TemplateView):
    template_name = "backend/index.html"
