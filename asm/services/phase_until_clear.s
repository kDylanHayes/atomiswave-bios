! phase_until_clear at 0xA1DA
! Stores r4 at GBR+146, then calls the 0x9CDC hole and step_phase until
! step_phase returns a value >= 0.
! Checked assembly, not matched C.

        .org    0xa1da
        .global phase_until_clear
phase_until_clear:
        mov r4, r0
        sts.l pr, @-r15
        mov.w r0, @(gbr,146)
.La1e0:
        bsr 0x9cdc
        nop
        bsr 0x9e68
        nop
        mov r0, r4
        cmp/pz r4
        bf .La1e0
        lds.l @+r15, pr
        rts
        mov r4, r0
