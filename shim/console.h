#pragma once
#include <stdint.h>
#include "a52s_profile.h"

#define FB_BASE		A52S_FB_BASE
#define FB_W		A52S_FB_WIDTH
#define FB_H		A52S_FB_HEIGHT
#define FB_STRIDE	A52S_FB_STRIDE	/* a8r8g8b8, matches live splash */

_Static_assert(FB_STRIDE == FB_W * 4, "A52s splash format must stay XRGB8888");

#define RED	0xffff0000U
#define BLUE	0xff0000a0U
#define WHITE	0xffffffffU
#define YELLOW	0xffffff00U
#define GREEN	0xff00ff00U

extern volatile uint32_t *con_fb;

void con_clear(uint32_t bg);
/* Solid-colour band at the top; height in pixels (1 text row = 48 px). */
void con_top_band(uint32_t color, int height);
void con_skip(void);
void con_str(const char *label, const char *s);
void con_hex(const char *label, uint64_t v);
/* label, then "a=xxxxxxxx b=xxxxxxxx" style pairs of 32-bit values */
void con_hex2(const char *label, const char *a, uint32_t va, const char *b, uint32_t vb);
