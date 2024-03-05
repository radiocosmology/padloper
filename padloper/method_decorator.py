from functools import wraps

def method_name_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Pass the method name as an argument to the original function
        return func(*args, method_name=func.__name__, **kwargs)
    return wrapper

class MyClass:
    @classmethod
    @method_name_decorator
    def my_class_method(cls, *args, **kwargs):
        print("This is method:", kwargs['method_name'])

# Usage
MyClass.my_class_method()
