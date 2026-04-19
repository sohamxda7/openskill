; Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

; Define and call small reusable procedures.
(defun areaRect (width height)
  width * height)

(procedure (describeRect width height)
  (println
    (list 'width width 'height height 'area (areaRect width height))))

(describeRect 4 6)
