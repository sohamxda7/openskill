; Author: Soham Sen <sensoham135@gmail.com>
; Repository: https://github.com/sohamxda7/openskill

; Work with in-memory ports.
let(((out outstring()))
  fprintf(out "alpha=%d beta=%d" 2 3)
  text = getOutstring(out)
  close(out)
  println(text))

let(((inp instring("row1\nrow2\n")))
  println(lineread(inp))
  println(gets(inp))
  close(inp))
