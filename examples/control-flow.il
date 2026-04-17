; Assignment, loops, and branching.
(setq sum 0)

(for i 1 5
  (setq sum (+ sum i)))

(cond
  ((> sum 10) (println (sprintf "sum=%d" sum)))
  (t (println "unexpected")))
