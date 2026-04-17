; Work with in-memory ports.
(let ((out (outstring)))
  (fprintf out "alpha=%d beta=%d" 2 3)
  (setq text (getOutstring out))
  (close out)
  (println text))

(let ((inp (instring "row1\nrow2\n")))
  (println (lineread inp))
  (println (gets inp))
  (close inp))
