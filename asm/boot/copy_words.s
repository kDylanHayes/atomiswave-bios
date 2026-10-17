! copy_words
! File 0x46c. r2 is added to r4 once per outer trip. r5 is the inner
! word count, reloaded into r8 each trip. r6 is the outer count.
! r3 is the source pointer. The inner bf targets the post-increment
! load. The outer bf targets this entry.

        .org    0x46c
        .global copy_words
copy_words:
        add     r2, r4
        mov     r4, r7
        mov     r5, r8
.Lword:
        mov.l   @r3+, r0
        mov.l   r0, @r7
        add     #4, r7
        dt      r8
        bf      .Lword
        dt      r6
        bf      copy_words
        rts
        nop
