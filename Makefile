# Atomiswave BIOS matching build.
# The ROM stays outside the repo. Override ROM if it lives somewhere else.

ROM ?= $(HOME)/Documents/awbios/bios0.ic23
PYTHON ?= python3

.PHONY: all split asm expected config probe progress

all: progress

split:
	$(PYTHON) tools/split.py $(ROM)

asm: split
	@mkdir -p build/asm/boot
	$(PYTHON) tools/as_sh.py asm/boot/mix_shifts.s -o build/asm/boot/mix_shifts.o --check $(ROM)
	$(PYTHON) tools/as_sh.py asm/boot/copy_words.s -o build/asm/boot/copy_words.o --check $(ROM)
	$(PYTHON) tools/as_sh.py asm/boot/poll_bit.s -o build/asm/boot/poll_bit.o --check $(ROM)

expected: split
	$(PYTHON) tools/gen_objdiff.py --rom $(ROM)

config: expected

probe:
	$(PYTHON) tools/probe_compiler.py

progress: asm config probe
	$(PYTHON) tools/progress.py

# objdiff rebuilds one base object with: make <path>
build/asm/boot/%.o: asm/boot/%.s
	@mkdir -p $(dir $@)
	$(PYTHON) tools/as_sh.py $< -o $@ --check $(ROM)
