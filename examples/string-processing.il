; Parse a settings line and build a readable summary.
(let ((line "width=12 height=5 label=m1_data"))
  (setq fields (parseString line " ="))
  (println (list 'fields fields))
  (println (list 'label_upper (upperCase (nth 5 fields))))
  (println (list 'label_prefix (substr (nth 5 fields) 0 2)))
  (println
    (sprintf
      "Rectangle %sx%s on %s"
      (nth 1 fields)
      (nth 3 fields)
      (upperCase (nth 5 fields)))))
