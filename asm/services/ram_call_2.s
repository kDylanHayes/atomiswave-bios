! ram_call_2 at 0xA15E
! Tail call 0x8C0010F0 with r4 = r5 = r6 = 0 and r7 = 2.
! Checked assembly, not matched C.

        .org    0xa15e
        .global ram_call_2
ram_call_2:
        mov #2, r7
        mov.l 0xa1d0, r3
        mov #0, r6
        mov r6, r5
        jmp r3
        mov r6, r4
