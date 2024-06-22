section .code:
.start:
.loop:
    ld 0
    jz .hlt
    st 1
    pop
    jmp .loop
.hlt:
    hlt

