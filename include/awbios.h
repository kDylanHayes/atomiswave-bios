#ifndef AWBIO_H
#define AWBIO_H

#include <stdint.h>

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef int8_t s8;
typedef int16_t s16;
typedef int32_t s32;

/* IC23 is a 128 KiB Macronix flash. The same bytes are visible at physical
 * 0 and in the P2 uncached area. Reset enters at the P2 address. */
#define AWB_FLASH_PHYS 0x00000000u
#define AWB_FLASH_P2 0xA0000000u
#define AWB_FLASH_SIZE 0x00020000u

/* SH-4 exception offsets from VBR 0. */
#define AWB_EXC_RESET 0x00000000u
#define AWB_EXC_GENERAL 0x00000100u
#define AWB_EXC_TLB 0x00000400u
#define AWB_EXC_INTERRUPT 0x00000600u

/* CCN and the bus controller. Names follow the SH-4 manual. */
#define CCN_CCR 0xFF00001Cu
#define BSC_BCR1 0xFF800000u
#define BSC_BCR2 0xFF800004u
#define BSC_WCR1 0xFF800008u
#define BSC_WCR2 0xFF80000Cu
#define BSC_WCR3 0xFF800010u
#define BSC_MCR 0xFF800014u
#define BSC_PCR 0xFF800018u
#define BSC_RTCSR 0xFF80001Cu
#define BSC_RTCNT 0xFF800020u
#define BSC_RTCOR 0xFF800024u
#define BSC_RFCR 0xFF800028u

/* Holly register polled by poll_bit. The mask is the pool constant 0x2000. */
#define HOLLY_P2 0xA05F0000u
#define HOLLY_POLL 0xA05F810Cu
#define HOLLY_POLL_BIT 0x00002000u

/* Macronix byte-program addresses used by program_bootrom. */
#define AWB_FLASH_555 0xA0000555u
#define AWB_FLASH_2AA 0xA00002AAu

/* The jmp at file 0x966 is 0xA0000000 | the dword at 0xAC01006C.
 * program_bootrom loads 0xAC010000 and adds 0x6C. The Ghidra export
 * comment names 0x01AC006C. That address is not in this pool. */
#define AWB_AREA3_P2 0xAC010000u
#define AWB_HANDOFF 0xAC01006Cu

/* Footer at file 0x1A000. No code reference to it has been found. */
#define AWB_FOOTER_OFF 0x0001A000u
#define AWB_FOOTER_LEN 12u

/* Service cluster. step_phase installs this as GBR, then restores the old one. */
#define AWB_GBR_BASE 0x8C000000u

/* Compared with the word at GBR+100 by ram_window_ready. */
#define AWB_RAM_WINDOW 0x8C008000u

/* Fixed RAM call. r7 is 0, 1, 2, 3, or 4 at the sites in this image. */
#define AWB_RAM_SERVICE 0x8C0010F0u

/* Stored at GBR+136 by set_hook. */
#define AWB_RAM_HOOK 0x8C000C86u

/* enter_ram writes 8 here. quiet_interrupts writes 0. */
#define SB_IML2NRM 0xA05F6910u

/* ORed into SR by enter_ram and quiet_interrupts. Sets BL and IMASK. */
#define AWB_SR_BLOCK 0x100000F0u

/* ANDed into SR by enter_ram. Clears BL and IMASK. */
#define AWB_SR_UNBLOCK 0xEFFFFF0Fu

#endif
