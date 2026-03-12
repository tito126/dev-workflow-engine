# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Exec Commands

### Long-Running Commands

**Always use yieldMs for commands that take >10 seconds:**

```python
exec(
    command="python script.py",
    workdir="...",
    yieldMs=10000  # Yield after 10 seconds
)
```

**Why:**
- Without yieldMs, I hang and can't respond to you
- With yieldMs, I can tell you progress and do other things
- After yield, use `process(action=poll)` to check status

**Workflow:**
1. Command starts, yields after 10s if still running
2. I tell you "Running, will check progress..."
3. I poll every 1-2 minutes and update you
4. When done, I report the results

**Examples of long-running commands:**
- Log inspection (10+ minutes)
- Large file processing
- Network operations
- Build/compile tasks

---

Add whatever helps you do your job. This is your cheat sheet.
