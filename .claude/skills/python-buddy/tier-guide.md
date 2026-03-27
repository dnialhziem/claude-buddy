# Tiered Solution Guide

Contracts for what each solution tier must and must not use.
Use this when writing the three code blocks in Step 3 of the Execution Flow.

> Sources: [PEP 8 – Style Guide](https://peps.python.org/pep-0008/), [Python Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html), [collections module](https://docs.python.org/3/library/collections.html), [itertools module](https://docs.python.org/3/library/itertools.html), [functools module](https://docs.python.org/3/library/functools.html)

---

## Tier Contracts

### Easy — Readable First

**Goal:** A beginner can read and understand this in one pass.

| Must use | Must NOT use |
|----------|--------------|
| `for` / `while` loops | List/dict/set comprehensions |
| Basic `if` / `elif` / `else` | `lambda` |
| `.append()`, `.pop()`, `.update()` | `map()`, `filter()`, `reduce()` |
| Named variables with clear intent | Walrus operator (`:=`) |
| `len()`, `range()`, `enumerate()`, `zip()` | Generators (`yield`) |
| Simple `try` / `except` for error handling | Decorator syntax |

**Tone:** Verbose is fine. Prefer clarity over conciseness.

---

### Moderate — Idiomatic Python

**Goal:** A Python developer would write it this way day-to-day.

| Must use (at least one) | Must NOT use |
|--------------------------|--------------|
| List / dict / set comprehensions | Raw `yield` generators (save for Advanced) |
| `enumerate()`, `zip()`, `any()`, `all()` | Specialized third-party modules |
| `dict.get()`, `dict.setdefault()` | Complex `functools` chains |
| `sorted()` with `key=` argument | `collections` internals |
| Ternary expression `x if cond else y` | Over-engineered class structures |
| String `.join()`, `.split()`, `.strip()` | |
| Context managers (`with open(...) as f`) | |
| f-strings for formatting | |

**Tone:** Concise. Follows PEP 8. No unnecessary intermediary variables.

---

### Advanced — Performance and Efficiency

**Goal:** Minimizes memory usage and execution time. Appropriate for large data or repeated calls.

| Must use (at least one) | Avoid |
|--------------------------|-------|
| Generator expressions or `yield` | Readability sacrifices without measurable gain |
| `collections.Counter`, `defaultdict`, `deque`, `namedtuple` | Premature optimization on trivially small data |
| `itertools.chain`, `islice`, `groupby`, `product`, `combinations` | |
| `functools.lru_cache`, `reduce`, `partial` | |
| `zip()` over index-based loops | |
| Lazy evaluation patterns | |

**Tone:** Explain the performance trade-off in a comment if it's non-obvious. One-liners are acceptable if they are idiomatic.

---

## Module Allowlist for Advanced Tier

All from the Python standard library — no third-party installs needed.

| Module | Key tools | Use for |
|--------|-----------|---------|
| `collections` | `Counter`, `defaultdict`, `deque`, `namedtuple`, `OrderedDict` | Frequency counts, fast queues, structured records |
| `itertools` | `chain`, `islice`, `groupby`, `product`, `combinations`, `permutations`, `cycle`, `accumulate` | Lazy iteration, combinatorics, chaining iterables |
| `functools` | `lru_cache`, `reduce`, `partial`, `cached_property` | Memoization, currying, repeated-call optimization |
| `operator` | `itemgetter`, `attrgetter`, `methodcaller` | Faster key functions than lambdas in sort/map |
| `heapq` | `nlargest`, `nsmallest`, `heappush`, `heappop` | Priority queues, top-N problems |
| `bisect` | `bisect_left`, `insort` | Binary search on sorted lists |

---

## Worked Example

**Problem:** Count the frequency of each word in a list.

```python
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
```

**Easy**
```python
counts = {}
for word in words:
    if word in counts:
        counts[word] = counts[word] + 1
    else:
        counts[word] = 1
print(counts)
```

**Moderate**
```python
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
print(counts)
```

**Advanced**
```python
from collections import Counter
counts = Counter(words)
print(counts)
```

---

## When to Skip or Merge a Tier

| Situation | Action |
|-----------|--------|
| Problem is trivially simple (< 3 lines at Easy) | Still provide all three tiers but note the trade-off is minimal |
| Easy and Moderate solutions are nearly identical | Note this explicitly; don't pad with fake differences |
| Advanced tier offers no meaningful benefit (small data, one-time call) | Provide it anyway but add a comment: "Overkill for small inputs — use Moderate unless data is large" |
| Problem involves I/O, networking, or GUI | Advanced tier focuses on `with` patterns and generators, not low-level optimization |

---

## Output Format Contract

Each tier block must follow this structure:

```
**Easy**
[optional: one sentence on the approach]
```python
# code here
```

**Moderate**
[optional: one sentence on the approach]
```python
# code here
```

**Advanced**
[optional: one sentence on what makes this faster/leaner]
```python
# code here
```
```

Keep explanatory text between tiers short — the code should speak for itself.
