; Literal data and list helpers.
(let ((pins '(in out vdd gnd)))
  (println pins)
  (println (reverse pins))
  (println (append1 pins 'clk)))
