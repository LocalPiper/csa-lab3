section .data:
   result: 2
   max: 10
   prev: 1
section .code:
.start:
   push 2
   dup
.loop:
   pop
   ld prev
   add
   swap
   st prev
   pop

   dup
   and 1
   sub 1
   jz .loop
   pop

   dup
   ld max
   sub
   jle .end_loop
   pop
   pop
   
   ld result
   add
   st result
   pop
   
   jmp .loop
.end_loop:
   pop
   ld result
   st 2
   pop
   hlt

