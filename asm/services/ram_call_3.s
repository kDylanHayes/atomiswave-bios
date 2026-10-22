! ram_call_3 at 0xA16A
! Tail call 0x8C0010F0 with r4 = r5 = r6 = 0 and r7 = 3.
! Twelve bytes of code. The rest of this range is the shared literal pool.
! Checked assembly, not matched C.

        .org    0xa16a
        .global ram_call_3
ram_call_3:
        mov #3, r7
        mov.l .La1d0, r3
        mov #0, r6
        mov r6, r5
        jmp r3
        mov r6, r4
        .word   0x0000
        .long   0xefffff0f ! 0xA178 SR mask ANDed by service_main and enter_ram
        .long   0x0000ff80 ! 0xA17C stored at GBR+146
        .long   0x8c000800 ! 0xA180 kept in r12 and called
        .long   0x8c00c000 ! 0xA184 kept in r14 and called
        .long   0x8c008000 ! 0xA188 stored at GBR+100
        .long   0x8ce00000 ! 0xA18C called with r4 = 1
        .long   0x8c0004f4 ! 0xA190 called with GBR+100
        .long   0x0000fffb ! 0xA194 stored at GBR+144
        .long   0x8c000472 ! 0xA198 called with no argument
        .long   0x8c000462 ! 0xA19C called with no argument
        .long   0x8c000fd8 ! 0xA1A0 passed as r4
        .long   0x8c0005b8 ! 0xA1A4 the call that takes that r4
        .long   0x0000b06e ! 0xA1A8 r5 to scan_list
        .long   0x8c010000 ! 0xA1AC r4 to scan_list
        .long   0x8c008100 ! 0xA1B0 stored at GBR+100 before the return
        .long   0x100000f0 ! 0xA1B4 ORed into SR by enter_ram and quiet_interrupts
        .long   0x8c000000 ! 0xA1B8 VBR set by enter_ram
        .long   0x8c0006aa ! 0xA1BC called by enter_ram
        .long   0x8c000728 ! 0xA1C0 stored at GBR+564
        .long   0xa05f6910 ! 0xA1C4 written by enter_ram and quiet_interrupts
        .long   0x8c000768 ! 0xA1C8 enter_ram jumps here
        .long   0x8c000c86 ! 0xA1CC stored at GBR+136 by set_hook
.La1d0:
        .long   0x8c0010f0 ! 0xA1D0 ram_call_3 jumps here
