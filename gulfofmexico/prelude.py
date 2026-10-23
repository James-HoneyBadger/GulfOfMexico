"""Standard prelude for Gulf of Mexico.

Gulf of Mexico has no loops, so everyday list work is written as recursion.
The prelude provides the handful of helpers every program ends up writing by
hand, implemented in GOM itself (so they behave exactly like user code):

    range(n)              [0, 1, ... n-1]
    map(list, fn)         transform every element
    filter(list, fn)      keep elements where fn returns true
    reduce(list, fn, acc) fold left
    zip(a, b)             pairs of elements
    sortBy(list, fn)      stable sort by a key function
    sum(list), maxOf(list), minOf(list)
    reverseOf(list), take(list, n), concat(a, b)

Loaded into the base namespace at startup. Disable with ``GOM_NO_PRELUDE=1``;
a program may shadow any prelude name with its own declaration.
"""

from __future__ import annotations

import os
from typing import Any

#: Environment variable that turns the prelude off.
DISABLE_ENV = "GOM_NO_PRELUDE"

PRELUDE_SOURCE = """\
// ── iteration helpers (GOM has no loops) ────────────────────────────────
function range(count) => {
   return rangeFrom(0, count)!
}!

function rangeFrom(start, count) => {
   const last = count - 1!
   return buildRange(start, last, 0)!
}!

function buildRange(start, last, index) => {
   if index > last {
      return []!
   }
   const value = start + index!
   const nextIndex = index + 1!
   const rest = buildRange(start, last, nextIndex)!
   return [value] + rest!
}!

function map(list, fn) => {
   return mapFrom(list, fn, -1)!
}!

function mapFrom(list, fn, index) => {
   const last = list.length - 2!
   if index > last {
      return []!
   }
   const head = fn(list[index])!
   const nextIndex = index + 1!
   const rest = mapFrom(list, fn, nextIndex)!
   return [head] + rest!
}!

function filter(list, fn) => {
   return filterFrom(list, fn, -1)!
}!

function filterFrom(list, fn, index) => {
   const last = list.length - 2!
   if index > last {
      return []!
   }
   const nextIndex = index + 1!
   const rest = filterFrom(list, fn, nextIndex)!
   const item = list[index]!
   if fn(item) {
      return [item] + rest!
   }
   return rest!
}!

function reduce(list, fn, accumulator) => {
   return reduceFrom(list, fn, accumulator, -1)!
}!

function reduceFrom(list, fn, accumulator, index) => {
   const last = list.length - 2!
   if index > last {
      return accumulator!
   }
   const total = fn(accumulator, list[index])!
   const nextIndex = index + 1!
   return reduceFrom(list, fn, total, nextIndex)!
}!

function zip(left, right) => {
   return zipFrom(left, right, -1)!
}!

function zipFrom(left, right, index) => {
   const lastLeft = left.length - 2!
   const lastRight = right.length - 2!
   var last = lastLeft!
   if lastRight < lastLeft {
      last = lastRight!
   }
   return zipUntil(left, right, index, last)!
}!

function zipUntil(left, right, index, last) => {
   if index > last {
      return []!
   }
   const pair = [left[index], right[index]]!
   const nextIndex = index + 1!
   const rest = zipUntil(left, right, nextIndex, last)!
   return [pair] + rest!
}!

function sum(list) => {
   return reduce(list, addValues, 0)!
}!

function addValues(left, right) => {
   return left + right!
}!

function maxOf(list) => {
   return reduce(list, biggerOf, list[-1])!
}!

function biggerOf(left, right) => {
   if right > left {
      return right!
   }
   return left!
}!

function minOf(list) => {
   return reduce(list, smallerOf, list[-1])!
}!

function smallerOf(left, right) => {
   if right < left {
      return right!
   }
   return left!
}!

function take(list, count) => {
   return takeFrom(list, count, -1)!
}!

function takeFrom(list, count, index) => {
   if index > count - 2 {
      return []!
   }
   const item = list[index]!
   const nextIndex = index + 1!
   const rest = takeFrom(list, count, nextIndex)!
   return [item] + rest!
}!

function sortBy(list, fn) => {
   var result = reverseOf(list)!
   return insertionSort(result, fn, -1)!
}!

function insertionSort(list, fn, index) => {
   const last = list.length - 2!
   if index > last {
      return list!
   }
   const inserted = insertSorted(list, fn, index)!
   const nextIndex = index + 1!
   return insertionSort(inserted, fn, nextIndex)!
}!

function insertSorted(list, fn, index) => {
   if index <= -1 {
      return list!
   }
   const key = fn(list[index])!
   const previousKey = fn(list[index - 1])!
   if previousKey > key {
      const earlier = list[index - 1]!
      var swapped = list!
      swapped[index - 1] = list[index]!
      swapped[index] = earlier!
      return insertSorted(swapped, fn, index - 1)!
   }
   return list!
}!

function reverseOf(list) => {
   return reverseInto(list, [])!
}!

function reverseInto(list, accumulator) => {
   if list.length == 0 {
      return accumulator!
   }
   const head = list[-1]!
   const tail = dropFirst(list)!
   return reverseInto(tail, [head] + accumulator)!
}!

function dropFirst(list) => {
   return dropFirstFrom(list, -1)!
}!

function dropFirstFrom(list, index) => {
   const last = list.length - 2!
   if index > last {
      return []!
   }
   const item = list[index]!
   const nextIndex = index + 1!
   const rest = dropFirstFrom(list, nextIndex)!
   if index == -1 {
      return rest!
   }
   return [item] + rest!
}!
"""

_PRELUDE_STATE: dict[str, Any] = {"loaded": False}


def prelude_enabled() -> bool:
    """Whether the prelude should be loaded for this process."""
    return os.environ.get(DISABLE_ENV) != "1"


def load_prelude(namespaces: list[dict], ctx: object) -> None:
    """Execute :data:`PRELUDE_SOURCE` into *namespaces* (idempotent per run)."""
    if not prelude_enabled():
        return
    # Imported lazily: the processor/interpreter import this package.
    from gulfofmexico.interpreter.execution import (  # noqa: PLC0415
        interpret_code_statements_main_wrapper,
    )
    from gulfofmexico.processor.lexer import tokenize  # noqa: PLC0415
    from gulfofmexico.processor.syntax_tree import (  # noqa: PLC0415
        generate_syntax_tree,
    )

    filename = "<prelude>"
    saved = (getattr(ctx, "filename", ""), getattr(ctx, "code", ""))
    try:
        ctx.filename = filename  # type: ignore[attr-defined]
        ctx.code = PRELUDE_SOURCE  # type: ignore[attr-defined]
        tokens = tokenize(filename, PRELUDE_SOURCE)
        statements = generate_syntax_tree(filename, tokens, PRELUDE_SOURCE)
        interpret_code_statements_main_wrapper(
            statements, namespaces, [], [{}], {}, [], ctx,
        )
    finally:
        ctx.filename, ctx.code = saved  # type: ignore[misc]
        _PRELUDE_STATE["loaded"] = True
