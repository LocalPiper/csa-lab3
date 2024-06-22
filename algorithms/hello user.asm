section .data:
    hello: "\n>What is yout name?"
    bye: "\n>Hello, "
    bf: "                                              "
addr: 0
section .code:
.start:

    push hello
    call .print

    push bf
    call .read

    push bye
    call .print

    push bf
    call .print

.exit:
    hlt

.print:
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
    pop
    ret

.read:
.read_loop:
    dup
    ld 0 
    jz .ret
    swap
    st
    pop
    inc
    jmp .read_loop
.ret:
    ret
    

