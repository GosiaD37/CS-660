"""CS 660 Module 4-2 Activity — Malgorzata Debska

"""

import argparse
import json
import math
from pathlib import Path


# Part One, criteria 1: recursive calculation with invalid-input handling
def recursive_factorial(number):
   
    try:
        if isinstance(number, bool) or not isinstance(number, int):
            raise TypeError("Factorial requires an integer, excluding booleans.")
        if number < 0:
            raise ValueError("Factorial requires a nonnegative integer.")
        if number <= 1:  #prevents further recursive calls
            return 1
        return number * recursive_factorial(number - 1)
    except (TypeError, ValueError):
        raise  # preserve the specific error for the calling code to report
    except RecursionError as error:
        raise ValueError("Input exceeds Python's recursion capacity.") from error


# Part One, criteria 2 and 3: visit every scalar leaf in dictionaries/lists.
def collect_leaves(node, path="root"):
   
    try:
        leaves = []
        if isinstance(node, dict):
            for key, value in node.items():
                if not isinstance(key, str):
                    raise TypeError(f"Dictionary key at {path} must be a string.")
                leaves.extend(collect_leaves(value, f"{path}[{key!r}]"))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                leaves.extend(collect_leaves(value, f"{path}[{index}]"))
        elif node is None or isinstance(node, (str, bool, int, float)):
            if isinstance(node, float) and not math.isfinite(node):
                raise ValueError(f"Nonfinite number at {path}.")
            leaves.append((path, node)) 
        else:
            raise TypeError(f"Unsupported value at {path}: {type(node).__name__}.")
        return leaves
    except (TypeError, ValueError):
        raise  
    except RecursionError as error:
        raise ValueError(f"Structure is too deeply nested near {path}.") from error


def collect_planets(node, path="root"):
   
    try:
        planets = []
        if isinstance(node, dict):
            for key, value in node.items():
                child_path = f"{path}[{key!r}]"
                if key == "planets":
                    if not isinstance(value, list):
                        raise TypeError(f"Expected a planet list at {child_path}.")
                    for index, planet in enumerate(value):
                        record_path = f"{child_path}[{index}]"
                        if not isinstance(planet, dict):
                            raise TypeError(f"Expected a planet dictionary at {record_path}.")
                        for field in ("planet_id", "name", "mass_earth_masses"):
                            if field not in planet:
                                raise ValueError(f"Missing {field!r} at {record_path}.")
                        if not all(isinstance(planet[f], str) and planet[f]
                                   for f in ("planet_id", "name")):
                            raise TypeError(f"Planet ID/name must be nonempty text at {record_path}.")
                        mass = planet["mass_earth_masses"]
                        if isinstance(mass, bool) or not isinstance(mass, (int, float)):
                            raise TypeError(f"Invalid planet mass at {record_path}.")
                        if mass <= 0 or not math.isfinite(mass):
                            raise ValueError(f"Mass must be positive and finite at {record_path}.")
                        planets.append(planet)
                # continue searching so deeper planet lists are also found
                planets.extend(collect_planets(value, child_path))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                planets.extend(collect_planets(value, f"{path}[{index}]"))
        elif node is not None and not isinstance(node, (str, bool, int, float)):
            raise TypeError(f"Unsupported structure at {path}.")
        return planets
    except (TypeError, ValueError):
        raise
    except RecursionError as error:
        raise ValueError(f"Structure is too deeply nested near {path}.") from error


# Part Two, criterion 6: a custom function accepting another function
def transform_records(records, operation):
    if not callable(operation):
        raise TypeError("operation must be callable.")
    return [operation(record) for record in records]


def demonstrate_errors():
    
    print("\nHandled error examples:")
    examples = [
        ("Negative factorial", lambda: recursive_factorial(-2)),
        ("Noninteger factorial", lambda: recursive_factorial("five")),
        ("Boolean factorial", lambda: recursive_factorial(True)),
        ("Invalid nested leaf", lambda: collect_leaves({"nested": [set()]})),
        ("Malformed planet list", lambda: collect_planets({"planets": "invalid"})),
        ("Missing planet field", lambda: collect_planets({"planets": [{"name": "Example"}]})),
        ("Invalid operation", lambda: transform_records([], 42)),
    ]
    for label, operation in examples:
        try:
            operation()
        except (TypeError, ValueError) as error:
            print(f"  {label}: {error}")
        else:
            raise AssertionError(f"Expected an error: {label}")


def main():
    parser = argparse.ArgumentParser(description="Recursion and functional catalog utilities")
    parser.add_argument("catalog", nargs="?", type=Path,
                        default=Path(__file__).resolve().with_name("catalog.json"))
    args = parser.parse_args()
    try:
        with args.catalog.open(encoding="utf-8") as source:
            data = json.load(source)
        if not isinstance(data, dict) or not isinstance(data.get("astronomical_catalog"), dict):
            raise ValueError("Expected an astronomical_catalog dictionary at the root.")
        catalog = data["astronomical_catalog"]
        leaves = collect_leaves(data)
        planets = collect_planets(data)

        print(f"Catalog: {catalog.get('catalog_name', 'Unnamed')}")
        print(f"Factorial example: 5! = {recursive_factorial(5)}")
        print(f"\nAll {len(leaves)} scalar leaves (path = value):")
        for path, value in leaves:
            print(f"{path} = {json.dumps(value, ensure_ascii=False)}")

        # Criteria 4 and 5: lambda (anonymous function) with map (higher-order)
        uppercase_names = list(map(lambda planet: planet["name"].upper(), planets))
        print(f"\nPlanet records found: {len(planets)}")
        print("\nLambda + map, uppercase planet names:")
        print("\n".join(uppercase_names))

        # filter is another higher-order function; missing flags are not inferred
        habitable = list(filter(lambda planet: planet.get("habitable_zone") is True, planets))
        print("\nPlanets explicitly marked habitable_zone=true in the data:")
        for planet in habitable:
            print(f"  {planet['name']}")

        # Criterion 6: pass an anonymous transformation to our own function
        summaries = transform_records(planets, lambda planet: {
            "name": planet["name"],
            "mass_kg": planet["mass_earth_masses"] * 5.9722e24,
        })
        print("\nCustom higher-order function, approximate planet masses:")
        for summary in summaries:
            print(f"  {summary['name']}: {summary['mass_kg']:.3e} kg")
        demonstrate_errors()
    except (OSError, UnicodeError, ValueError, TypeError, RecursionError) as error:
        parser.exit(1, f"Unable to process catalog: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
