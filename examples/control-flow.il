; Author: Soham Sen <sensoham135@gmail.com>
; Repository: https://github.com/sohamxda7/openskill

; Assignment, loops, and branching.
sum = 0

for(i 1 5
  sum = sum + i)

cond(
  ((sum > 10) println(sprintf("sum=%d" sum)))
  (t println("unexpected")))
