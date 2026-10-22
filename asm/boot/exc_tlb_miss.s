! exc_tlb_miss
! File 0x400, the TLB-miss vector. Three jsr @r1. r1 is incoming, not
! a constant in this range. Each call gets pointer and count arguments
! from the pool, then the range branches to set_system_bits.
! The longs at file 0x428 through 0x440 are init_memory's pool.
! Byte-checked assembly, not matched C.

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
        .long   0xa05f8050 ! 0x428 init_memory clears this word
        .long   0xa05f8048 ! 0x42C bit 3 is forced on
        .long   0xa5000000 ! 0x430 filled with -1
        .long   0x00025800 ! 0x434 dword count of that fill
        .long   0x0000046c ! 0x438 loaded into r1. File offset of copy_words
        .long   0x00000500 ! 0x43C loaded into r2
        .long   0x00001498 ! 0x440 loaded into r3
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
