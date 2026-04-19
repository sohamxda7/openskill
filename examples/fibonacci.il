; Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

; Build a Fibonacci series with a procedure, a loop, and list growth.
(procedure (fibonacciSeries count)
  (let ((a 0) (b 1) (result nil))
    (for i 1 count
      (setq result (append1 result a))
      (let ((next (+ a b)))
        (setq a b)
        (setq b next)))
    result))

(println (list 'first_10_values (fibonacciSeries 10)))
