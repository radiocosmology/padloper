from functools import wraps
from _permissions import check_permission

def authenticated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # get the class name
        class_name = func.__qualname__.split('.')[0]

        # get the method name
        method_name = func.__name__
       
        # get the permissions
        kw_permissions = kwargs.get('permissions')
        check_permission(kw_permissions, class_name, method_name)
        return func(*args, **kwargs)
    return wrapper


# example usage
# class MyClass:
#     @classmethod
#     @authenticated
#     def my_class_method(cls, permissions=None):
#         # Authentication happens before this point
#         pass

# Usage
# MyClass.my_class_method(permissions=['Hello'])
