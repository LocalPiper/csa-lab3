section .data:
    msg: "Hello, world! \n"
section .code:
.start:
    push msg
.loop:
    dup
    ld
    jz .break
    st 1
    pop
    inc
    jmp .loop
.break:
    pop
.hlt:
    hlt
