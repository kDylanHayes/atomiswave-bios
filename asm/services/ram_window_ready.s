! ram_window_ready at 0x9E50
! Returns 1 when GBR+100 is 0x8C008000 and GBR+76 is 32. Otherwise 0.
! The 0x8C008000 literal is at 0x9EFC, inside step_phase.
! Checked assembly, not matched C.

        .org    0x9e50
        .global ram_window_ready
ram_window_ready:
        mov.l @(gbr,100), r0
        mov.l 0x9efc, r3
        cmp/eq r3, r0
        bf .L9e62
        mov.l @(gbr,76), r0
        cmp/eq #32, r0
        bf .L9e62
        rts
        mov #1, r0
.L9e62:
        mov #0, r0
        rts
        nop
