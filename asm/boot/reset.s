! reset
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0x0
        .global reset
reset:
        mov.l .L38, r2
        mov.l .L3c, r0
        mov.l r0, @r2
        nop
        nop
        mov.l .L40, r2
        mov.l .L44, r1
        mov.l r1, @r2
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        mov.l .L48, r2
        mov.l .L4c, r1
        add #-1, r1
        mov.l r1, @r2
        mov.l .L50, r0
        mov.l .L54, r1
        mov.l .L58, r2
        and r2, r0
        or r1, r0
        jmp r0
        nop
        .word   0x0000
.L38:
        .long   0xff80000c
.L3c:
        .long   0x618066d8
.L40:
        .long   0xff00001c
.L44:
        .long   0x0000090d
.L48:
        .long   0xa05f74e4
.L4c:
        .long   0x0000a678
.L50:
        .long   0x0000005c
.L54:
        .long   0x00000000
.L58:
        .long   0x00ffffff
