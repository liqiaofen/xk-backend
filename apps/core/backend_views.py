from django.views.generic import ListView


class BackendListBaseView(ListView):
    page_name = ''

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs['page_name'] = self.page_name
        return super(BackendListBaseView, self).get_context_data(object_list=None, **kwargs)
