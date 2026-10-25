#pragma once
#include <stdint.h>
#include "a52s_profile.h"

#define FB_PHYS	A52S_FB_BASE

struct mmu_info {
	uint64_t img_lo, img_hi, ttbr;
	uint64_t sctlr_before, sctlr_after;
	int n_l3;
};

int mmu_enable(struct mmu_info *info);
uint64_t mmu_probe(uintptr_t va);
