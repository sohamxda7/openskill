; Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

; A tiny vending-machine style state machine.
(procedure (nextState state event)
  (caseq state
    ((idle)
      (caseq event
        ((coin) 'ready)
        ((cancel) 'idle)
        (t state)))
    ((ready)
      (caseq event
        ((dispense) 'done)
        ((cancel) 'idle)
        (t state)))
    ((done)
      (caseq event
        ((reset) 'idle)
        (t state)))
    (t state)))

(let ((state 'idle)
      (events '(coin dispense reset coin cancel)))
  (println (list 'start state))
  (foreach event events
    (setq state (nextState state event))
    (println (list 'event event 'state state)))
  t)
