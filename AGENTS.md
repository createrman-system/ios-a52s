# Working on ios-sweet

- Read `NOTES.md` before starting; it contains the project goal, hardware facts,
  current blocker, local artifact locations and the next concrete action.
- The user switches agents frequently. Update the active handoff in `NOTES.md`
  after each milestone and before stopping. Record commits, CI run IDs, exact
  build/boot results and unfinished work. Distinguish observations from guesses.
- Commit completed changes. Use `gh` for GitHub Actions kernel builds and logs.
  Local single-file cross-compiles are useful before spending a CI run.
- Device boot paths are device-specific: Xiaomi `sweet` supports temporary
  `fastboot boot`; Samsung Galaxy A52s does not. A52s testing uses Samsung
  Download Mode (Odin/LOKE; Heimdall client) and writes the selected partition,
  so never describe an AP tar as a temporary boot. Preserve Android and
  backups. The user approved internal UFS for iOS on 2026-10-15, but confirm the
  specific partition/write operation before it is performed; confirm destructive
  userdata writes separately. Keep bootloaders, recovery, modem, persist and
  backups intact.
- Keep device dumps, serial numbers and downloaded Apple artifacts out of git.
