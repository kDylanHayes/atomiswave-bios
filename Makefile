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
	build/services/retry_issue.o build/services/run_transfer.o
LINK_DEPS := src/services.c tools/link_matched.py tools/sh4.py

.PHONY: all split probe progress

all: progress

split:
	$(PYTHON) tools/split.py $(ROM)

build/asm/%.o: asm/%.s
	@mkdir -p $(dir $@)
	$(PYTHON) tools/as_sh.py $< -o $@ --check $(ROM)

# One recipe writes all six objects. The stamp is touched after that,
# so a missing object is the only reason to link a second time.
build/services/matched.stamp: $(LINK_DEPS)
	@mkdir -p $(dir $@)
	$(PYTHON) tools/link_matched.py --rom $(ROM)
	@touch $@

$(C_OBJS): build/services/matched.stamp
	@if [ ! -s $@ ]; then $(PYTHON) tools/link_matched.py --rom $(ROM); touch build/services/matched.stamp; fi

probe:
	$(PYTHON) tools/probe_compiler.py

progress: split $(ASM_OBJS) $(C_OBJS) probe
	$(PYTHON) tools/progress.py
