from rest_framework.permissions import BasePermission


class RbacPermission(BasePermission):
    @staticmethod
    def get_current_view_perms_map(view_cls):
        from rest_framework.viewsets import ModelViewSet, mixins, generics
        extends_class = view_cls.__mro__  # 获取当前类的继承链
        all_perms_map = {}

        if hasattr(view_cls, 'perms_map'):
            all_perms_map = view_cls.perms_map
            if not all_perms_map:
                # 有perms_map, 但是为{}， 当前视图不需要任何权限
                return {}
        if generics.GenericAPIView in extends_class:
            view_actions = []
            model_name = (view_cls.queryset.model.__name__).lower()
            app_name = (view_cls.queryset.model._meta.app_label).lower()
            # 所有继承了ModelViewSet的，都会生成默认权限
            if ModelViewSet in extends_class:
                view_actions = ['list', 'retrieve', 'create', 'update', 'destroy']
            else:
                mixins_map = {
                    'list': mixins.ListModelMixin, 'retrieve': mixins.RetrieveModelMixin,
                    'create': mixins.CreateModelMixin, 'update': mixins.UpdateModelMixin,
                    'destroy': mixins.DestroyModelMixin
                }
                for action, viewset in mixins_map.items():
                    if viewset in extends_class:
                        view_actions.append(action)
            perms_map = {action: f'{app_name}:{model_name}:{action}' for action in view_actions}
            if 'update' in view_actions:
                perms_map['partial_update'] = perms_map['update']
            #  视图默认权限+perms_map
            return dict(perms_map, **all_perms_map)
        return all_perms_map

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        """
        2.访问对象时，首先执行has_permission，
        当返回True时，再执行has_object_permission；
        当返回False时，has_object_permission不再执行
        """
        return True
