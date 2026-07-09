; Author: Soham Sen <sensoham135@gmail.com>
; Repository: https://github.com/sohamxda7/openskill

; Build a Fibonacci series with a procedure, a loop, and list growth.
procedure(fibonacciSeries(count)
  let(((a 0) (b 1) (result nil))
    for(i 1 count
      result = append1(result a)
      let(((next a + b))
        a = b
        b = next))
    result))

println(list('first_10_values fibonacciSeries(10)))
