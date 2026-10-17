! FUN_0a15e
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0xa15e
        .global FUN_0a15e
FUN_0a15e:
        mov #2, r7
        mov.l 0xa1d0, r3
        mov #0, r6
        mov r6, r5
        jmp r3
        mov r6, r4
