! set_hook at 0xA158
! Stores 0x8C000C86 at GBR+136. The store is in the rts delay slot.
! Checked assembly, not matched C.

        .org    0xa158
        .global set_hook
set_hook:
        mov.l 0xa1cc, r0
        rts
        mov.l r0, @(gbr,136)
