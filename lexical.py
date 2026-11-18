"""CS 680 Module Three -Activity 3-1 Typing and Scoping Exploration
Malgorzata Debska
"""
import platform
from contextlib import contextmanager


def typing_examples():
    print('PART ONE: TYPING')
    value = 10
    print(f'Rebinding before: {value!r} ({type(value).__name__})')
    value = 'ten'  # Legal: the name now refers to a string object.
    print(f'Rebinding after: {value!r} ({type(value).__name__})')
    cases = [('10 + "5"', lambda: 10 + '5'),
             ('"Count: " + 10', lambda: 'Count: ' + 10)]
    for label, operation in cases:
        try:
            operation()  # Unsupported operand types fail when executed.
        except TypeError as error:
            print(f'{label} -> {type(error).__name__}: {error}')
    print(f'Correct numeric addition: {10 + int("5")}')
    print(f'Correct text concatenation: {"Count: " + str(10)}')
    print(f'Allowed numeric coercion: 10 + 2.5 = {10 + 2.5}')
    annotated: int = 'ten'  # A static checker can flag this; Python permits it.
    print(f'Annotation alone: {annotated!r} ({type(annotated).__name__})')
    # Compile a type-invalid operation without executing it.
    bytecode = compile('10 + "5"', '<typing_demo>', 'eval')
    print('Compile 10 + "5": succeeds')
    try:
        eval(bytecode)  # Evaluating the compiled code triggers the error.
    except TypeError:
        print('Execute compiled expression: TypeError')


def example_1():
    x = 'outer'
    def inner():
        print(f'Inner sees: {x}')  
    inner()
    print(f'Outer has: {x}')


def example_2():
    x = 10
    def middle():
        x = 20  
        def inner():
            print(f'Inner sees: {x}')  
        inner()
        print(f'Middle has: {x}')
    middle()
    print(f'Outer has: {x}')  


def example_3():
    count = 0
    def increment():
        nonlocal count  
        count += 1
        return count
    def get_counter():
        def counter():
            return increment()  
        return counter
    my_counter = get_counter()
    print(my_counter())
    print(my_counter())
    print(count)  


def example_4():
    name = 'global'  
    def outer():
        name = 'outer'
        def inner():
            name = 'inner'  
            print(f'Inner: {name}')
        inner()
        print(f'Outer: {name}')
    outer()
    print(f'Global: {name}') 


class DynamicEnvironment:
    """Explicit active-call environments; Python itself stays lexical."""
    def __init__(self):
        self.frames = []

    @contextmanager
    def bind(self, **values):
        self.frames.append(values)  # Enter an active simulated call scope.
        try:
            yield
        finally:
            self.frames.pop()  # Restore the caller even after an exception.

    def lookup(self, name):
        for frame in reversed(self.frames):  # Newest active scope first.
            if name in frame:
                return frame[name]
        raise NameError(f'No active binding for {name!r}')


def compare_scoping():
    x = 10
    def inner():
        return x  # Lexically defined here: always use this enclosing x.
    def caller():
        x = 20  # Caller-local x is not a lexical ancestor of inner.
        return inner()
    print(f'Lexical direct call: {inner()}')
    print(f'Lexical through caller x=20: {caller()}')
    env = DynamicEnvironment()
    def dynamic_inner():
        return env.lookup('x')  # Explicitly search active simulated frames.
    def dynamic_caller():
        with env.bind(x=20):
            return dynamic_inner()  # Caller frame wins over outer x=10.
    with env.bind(x=10):
        print(f'Dynamic direct call: {dynamic_inner()}')
        print(f'Dynamic through caller x=20: {dynamic_caller()}')
        print(f'Dynamic after caller returns: {dynamic_inner()}')
    print(f'Dynamic frames after cleanup: {len(env.frames)}')


def main():
    print(f'Python {platform.python_version()} | {platform.python_implementation()}')
    typing_examples()
    print('\nPART TWO: ORIGINAL LEXICAL EXAMPLES')
    for number, function in enumerate((example_1, example_2, example_3, example_4), 1):
        print(f'Example {number}:')
        function()
    print('\nLEXICAL VS SIMULATED DYNAMIC SCOPING')
    compare_scoping()


if __name__ == '__main__':
    main()
