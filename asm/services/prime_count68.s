! prime_count68 at 0xA1D4
! Loads the halfword at 0xA0E6 (0x65A3) and stores it at GBR+68.
! That halfword sits inside service_main. The store is in the rts delay.
! Checked assembly, not matched C.

        .org    0xa1d4
        .global prime_count68
prime_count68:
        mov.w 0xa0e6, r0
        rts
        mov.w r0, @(gbr,68)
