# Atomiswave BIOS matching build.
# The ROM stays outside the repo. Override ROM if it lives somewhere else.
# Object recipes are real files. A newer object that no longer matches flash
# is not rebuilt over, and tools/progress.py rejects it.

ROM ?= $(HOME)/Documents/awbios/bios0.ic23
PYTHON ?= python3

ASM_SRCS := $(wildcard asm/boot/*.s) $(wildcard asm/services/*.s) $(wildcard asm/data/*.s)
ASM_OBJS := $(patsubst asm/%.s,build/asm/%.o,$(ASM_SRCS))
C_OBJS := build/services/reject_code.o build/services/ram_window_ready.o \
	build/services/set_hook.o build/services/phase_until_clear.o \
	build/services/retry_issue.o build/services/run_transfer.o \
	build/services/ram_call_2.o build/services/ram_call_3.o \
	build/services/prime_count68.o build/services/quiet_interrupts.o \
	build/services/enter_ram.o build/services/step_phase.o
ISSUE_OBJ := build/services/issue_command.o
LINK_DEPS := src/services.c tools/link_matched.py tools/sh4.py

.PHONY: all split probe progress

all: progress

split:
	$(PYTHON) tools/split.py $(ROM)

build/asm/%.o: asm/%.s
	@mkdir -p $(dir $@)
	$(PYTHON) tools/as_sh.py $< -o $@ --check $(ROM)

# One recipe writes all twelve objects. The stamp is touched after that,
# so a missing object is the only reason to link a second time.
build/services/matched.stamp: $(LINK_DEPS)
	@mkdir -p $(dir $@)
	$(PYTHON) tools/link_matched.py --rom $(ROM)
	@touch $@

$(C_OBJS): build/services/matched.stamp
	@if [ ! -s $@ ]; then $(PYTHON) tools/link_matched.py --rom $(ROM); touch build/services/matched.stamp; fi

$(ISSUE_OBJ): docs/candidates/issue_command_60b.src tools/as_shc_src.py
	@mkdir -p $(dir $@)
	$(PYTHON) tools/as_shc_src.py $< -o $@ --origin 0xA3A0 --symbol issue_command \
		--extern '__$$reject_code=0x9E34' --extern '__$$prime_count68=0xA1D4' --check $(ROM)

probe:
	$(PYTHON) tools/probe_compiler.py

progress: split $(ASM_OBJS) $(C_OBJS) $(ISSUE_OBJ) probe
	$(PYTHON) tools/progress.py
