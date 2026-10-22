import os, subprocess, shutil, stat

def remove_readonly(func, path, excinfo):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

if os.path.exists('test_apply'):
    shutil.rmtree('test_apply', onexc=remove_readonly)

os.makedirs('test_apply/bsd/dev', exist_ok=True)

# 1. Put base file
with open('sweet_touch_03defe6.c', 'r', encoding='latin1') as f:
    base_text = f.read()

with open('test_apply/bsd/dev/sweet_touch.c', 'w', encoding='latin1', newline='\n') as out:
    out.write(base_text)

subprocess.run(['git', 'init'], cwd='test_apply', capture_output=True)
subprocess.run(['git', 'config', 'user.name', 'test'], cwd='test_apply', capture_output=True)
subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd='test_apply', capture_output=True)
subprocess.run(['git', 'add', 'bsd/dev/sweet_touch.c'], cwd='test_apply', capture_output=True)
subprocess.run(['git', 'commit', '-m', 'base'], cwd='test_apply', capture_output=True)

# 2. Modify base text
text = base_text

# 1. Add TOUCH_WEST_PA
target1 = '#define TOUCH_NORTH_PA   0x03900000u /* DT TLMM + NORTH (0x500000) */\n'
repl1 = target1 + '#define TOUCH_WEST_PA    0x03500000u /* DT TLMM + WEST  (0x100000) */\n'
assert target1 in text, 'target1 not found'
text = text.replace(target1, repl1, 1)

# 2. Add SEC_TS defines
target2 = '#define TOUCH_FTS        2\n'
repl2 = target2 + '''#define TOUCH_SEC_TS     3

#define SEC_TS_I2C_ADDR  0x48
#define SEC_TS_READ_ID   0x52
#define SEC_TS_READ_ONE_EVENT 0x60
#define SEC_TS_CMD_SENSE_ON 0x10
#define SEC_TS_CMD_CLEAR_EVENT_STACK 0x62
#define SEC_TS_COORDINATE_EVENT 0
#define SEC_TS_STATUS_EVENT     1
#define SEC_TS_EVENT_BUFF_SIZE  16
#define SEC_TS_COORDINATE_ACTION_PRESS   1
#define SEC_TS_COORDINATE_ACTION_MOVE    2
#define SEC_TS_COORDINATE_ACTION_RELEASE 3
'''
assert target2 in text, 'target2 not found'
text = text.replace(target2, repl2, 1)

# 3. Add gpio_west
target3 = 'static struct {\n\tvm_offset_t se, gcc, gpio;\n'
repl3 = 'static struct {\n\tvm_offset_t se, gcc, gpio, gpio_west;\n'
assert target3 in text, 'target3 not found'
text = text.replace(target3, repl3, 1)

# 4. Add touch_gpio_west and touch_power_dvdd
target4 = 'static bool\ntouch_clocks(void)\n'
repl4 = '''static void
touch_gpio_west(unsigned pin, unsigned mux, unsigned pull, unsigned drive, bool out, bool high)
{
\tif (!st.gpio_west) {
\t\treturn;
\t}
\tuint32_t off = TOUCH_GPIO_CFG(pin);
\tif (out) {
\t\ttouch_wr(st.gpio_west, TOUCH_GPIO_IO(pin),
\t\t    (touch_rd(st.gpio_west, TOUCH_GPIO_IO(pin)) & ~2u) | (high ? 2u : 0u));
\t}
\tuint32_t cfg = touch_rd(st.gpio_west, off);
\tcfg &= ~0x3ffu;
\tcfg |= (mux << 2) | pull | (drive << 6) | (out ? 0x200u : 0u);
\ttouch_wr(st.gpio_west, off, cfg);
}

static void
touch_power_dvdd(void)
{
\tvm_offset_t core = ml_io_map(0x0c440000u, 0x2000);
\tvm_offset_t cnfg = ml_io_map(0x0c40a000u, 0x1000);
\tvm_offset_t obs  = ml_io_map(0x0e600000u, 0x10000);
\tif (!core || !cnfg || !obs) {
\t\tprintf("SWEET TOUCH: SPMI map failed\\n");
\t\treturn;
\t}
\tuint32_t count = touch_rd(core, 4) & 0x7ffu;
\tuint16_t apid = 0xffffu;
\tfor (uint32_t i = 0; i < count; ++i) {
\t\tuint32_t map = touch_rd(core, 0x900u + 4u * i);
\t\tif (((map >> 8) & 0xfffu) == 0x0c3u) {
\t\t\tuint32_t owner = touch_rd(cnfg, 0x700u + 4u * i) & 7u;
\t\t\tif (apid == 0xffffu || owner == 0) {
\t\t\t\tapid = (uint16_t)i;
\t\t\t}
\t\t}
\t}
\tif (apid == 0xffffu) {
\t\tprintf("SWEET TOUCH: PM6150 GPIO4 APID not found\\n");
\t\treturn;
\t}
\tuint32_t obs_off = 0x80u * apid;
\tuint8_t en = 0, out = 0;
\ttouch_wr(obs, obs_off, (1u << 27) | (0x46u << 4));
\tfor (int j = 0; j < 500; j++) { if (touch_rd(obs, obs_off + 8) & 1u) { en = (uint8_t)touch_rd(obs, obs_off + 0x18); break; } delay(1); }
\ttouch_wr(obs, obs_off, (1u << 27) | (0x45u << 4));
\tfor (int j = 0; j < 500; j++) { if (touch_rd(obs, obs_off + 8) & 1u) { out = (uint8_t)touch_rd(obs, obs_off + 0x18); break; } delay(1); }
\tprintf("SWEET TOUCH: PM6150 GPIO4 apid=%u init en=%#x out=%#x\\n", apid, en, out);

\tvm_offset_t chnl = ml_io_map(0x0c600000u + 0x10000u * (vm_offset_t)apid, 0x1000);
\tif (chnl) {
\t\ttouch_wr(chnl, 0x10, 1u);
\t\ttouch_wr(chnl, 0x00, (0u << 27) | (0x45u << 4) | 0u);
\t\tfor (int j = 0; j < 500; j++) { if (touch_rd(chnl, 8) & 1u) break; delay(1); }
\t\ttouch_wr(chnl, 0x10, 1u);
\t\ttouch_wr(chnl, 0x00, (0u << 27) | (0x40u << 4) | 0u);
\t\tfor (int j = 0; j < 500; j++) { if (touch_rd(chnl, 8) & 1u) break; delay(1); }
\t\ttouch_wr(chnl, 0x10, 0x80u);
\t\ttouch_wr(chnl, 0x00, (0u << 27) | (0x46u << 4) | 0u);
\t\tfor (int j = 0; j < 500; j++) { if (touch_rd(chnl, 8) & 1u) break; delay(1); }
\t\ttouch_wr(obs, obs_off, (1u << 27) | (0x46u << 4));
\t\tfor (int j = 0; j < 500; j++) { if (touch_rd(obs, obs_off + 8) & 1u) { en = (uint8_t)touch_rd(obs, obs_off + 0x18); break; } delay(1); }
\t\ttouch_wr(obs, obs_off, (1u << 27) | (0x45u << 4));
\t\tfor (int j = 0; j < 500; j++) { if (touch_rd(obs, obs_off + 8) & 1u) { out = (uint8_t)touch_rd(obs, obs_off + 0x18); break; } delay(1); }
\t\tprintf("SWEET TOUCH: PM6150 GPIO4 DVDD active en=%#x out=%#x\\n", en, out);
\t}
}

static bool
touch_clocks(void)
'''
assert target4 in text, 'target4 not found'
text = text.replace(target4, repl4, 1)

# 5. Add touch_sec_ts
target5 = 'static bool\ntouch_se_init(void)\n'
repl5 = '''static int
touch_sec_ts(void)
{
\tuint32_t mask = st.active;
\tint x[TOUCH_MAX], y[TOUCH_MAX];
\tfor (unsigned i = 0; i < TOUCH_MAX; ++i) {
\t\tx[i] = st.x[i];
\t\ty[i] = st.y[i];
\t}

\tint events = 0;
\twhile (events++ < 16) {
\t\tuint8_t buf[SEC_TS_EVENT_BUFF_SIZE] = {0};
\t\tint err = touch_read(SEC_TS_I2C_ADDR, SEC_TS_READ_ONE_EVENT, false, buf, sizeof(buf));
\t\tif (err) {
\t\t\treturn err;
\t\t}
\t\tif (buf[0] == 0 || (buf[0] & 3u) == 3u) {
\t\t\tbreak; /* Buffer empty */
\t\t}
\t\tuint8_t eid = buf[0] & 3u;
\t\tif (eid == SEC_TS_COORDINATE_EVENT) {
\t\t\tuint8_t tid = (buf[0] >> 2) & 0x0fu;
\t\t\tuint8_t tchsta = (buf[0] >> 6) & 0x03u;
\t\t\tif (tid >= 1 && tid <= TOUCH_MAX) {
\t\t\t\tunsigned id = tid - 1u;
\t\t\t\tunsigned raw_x = ((unsigned)buf[1] << 4) | ((buf[3] >> 4) & 0x0fu);
\t\t\t\tunsigned raw_y = ((unsigned)buf[2] << 4) | (buf[3] & 0x0fu);
\t\t\t\tunsigned px = raw_x > 1079u ? (raw_x * 1080u) / 4096u : raw_x;
\t\t\t\tunsigned py = raw_y > 2399u ? (raw_y * 2400u) / 4096u : raw_y;
\t\t\t\tif (px > 1079u) px = 1079u;
\t\t\t\tif (py > 2399u) py = 2399u;

\t\t\t\tif (tchsta == SEC_TS_COORDINATE_ACTION_PRESS ||
\t\t\t\t    tchsta == SEC_TS_COORDINATE_ACTION_MOVE) {
\t\t\t\t\tmask |= (1u << id);
\t\t\t\t\tx[id] = (int)px;
\t\t\t\t\ty[id] = (int)py;
\t\t\t\t} else if (tchsta == SEC_TS_COORDINATE_ACTION_RELEASE) {
\t\t\t\t\tmask &= ~(1u << id);
\t\t\t\t}
\t\t\t}
\t\t} else if (eid == SEC_TS_STATUS_EVENT) {
\t\t\tuint8_t stype = (buf[0] >> 2) & 0x0fu;
\t\t\tif (stype == 1u) { /* ERR event */
\t\t\t\tconst uint8_t cmd_clear = SEC_TS_CMD_CLEAR_EVENT_STACK;
\t\t\t\t(void)touch_msg(SEC_TS_I2C_ADDR, &cmd_clear, 1, NULL, 0, false);
\t\t\t\tmask = 0;
\t\t\t}
\t\t}
\t\tuint8_t left = buf[7] & 0x1fu;
\t\tif (left == 0) {
\t\t\tbreak;
\t\t}
\t}
\ttouch_report(mask, x, y);
\treturn 0;
}

static bool
touch_se_init(void)
'''
assert target5 in text, 'target5 not found'
text = text.replace(target5, repl5, 1)

# 6. Remove 0x64 check
target6 = 'if (((fw >> 8) & 0xffu) != 3u || (touch_rd(st.se, 0x64) & 1u) ||\n'
repl6   = 'if (((fw >> 8) & 0xffu) != 3u ||\n'
assert target6 in text, 'target6 not found'
text = text.replace(target6, repl6, 1)

# 7. Delay_s = 3
target7 = 'unsigned delay_s = 45;\n'
repl7   = 'unsigned delay_s = 3;\n'
assert target7 in text, 'target7 not found'
text = text.replace(target7, repl7, 1)

# 8. Add st.gpio_west mapping
target8 = '\tst.gpio = ml_io_map(TOUCH_NORTH_PA, 0x5b000);\n\tst.se = ml_io_map(TOUCH_SE_PA, 0x4000);\n'
repl8   = '\tst.gpio = ml_io_map(TOUCH_NORTH_PA, 0x5b000);\n\tst.gpio_west = ml_io_map(TOUCH_WEST_PA, 0x40000);\n\tst.se = ml_io_map(TOUCH_SE_PA, 0x4000);\n'
assert target8 in text, 'target8 not found'
text = text.replace(target8, repl8, 1)

# 9. Power sequence, pin configuration, probe and main loop
old_block = '''\t/* Keep the IC in reset while its rails settle; IRQ stays an input. */
\ttouch_gpio(9, 0, 3, 3, false, false); /* IRQ input, 8 mA, pull-up */
\ttouch_gpio(8, 0, 3, 3, true, false);
\tint power_error = sweet_rpmh_vreg_enable("ldoc11", 3200);
\tif (power_error) {
\t\tprintf("SWEET TOUCH: L11C RPMh enable failed %d; probes skipped\\n", power_error);
\t\tgoto out;
\t}
\ttouch_gpio(90, 0, 0, 0, true, true); /* board digital power enable */
\ttouch_wait(10); /* conservative rail settling; not a DT timing value */
\ttouch_gpio(6, 1, 0, 0, false, false); /* qup11 SDA/SCL, 2 mA */
\ttouch_gpio(7, 1, 0, 0, false, false);
\t/* Vendor GT9896 dev_confirm: reset low 2 ms, then high. */
\ttouch_gpio(8, 0, 3, 3, true, false);
\ttouch_wait(2);
\ttouch_gpio(8, 0, 3, 3, true, true);
\ttouch_wait(300); /* exceeds vendor 5 ms test + 95 ms post-test wait */
\tuint8_t gid[32], legacy[32], fid1 = 0, fid2 = 0;
\tst.probing = true;
\tint ge = touch_probe_info(GOODIX_PID_REG, gid);
\tprintf("SWEET TOUCH: probe 0x5d err=%d pid=%02x%02x%02x%02x fw=%02x.%02x.%02x.%02x irq=%#x\\n",
\t    ge, gid[0], gid[1], gid[2], gid[3], gid[8], gid[9], gid[10], gid[11], st.irq_status);
\t(void)touch_probe_info(0x8240, legacy);
\tint fe1 = touch_read(0x38, 0xa3, false, &fid1, 1);
\tint fe2 = touch_read(0x38, 0x9f, false, &fid2, 1);
\tprintf("SWEET TOUCH: probe 0x38 err=%d/%d chip-id=%02x:%02x irq=%#x\\n",
\t    fe1, fe2, fid1, fid2, st.irq_status);
\tst.probing = false;
\tbool goodix = !ge && gid[0] == '9' && gid[1] == '8' && gid[2] == '9' && gid[3] == '6';
\tbool fts = !fe1 && !fe2 && fid1 == 0x54 && fid2 == 0x52;
\tif (st.dead || goodix == fts) {
\t\tprintf("SWEET TOUCH: no unique supported IC (goodix=%d fts=%d dead=%d); stopping\\n",
\t\t    goodix, fts, st.dead);
\t\tgoto out;
\t}
\tst.kind = goodix ? TOUCH_GOODIX : TOUCH_FTS;
\tprintf("SWEET TOUCH: selected %s, 1080x2400, poll=10ms irq-hint=%d\\n",
\t    goodix ? "GT9896 Yellowstone" : "Focaltech 54:52", st.irq_hint);
\tunsigned errors = 0, ticks = 0;
\twhile (!st.dead) {
\t\t/* Optional IRQ hint still reads every 100ms, and always while down. */
\t\tif (!st.irq_hint || st.active || !(touch_rd(st.gpio, TOUCH_GPIO_IO(9)) & 1u) ||
\t\t    (++ticks % 10u) == 0) {
\t\t\tint err = st.kind == TOUCH_GOODIX ? touch_goodix() : touch_focaltech();
\t\t\tif (err) {
\t\t\t\tif ((errors++ % 100u) == 0) {
\t\t\t\t\tprintf("SWEET TOUCH: report err=%d irq=%#x\\n", err, st.irq_status);
\t\t\t\t}
\t\t\t\tif (errors == 10) {
\t\t\t\t\ttouch_report(0, st.x, st.y); /* release after persistent bad reads */
\t\t\t\t}
\t\t\t} else {
\t\t\t\terrors = 0;
\t\t\t}
\t\t}
\t\ttouch_wait(10);
\t}'''

new_block = '''\tint power_error = sweet_rpmh_vreg_enable("ldoc11", 3200);
\tif (power_error) {
\t\tprintf("SWEET TOUCH: L11C RPMh enable returned %d; continuing\\n", power_error);
\t}
\t/* Samsung Galaxy A71 tsp_ldo_avdd / tsp_ldo_en is on GPIO 56 (WEST tile) */
\ttouch_gpio_west(56, 0, 0, 0, true, true);
\tprintf("SWEET TOUCH: GPIO56 (AVDD) cfg=%#x io=%#x\\n",
\t    st.gpio_west ? touch_rd(st.gpio_west, TOUCH_GPIO_CFG(56)) : 0,
\t    st.gpio_west ? touch_rd(st.gpio_west, TOUCH_GPIO_IO(56)) : 0);

\t/* Samsung Galaxy A71 tsp_int_dvdd_en is on PM6150 GPIO 4 (SPMI) */
\ttouch_power_dvdd();

\t/* Allow power supplies to settle and IC to finish POR */
\ttouch_wait(100);

\t/* Configure IRQ (GPIO 9): input, active-low, internal pull-up */
\ttouch_gpio(9, 0, 3, 2, false, false);

\t/* Configure I2C SDA (GPIO 6) and SCL (GPIO 7): qup11, internal pull-up, 6 mA */
\ttouch_gpio(6, 1, 3, 2, false, false);
\ttouch_gpio(7, 1, 3, 2, false, false);

\t/* Diagnostic: check physical line levels (1 = idle high) */
\tprintf("SWEET TOUCH: bus pins SDA(6)=%u SCL(7)=%u IRQ(9)=%u\\n",
\t    touch_rd(st.gpio, TOUCH_GPIO_IO(6)) & 1u,
\t    touch_rd(st.gpio, TOUCH_GPIO_IO(7)) & 1u,
\t    touch_rd(st.gpio, TOUCH_GPIO_IO(9)) & 1u);
\tuint8_t gid[32], legacy[32], fid1 = 0, fid2 = 0;
\tst.probing = true;
\tint ge = touch_probe_info(GOODIX_PID_REG, gid);
\tprintf("SWEET TOUCH: probe 0x5d err=%d pid=%02x%02x%02x%02x fw=%02x.%02x.%02x.%02x irq=%#x\\n",
\t    ge, gid[0], gid[1], gid[2], gid[3], gid[8], gid[9], gid[10], gid[11], st.irq_status);
\t(void)touch_probe_info(0x8240, legacy);
\tint fe1 = touch_read(0x38, 0xa3, false, &fid1, 1);
\tint fe2 = touch_read(0x38, 0x9f, false, &fid2, 1);
\tprintf("SWEET TOUCH: probe 0x38 err=%d/%d chip-id=%02x:%02x irq=%#x\\n",
\t    fe1, fe2, fid1, fid2, st.irq_status);
\tuint8_t sid[6] = {0};
\tint se_id = touch_read(SEC_TS_I2C_ADDR, SEC_TS_READ_ID, false, sid, 5);
\tprintf("SWEET TOUCH: probe 0x48 (sec_ts ID) err=%d id='%c%c%c%c' (%02x %02x %02x %02x %02x) irq=%#x\\n",
\t    se_id, sid[0] ? sid[0] : '?', sid[1] ? sid[1] : '?', sid[2] ? sid[2] : '?', sid[3] ? sid[3] : '?',
\t    sid[0], sid[1], sid[2], sid[3], sid[4], st.irq_status);
\tbool sec_ts = !se_id;
\tif (!sec_ts) {
\t\tuint8_t se_ev[8] = {0};
\t\tint se_ev_err = touch_read(SEC_TS_I2C_ADDR, SEC_TS_READ_ONE_EVENT, false, se_ev, sizeof(se_ev));
\t\tprintf("SWEET TOUCH: probe 0x48 (one_event) err=%d ev0=%02x ev1=%02x\\n", se_ev_err, se_ev[0], se_ev[1]);
\t\tsec_ts = !se_ev_err;
\t}
\tuint8_t im_id[4] = {0};
\tint im_err = touch_read(0x50, 0x00, false, im_id, 4);
\tprintf("SWEET TOUCH: probe 0x50 (imagis) err=%d id=%02x %02x %02x %02x\\n",
\t    im_err, im_id[0], im_id[1], im_id[2], im_id[3]);
\tst.probing = false;
\tbool goodix = !ge && gid[0] == '9' && gid[1] == '8' && gid[2] == '9' && gid[3] == '6';
\tbool fts = !fe1 && !fe2 && fid1 == 0x54 && fid2 == 0x52;
\tif (st.dead || (!goodix && !fts && !sec_ts)) {
\t\tprintf("SWEET TOUCH: no supported IC (goodix=%d fts=%d sec_ts=%d dead=%d); stopping\\n",
\t\t    goodix, fts, sec_ts, st.dead);
\t\tgoto out;
\t}
\tif (sec_ts) {
\t\tst.kind = TOUCH_SEC_TS;
\t\tconst uint8_t cmd_sense = SEC_TS_CMD_SENSE_ON;
\t\tconst uint8_t cmd_clear = SEC_TS_CMD_CLEAR_EVENT_STACK;
\t\t(void)touch_msg(SEC_TS_I2C_ADDR, &cmd_sense, 1, NULL, 0, false);
\t\ttouch_wait(10);
\t\t(void)touch_msg(SEC_TS_I2C_ADDR, &cmd_clear, 1, NULL, 0, false);
\t} else if (goodix) {
\t\tst.kind = TOUCH_GOODIX;
\t} else {
\t\tst.kind = TOUCH_FTS;
\t}
\tprintf("SWEET TOUCH: selected %s, 1080x2400, poll=10ms irq-hint=%d\\n",
\t    (st.kind == TOUCH_SEC_TS) ? "Samsung S6SY771 (sec_ts)" :
\t    (st.kind == TOUCH_GOODIX) ? "GT9896 Yellowstone" : "Focaltech 54:52", st.irq_hint);
\tunsigned errors = 0, ticks = 0;
\twhile (!st.dead) {
\t\t/* IRQ on GPIO 9 is active LOW when events are pending */
\t\tbool irq_active = !(touch_rd(st.gpio, TOUCH_GPIO_IO(9)) & 1u);
\t\tif (!st.irq_hint || st.active || irq_active ||
\t\t    (++ticks % 10u) == 0) {
\t\t\tint err;
\t\t\tif (st.kind == TOUCH_SEC_TS) {
\t\t\t\terr = touch_sec_ts();
\t\t\t} else if (st.kind == TOUCH_GOODIX) {
\t\t\t\terr = touch_goodix();
\t\t\t} else {
\t\t\t\terr = touch_focaltech();
\t\t\t}
\t\t\tif (err) {
\t\t\t\tif ((errors++ % 100u) == 0) {
\t\t\t\t\tprintf("SWEET TOUCH: report err=%d irq=%#x\\n", err, st.irq_status);
\t\t\t\t}
\t\t\t\tif (errors == 10) {
\t\t\t\t\ttouch_report(0, st.x, st.y); /* release after persistent bad reads */
\t\t\t\t}
\t\t\t} else {
\t\t\t\terrors = 0;
\t\t\t}
\t\t}
\t\ttouch_wait(10);
\t}'''

assert old_block in text, 'old_block not found'
text = text.replace(old_block, new_block, 1)

# Write modified file
with open('test_apply/bsd/dev/sweet_touch.c', 'w', encoding='latin1', newline='\n') as out:
    out.write(text)

# Generate git diff!
diff_res = subprocess.run(['git', 'diff', 'bsd/dev/sweet_touch.c'], cwd='test_apply', capture_output=True, text=True)
patch_text = diff_res.stdout
print('Generated patch length:', len(patch_text))

with open('xnu/patches/0082-sweet-samsung-sec-ts-touch.patch', 'w', encoding='latin1', newline='\n') as out:
    out.write(patch_text)

# Test git apply --check on the base!
subprocess.run(['git', 'checkout', 'HEAD', '--', 'bsd/dev/sweet_touch.c'], cwd='test_apply', capture_output=True)
check_res = subprocess.run(['git', 'apply', '--check', '../xnu/patches/0082-sweet-samsung-sec-ts-touch.patch'], cwd='test_apply', capture_output=True, text=True)
print('GIT APPLY --CHECK EXIT CODE:', check_res.returncode)
if check_res.returncode != 0:
    print('ERROR:', check_res.stderr)
else:
    print('SUCCESS! Patch applies cleanly!')
