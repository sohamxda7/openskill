; Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

; Basic list construction, access, and mapping.
(let ((pins '(vin vout vdd gnd)))
  (println (list 'original pins))
  (println (list 'first (car pins) 'rest (cdr pins)))
  (setq extended (append1 pins 'enable))
  (println (list 'append1 extended))
  (println (list 'reverse (reverse extended)))
  (println
    (list
      'labels
      (mapcar (lambda (pin) (strcat "pin_" pin)) extended))))
