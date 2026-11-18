"""
5-2 Activity CS 660
Malgorzata Debska

"""


def imperative_solution(numbers):
    """Use explicit steps, a loop, and a changing result list."""
    result = []  # Mutable state stores the answer as it is built.
    for number in numbers:  # Explicit control flow visits each integer.
        if number % 2 != 0:  # A conditional selects only odd integers.
            result.append(number ** 2)  # Update state with the squared value.
    return result  # Return a new list without modifying the input.


class NumberProcessor:
    """Encapsulate integer data and the behavior that processes it."""

    def __init__(self, numbers):
        self._numbers = list(numbers)  # Each object owns a copy of its data.

    def square_odds(self):
        # Expose processing through a method on the object.
        # A leading underscore marks internal data by convention in Python.
        result = []
        for number in self._numbers:
            if number % 2 != 0:
                result.append(number ** 2)
        return result  # Keep the object's stored data unchanged.


def functional_solution(numbers):
    """Compose filtering and mapping without changing the input."""
    # filter is a higher-order function; its lambda selects odd values.
    odd_numbers = filter(lambda number: number % 2 != 0, numbers)
    # map applies a pure transformation to each selected integer.
    squared_numbers = map(lambda number: number ** 2, odd_numbers)
    # Materialize the lazy pipeline into the required new list.
    return list(squared_numbers)


def main():
    numbers = list(range(1, 11))
    print("Programming Paradigm Comparison")
    print(f"Input:           {numbers}")
    print(f"Imperative:      {imperative_solution(numbers)}")
    print(f"Object-oriented: {NumberProcessor(numbers).square_odds()}")
    print(f"Functional:      {functional_solution(numbers)}")
    print(f"Input unchanged: {numbers}")


if __name__ == "__main__":
    main()
