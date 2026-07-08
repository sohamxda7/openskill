; Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

; Assignment, loops, and branching.
sum = 0

for(i 1 5
  sum = sum + i)

cond(
  ((sum > 10) println(sprintf("sum=%d" sum)))
  (t println("unexpected")))
