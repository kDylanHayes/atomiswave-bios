! footer
! File 0x1A000. Twelve original bytes. bios1 differs at 0x1A003,
! 0x1A004, 0x1A006, 0x1A007, 0x1A008, and 0x1A009. No instruction in
! this split loads this address.

        .org    0x1a000
        .global footer
footer:
        .long   0x02031101
        .long   0x3b160007
        .long   0x00005f01
