# Atomiswave BIOS matching build.
# The ROM stays outside the repo. Override ROM if it lives somewhere else.
# Object recipes are real files. A newer object that no longer matches flash
# is not rebuilt over, and tools/progress.py rejects it.

ROM ?= $(HOME)/Documents/awbios/bios0.ic23
PYTHON ?= python3

ASM_SRCS := $(wildcard asm/boot/*.s) $(wildcard asm/services/*.s) $(wildcard asm/data/*.s)
ASM_OBJS := $(patsubst asm/%.s,build/asm/%.o,$(ASM_SRCS))
C_OBJ := build/services/FUN_09e34.o

.PHONY: all split probe progress config

all: progress

split:
	$(PYTHON) tools/split.py $(ROM)

build/asm/%.o: asm/%.s
	@mkdir -p $(dir $@)
	$(PYTHON) tools/as_sh.py $< -o $@ --check $(ROM)

$(C_OBJ): src/services.c tools/link_matched.py tools/sh4.py
	@mkdir -p $(dir $@)
	$(PYTHON) tools/link_matched.py --rom $(ROM) -o $@

config: split $(ASM_OBJS) $(C_OBJ)
	$(PYTHON) tools/gen_objdiff.py --rom $(ROM)

probe:
	$(PYTHON) tools/probe_compiler.py

progress: config probe
	$(PYTHON) tools/progress.py

# objdiff rebuilds one base object with: make <path>
