! poll_bit
! File 0x97c. r0 is the countdown. Spins while Holly bit 0x2000 at
! 0xA05F810C stays clear, then while it stays set, then decrements.
! The bf at the dt is the loop MAME replaces with a nop.

        .org    0x97c
        .global poll_bit
poll_bit:
        mov.l   .Lholly, r1
        mov.l   .Lmask, r2
.Lclear:
        mov.l   @r1, r3
        tst     r2, r3
        bf      .Lclear
.Lset:
        mov.l   @r1, r3
        tst     r2, r3
        bt      .Lset
        dt      r0
        bf      .Lclear
        rts
        nop
.Lholly:
        .long   0xa05f810c
.Lmask:
        .long   0x00002000
