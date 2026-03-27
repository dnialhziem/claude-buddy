# Python Error Catalogue

Reference for identifying failure mechanisms in Step 1 of the Execution Flow.
Each entry includes: what it is, how to spot it, and the variable/state symptom.

> Sources: [Python Built-in Exceptions](https://docs.python.org/3/library/exceptions.html), [Python Data Model](https://docs.python.org/3/reference/datamodel.html), [Python FAQs](https://docs.python.org/3/faq/programming.html)

---

## Type Errors

| Error | Symptom | Example Trigger |
|-------|---------|-----------------|
| `TypeError: unsupported operand` | Mixing incompatible types in an operation | `"5" + 5` |
| `TypeError: argument of type X is not iterable` | Passing a non-iterable where iteration is expected | `5 in 10` |
| `TypeError: X() takes N positional arguments but M were given` | Wrong number of args passed to a function | Calling `f(a, b)` when `f(a)` is defined |
| Implicit coercion confusion | Code runs but produces wrong type silently | `int / int` returns `float` in Python 3; use `//` for floor division |
| `None` propagation | `None` returned from a function used in an expression | Forgetting `return` in a function body |

---

## Index / Key Errors

| Error | Symptom | Example Trigger |
|-------|---------|-----------------|
| `IndexError: list index out of range` | Accessing index >= len(list) | Off-by-one in a loop using `range(len(x)+1)` |
| `KeyError` | Accessing a dict key that doesn't exist | `d["key"]` when `"key"` not in `d` |
| `KeyError` (silent) | Using `.get()` returns `None` unexpectedly | Default not set: `d.get("key")` returns `None` |
| Negative index misuse | Wraps around unintentionally | `lst[-1]` on an empty list raises `IndexError` |

---

## Logic Errors (Silent Wrong Outputs)

| Error | Symptom | How to Identify |
|-------|---------|-----------------|
| Mutable default argument | State persists across function calls | `def f(lst=[]):` — `lst` is shared across all calls |
| `==` vs `is` confusion | Identity check instead of equality | `x is None` is correct; `x == None` is not idiomatic |
| Shallow copy vs deep copy | Modifying a copy mutates the original | `b = a` for lists; use `b = a.copy()` or `copy.deepcopy(a)` |
| Loop variable capture in closures | All closures reference the same variable | `lambda` in a loop captures loop var by reference, not value |
| Integer division truncation | Expected float, got int | `5 / 2 = 2.5` but `5 // 2 = 2` |
| Boolean short-circuit side effects | Second condition never evaluates | `if a and b()` — `b()` never called if `a` is falsy |
| Off-by-one in range | Last element skipped or extra element included | `range(n)` gives 0 to n-1; `range(1, n+1)` gives 1 to n |

---

## Scope Errors

| Error | Symptom | Example |
|-------|---------|---------|
| `UnboundLocalError` | Variable referenced before assignment inside a function | Assigning to a name inside a function makes it local; reading it before assignment fails |
| `global` misuse | Intended to modify module-level var but didn't declare it | Missing `global x` inside function |
| Closure variable capture | Loop closure captures final value of loop variable | Use `default=var` argument pattern to capture by value |
| Class vs instance variable shadowing | Instance attribute masks class attribute | Assigning `self.x` when `x` is a class variable changes only the instance |

---

## Memory / Performance Errors

| Error | Symptom | Cause |
|-------|---------|-------|
| O(n^2) nested loop | Code correct but too slow on large input | Searching a list inside a loop; use a set/dict for O(1) lookup |
| List concatenation in loop | Memory spikes, slow performance | `result = result + [item]` in a loop; use `.append()` or list comprehension |
| Loading entire file into memory | `MemoryError` or slow I/O | `file.read()` on large files; use line-by-line iteration or generators |
| Repeated recomputation | Slow for recursive problems | Missing memoization; use `functools.lru_cache` |
| String concatenation in loop | Quadratic memory usage | `s += char` in a loop; use `"".join(list)` |

---

## Common Beginner Mistakes

| Mistake | Correct Pattern |
|---------|-----------------|
| `if x == True` | `if x` |
| `if x == None` | `if x is None` |
| `except Exception` catching everything silently | Catch specific exceptions; re-raise or log |
| Modifying a list while iterating it | Iterate over a copy: `for item in lst[:]` |
| Using `input()` result as a number without casting | `int(input(...))` |
| Forgetting `self` in method definition | `def method(self, ...)` |

---

## Lookup Order for Step 1

When identifying the failure mechanism, check in this order:

1. Is there a traceback? Match the exception type to the table above.
2. No traceback but wrong output? Check the Logic Errors table.
3. Runs but too slow? Check Memory / Performance Errors.
4. Intermittent or stateful bug? Check Scope Errors and mutable default argument.
