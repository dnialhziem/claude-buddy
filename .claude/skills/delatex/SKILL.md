---
name: delatex
description: Use when the user wants to convert LaTeX or math notation to readable plain text, solve a math problem with step-by-step working, or get a clean readable solution to a linear algebra or calculus question.
argument-hint: "convert | solve"
---

## INVOCATION GUARD

This skill must ONLY run when the user explicitly types `/delatex`. Do NOT run this skill in response to general requests unless `/delatex` was typed.

---

## Mode Detection

Check `$ARGUMENTS` and the user's message to determine mode:

- **Convert mode** — user pastes LaTeX/math markup and wants it cleaned up. Keywords: "convert", "clean", pasted LaTeX with `$$`, `\mathbf`, `\frac`, etc.
- **Solve mode** — user provides a math problem (text or image) and wants step-by-step working. Keywords: "solve", "find", "calculate", "show working", or a question with no LaTeX markup.
- **Both** — user pastes existing LaTeX working and wants it re-explained step-by-step.

If unclear, ask: "Do you want me to (1) clean up LaTeX notation, or (2) solve this problem with full step-by-step working?"

---

## MODE 1: Convert (LaTeX → Readable Text)

Strip all LaTeX markup and rewrite as clean plain text.

### Conversion Table

| LaTeX | Readable |
|---|---|
| `\mathbf{a}` | `a` |
| `\overrightarrow{AB}` | `AB` |
| `\times` | `×` |
| `\cdot` | `·` |
| `\sqrt{x}` | `√x` |
| `\tfrac{a}{b}` / `\dfrac{a}{b}` / `\frac{a}{b}` | `a/b` |
| `\boxed{x}` | `→ Answer: x` |
| `\begin{vmatrix}...\end{vmatrix}` | `det[ row1 ; row2 ; row3 ]` |
| `\hat{n}` | `n̂` |
| `\leq` / `\geq` | `≤` / `≥` |
| `\text{Word}` | `Word` |
| `\quad` | `  ` (space) |
| `\\` (matrix row break) | `;` |
| `&` (matrix column sep) | ` | ` |
| `\mathbf{i}`, `\mathbf{j}`, `\mathbf{k}` | `i`, `j`, `k` |
| `\left(` / `\right)` | `(` / `)` |
| `\left[` / `\right]` | `[` / `]` |
| `$$...$$`, `$...$`, `\[...\]` | (remove delimiters) |

### Convert Rules

1. Remove all LaTeX delimiters
2. Apply every row of the conversion table
3. Rewrite matrices as: `det[ i | j | k ; row2 ; row3 ]`
4. Keep structure — numbered lists, lettered parts, indentation
5. Preserve all working — don't skip steps
6. Boxed answers → `→ Answer: value`

### Convert Output Format

Output inside a code block for easy copying:

````
```
[converted plain text]
```
````

End with: *"Copy-paste ready. Let me know if any symbol didn't convert correctly."*

---

## MODE 2: Solve (Step-by-Step Working)

Solve the math problem and present full working in clean, readable plain text — no LaTeX, no markup. Match the style of the example below.

### Output Style (match this exactly)

Use this structure for every solution:

```
Question [number/label]: [Problem Title]

[Restate the problem clearly in one sentence.]

─────────────────────────────────────────────

Step 1: [Descriptive Step Title]
[Brief explanation of what you're doing and why.]

  [calculation or setup]
  [result]

Step 2: [Descriptive Step Title]
[Brief explanation.]

  [Show each component calculation on its own line]
  [e.g.]
  i component: (a)(d) - (b)(c) = result
  j component: -[(a)(d) - (b)(c)] = result
  k component: (a)(d) - (b)(c) = result

  Result: (x, y, z)

Step 3: [Descriptive Step Title]
[Brief explanation.]

  formula
  = substitution
  = simplified
  = final value

─────────────────────────────────────────────
Answer: [value with units if applicable]
```

### Solve Rules

1. **Always restate the problem** at the top — what is given, what is asked
2. **Number every step** with a clear descriptive title (e.g. "Step 2: Compute the Cross Product")
3. **Explain each step** in one sentence before showing the math — say what you're doing and why
4. **Show every component** — don't collapse multi-part calculations into one line
5. **Use plain symbols only:**
   - Cross product: `×`
   - Dot product: `·`
   - Vectors: write as `AB` or `(x, y, z)` — no arrows needed
   - Magnitude: `||v||`
   - Square root: `√(expression)`
   - Fractions: `a/b` or `(numerator) / (denominator)`
6. **Indent calculations** under each step using 2 spaces
7. **Draw a separator line** (`─────`) before the final answer
8. **State the answer clearly** — value + what it represents

### Solve Example

**Input:** "Find the area of the parallelogram with vertices A(1,0,1), B(0,1,1), C(−1,0,1), D(0,−1,1)."

**Output:**
```
Question 51(b): Area of the Parallelogram

Vertices: A(1,0,1), B(0,1,1), C(−1,0,1), D(0,−1,1)
Find the area using the cross product of two adjacent edge vectors.

─────────────────────────────────────────────

Step 1: Construct Adjacent Edge Vectors
Choose vertex A as the base point. Compute the vectors to its two adjacent vertices B and D.

  AB = B − A = (0−1, 1−0, 1−1) = (−1, 1, 0)
  AD = D − A = (0−1, −1−0, 1−1) = (−1, −1, 0)

Step 2: Compute the Cross Product (AB × AD)
The area of the parallelogram equals the magnitude of the cross product of two adjacent edge vectors.

  AB × AD = det[ i |  j | k ;
                −1 |  1 | 0 ;
                −1 | −1 | 0 ]

  i component: (1)(0) − (0)(−1) = 0
  j component: −[(−1)(0) − (0)(−1)] = 0
  k component: (−1)(−1) − (1)(−1) = 1 − (−1) = 2

  AB × AD = (0, 0, 2)

Step 3: Calculate the Magnitude (Area)

  Area = ||AB × AD||
       = √(0² + 0² + 2²)
       = √4
       = 2

─────────────────────────────────────────────
Answer: Area = 2
```

---

## Notes

- **Never use LaTeX in Solve mode output** — no `$$`, no `\frac`, no `\mathbf`. Everything must be readable as plain text.
- If given multiple questions, solve each one in full before moving to the next.
- If the input is already clean plain text with no LaTeX, default to **Solve mode**.
- If the input is a `.md` or `.tex` file, offer to save the output as a new file with `_plain` suffix.
- This skill **can and should solve math** in Solve mode — do not refuse to calculate.
