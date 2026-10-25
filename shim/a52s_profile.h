#pragma once

/*
 * Samsung Galaxy A52s 5G (a52sxq / SM-A528B) bring-up profile.
 *
 * The numeric values below are locked to the live recovery dumps supplied for
 * this handset.  Keep this header free of inferred register offsets: the shim
 * includes it directly and tools/mkadt.py parses it, so it is the single
 * source of truth for the values they share.
 */

/* /arm-io has a non-zero parent range in Apple's ADT. */
#define A52S_SOC_BASE             0x01000000UL

#define A52S_GICD_BASE            0x17a00000UL
#define A52S_GICD_SIZE            0x00010000UL
#define A52S_GICR_BASE            0x17a60000UL
#define A52S_GICR_SIZE            0x00100000UL
#define A52S_TIMER_BASE           0x17c20000UL
#define A52S_TIMER_FRAME_BASE     0x17c21000UL
#define A52S_TIMEBASE_HZ          19200000UL

#define A52S_UFS_HOST_BASE        0x01d84000UL
#define A52S_UFS_HOST_SIZE        0x00003000UL
#define A52S_UFS_PHY_BASE         0x01d87000UL
#define A52S_UFS_ICE_BASE         0x01d88000UL
#define A52S_UFS_IRQ              297U

#define A52S_FB_BASE              0xe1000000UL
#define A52S_FB_SIZE              0x02300000UL
#define A52S_FB_WIDTH             1080U
#define A52S_FB_HEIGHT            2400U
#define A52S_FB_STRIDE            4320U
#define A52S_MDSS_BASE            0x0ae00000UL

#define A52S_TLMM_BASE            0x0f000000UL
#define A52S_TOUCH_GENI_BASE      0x00a94000UL
#define A52S_TOUCH_I2C_ADDR       0x49U
#define A52S_TOUCH_IRQ_GPIO       81U
#define A52S_TOUCH_MAX_X          4096U
#define A52S_TOUCH_MAX_Y          4096U
#define A52S_TOUCH_MAX_CONTACTS   10U
#define A52S_TOUCH_AVDD_LDO       7U /* PM8350C L7 / pm8350c_l7 */

/* MPIDR Aff1:Aff0 values are 0x0000, 0x0100, ..., 0x0700. */
#define A52S_CPU_COUNT            8U
#define A52S_CPU_LITTLE_COUNT     4U /* Cortex-A55, MIDR part 0xd05 */
#define A52S_CPU_PERF_COUNT       4U /* Cortex-A78, MIDR part 0xd41 */
