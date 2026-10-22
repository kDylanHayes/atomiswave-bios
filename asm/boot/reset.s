! reset
! File 0x0. Stores 0x618066D8 at 0xFF80000C (WCR2) and 0x0000090D at
! 0xFF00001C (CCR). Stores 0xA677, one less than the 0xA678 limit, at
! 0xA05F74E4. Jumps to physical 0x5C: r0 is 0x5C masked with
! 0x00FFFFFF and ored with 0.
! Byte-checked assembly, not matched C.

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
        .long   0xff80000c ! WCR2
.L3c:
        .long   0x618066d8 ! stored at WCR2
.L40:
        .long   0xff00001c ! CCR
.L44:
        .long   0x0000090d ! stored at CCR
.L48:
        .long   0xa05f74e4
.L4c:
        .long   0x0000a678 ! one less than this is stored
.L50:
        .long   0x0000005c ! physical boot entry
.L54:
        .long   0x00000000 ! ORed after the mask
.L58:
        .long   0x00ffffff ! mask applied to 0x5C
