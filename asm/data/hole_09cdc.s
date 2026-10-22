! hole_09cdc
! File 0x9CDC. bsr targets 0x9CDC and 0x9CE2 land here. The bytes are
! zero. Not a recoverable function. service_main, phase_until_clear,
! scan_list, retry_issue, and run_transfer call 0x9CDC. scan_list
! calls 0x9CE2.

        .org    0x9cdc
        .global hole_09cdc
hole_09cdc:
        .long   0x00000000
        .word   0x0000
hole_09ce2:
        .word   0x0000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .word   0x0000
