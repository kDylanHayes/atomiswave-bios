! blit_glyphs
! File 0x99C. 16 by 16 glyph blit. Masks a source byte with 0xFF,
! subtracts 0x20, multiplies by 0x20, and adds the font base at file
! 0xC98. A set glyph bit stores 0xFFFF. A clear bit stores 0x528A.
! The row stride is 0x500.
! Byte-checked assembly, not matched C.

        .org    0x99c
        .global blit_glyphs
blit_glyphs:
.L99c:
        mov.b @+r1, r8
        mov.l .L9e4, r0
        and r0, r8
        mov #32, r0
        sub r0, r8
        shll2 r8
        shll2 r8
        shll r8
        mov.l .L9e8, r0
        add r0, r8
        mov r2, r6
        mov #16, r4
.L9b4:
        mov r6, r7
        mov.w @+r8, r9
        mov.l .L9ec, r10
        mov #16, r5
.L9bc:
        mov.l .L9f0, r0
        tst r10, r9
        bt .L9c4
        mov.l .L9f4, r0
.L9c4:
        mov.w r0, @r7
        add #2, r7
        shlr r10
        dt r5
        bf .L9bc
        mov.l .L9f8, r0
        add r0, r6
        dt r4
        bf .L9b4
        mov.l .L9fc, r0
        add r0, r2
        dt r3
        bf .L99c
        rts
        nop
        .word   0x0000
.L9e4:
        .long   0x000000ff
.L9e8:
        .long   0x00000c98
.L9ec:
        .long   0x00008000
.L9f0:
        .long   0x0000528a
.L9f4:
        .long   0x0000ffff
.L9f8:
        .long   0x00000500
.L9fc:
        .long   0x00000020
