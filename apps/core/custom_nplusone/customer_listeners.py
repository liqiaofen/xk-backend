from nplusone.core.listeners import Message, LazyListener, EagerListener


class CustomMessage(Message):
    def __init__(self, model, field, method, url):
        self.url = url
        self.method = method
        super(CustomMessage, self).__init__(model, field)

    @property
    def message(self):
        return self.formatter.format(
            label=self.label,
            model=self.model.__name__,
            field=self.field,
            method=self.method,
            url=self.url
        )


class CustomLazyLoadMessage(CustomMessage):
    label = 'n_plus_one'
    formatter = '{method} {url};Potential n+1 query detected on `{model}.{field}`'


class CustomEagerLoadMessage(CustomMessage):
    label = 'unused_eager_load'
    formatter = '{method} {url};Potential unnecessary eager load detected on `{model}.{field}`'


class CustomLazyListener(LazyListener):
    def setup(self, **kwargs):
        self.request = kwargs.get('request', None)
        super(CustomLazyListener, self).setup()

    def handle_lazy(self, caller, args=None, kwargs=None, context=None, ret=None,
                    parser=None):
        model, instance, field = parser(args, kwargs, context)
        if instance in self.loaded and instance not in self.ignore:
            url = self.request.path if self.request else ''
            message = CustomLazyLoadMessage(model, field, self.request.method, url)
            self.parent.notify(message)


class CustomEagerListener(EagerListener):
    def setup(self, **kwargs):
        self.request = kwargs.get('request', None)
        super(CustomEagerListener, self).setup()

    def log_eager(self):
        self.tracker.prune([each for each in self.touched if each])
        for model, field in self.tracker.unused:
            url = self.request.path if self.request else ''
            message = CustomEagerLoadMessage(model, field, self.request.method, url)
            self.parent.notify(message)


custom_listeners = {
    'lazy_load': CustomLazyListener,
    'eager_load': CustomEagerListener,
}
