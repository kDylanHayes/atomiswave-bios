! exc_tlb_miss
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0x400
        .global exc_tlb_miss
exc_tlb_miss:
        mov.l .L444, r4
        mov.l .L448, r5
        mov.l .L44c, r6
        jsr r1
        nop
        mov.l .L450, r3
        mov.l .L454, r4
        mov.l .L458, r5
        mov.l .L45c, r6
        jsr r1
        nop
        mov.l .L460, r3
        mov.l .L464, r4
        mov.l .L468, r5
        mov.l .L468, r6
        jsr r1
        nop
        bra 0x484
        nop
        .word   0x0000
        .long   0xa05f8050
        .long   0xa05f8048
        .long   0xa5000000
        .long   0x00025800
        .long   0x0000046c
        .long   0x00000500
        .long   0x00001498
.L444:
        .long   0xa503e458
.L448:
        .long   0x0000003c
.L44c:
        .long   0x00000048
.L450:
        .long   0x00005818
.L454:
        .long   0xa5043548
.L458:
        .long   0x00000058
.L45c:
        .long   0x00000030
.L460:
        .long   0x00009a18
.L464:
        .long   0xa5052668
.L468:
        .long   0x00000010
