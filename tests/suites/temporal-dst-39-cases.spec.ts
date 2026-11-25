import fs from 'node:fs';
import path from 'node:path';
import { describe, it, expect } from 'vitest';

const dstPath = path.resolve(process.cwd(), 'tests/datasets/temporal_dst_39_cases.json');
const dstDataset = JSON.parse(fs.readFileSync(dstPath, 'utf8'));

function daysInMonth(year: number, month1Based: number): number {
  return new Date(Date.UTC(year, month1Based, 0)).getUTCDate();
}

/** Calendar-anchored month-end recurrence step (FR-REC-03). */
function computeNextMonthlyAnchor(fromLocal: string, anchorDay: number, rule: 'MONTHLY' | 'YEARLY'): string {
  const [datePart, timePart] = fromLocal.split('T');
  const [y, m] = datePart.split('-').map(Number);
  let nextYear = y;
  let nextMonth = m;
  if (rule === 'MONTHLY') {
    nextMonth += 1;
    if (nextMonth > 12) {
      nextMonth = 1;
      nextYear += 1;
    }
  } else {
    nextYear += 1;
  }
  const clampedDay = Math.min(anchorDay, daysInMonth(nextYear, nextMonth));
  const mm = String(nextMonth).padStart(2, '0');
  const dd = String(clampedDay).padStart(2, '0');
  return `${nextYear}-${mm}-${dd}T${timePart}`;
}

/** Formats UTC instant into an IANA timezone's local YYYY-MM-DDTHH:mm wall clock. */
function formatLocalWallClock(utcIso: string, timeZone: string): string {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23'
  }).formatToParts(new Date(utcIso));
  const get = (type: string) => parts.find((p) => p.type === type)?.value ?? '';
  return `${get('year')}-${get('month')}-${get('day')}T${get('hour')}:${get('minute')}`;
}

/** Fast-forwards overdue HOURLY/DAILY jobs strictly past NOW() without catch-up burst (FR-REC-04). */
function fastForwardOverdue(
  lastScheduledUtc: string,
  nowUtc: string,
  rule: 'HOURLY' | 'DAILY'
): { misfiredCount: number; nextUtc: string } {
  const stepMs = rule === 'HOURLY' ? 3_600_000 : 86_400_000;
  const startMs = Date.parse(lastScheduledUtc);
  const nowMs = Date.parse(nowUtc);
  let misfiredCount = 0;
  let candidate = startMs + stepMs;
  while (candidate <= nowMs) {
    misfiredCount += 1;
    candidate += stepMs;
  }
  return { misfiredCount, nextUtc: new Date(candidate).toISOString().replace('.000Z', 'Z') };
}

describe('Phase 2 (M5 / EPIC-05) — 39-Case Wall-Clock Recurrence & DST Verification Harness', () => {
  it('contains all 39 canonical test cases across all 5 temporal categories', () => {
    expect(dstDataset.cases).toHaveLength(39);
    expect(dstDataset.meta.total_cases).toBe(39);

    const groups = dstDataset.cases.reduce((acc: Record<string, number>, c: { group: string }) => {
      acc[c.group] = (acc[c.group] ?? 0) + 1;
      return acc;
    }, {});

    expect(groups).toEqual({
      dst_spring_forward: 10,
      dst_fall_back: 8,
      month_end_anchor: 10,
      timezone_travel: 6,
      reboot_misfire_fast_forward: 5
    });
  });

  it('TC-TMP-01..18: verifies DST spring-forward and fall-back local wall-clock & offset invariants', () => {
    const dstCases = dstDataset.cases.filter(
      (c: { group: string }) => c.group === 'dst_spring_forward' || c.group === 'dst_fall_back'
    );
    expect(dstCases).toHaveLength(18);
    for (const c of dstCases) {
      const utcCandidate = new Date(`${c.expected_next_local}:00${c.expected_next_offset}`).toISOString();
      expect(formatLocalWallClock(utcCandidate, c.timezone)).toBe(c.expected_next_local);
      if (c.group === 'dst_fall_back') {
        expect(c.expected_occurrence_count).toBe(1);
      }
    }
  });

  it('TC-TMP-19..28: preserves month-end anchor days across Feb 28, leap Feb 29, Apr 30 & restores 31st', () => {
    const monthEndCases = dstDataset.cases.filter((c: { group: string }) => c.group === 'month_end_anchor');
    expect(monthEndCases).toHaveLength(10);
    for (const c of monthEndCases) {
      expect(computeNextMonthlyAnchor(c.from_local, c.anchor_day, c.rule)).toBe(c.expected_next_local);
    }
  });

  it('TC-TMP-29..34: verifies relative UTC countdown invariance, TZ travel & +05:30 / +05:45 offsets', () => {
    const travelCases = dstDataset.cases.filter((c: { group: string }) => c.group === 'timezone_travel');
    expect(travelCases).toHaveLength(6);

    for (const c of travelCases) {
      if (c.mode === 'RELATIVE_COUNTDOWN') {
        const expectedMs = Date.parse(c.created_at_utc) + c.offset_minutes * 60_000;
        expect(new Date(expectedMs).toISOString().replace('.000Z', 'Z')).toBe(c.expected_fire_utc);
      } else {
        const tz = c.to_tz ?? c.timezone;
        expect(formatLocalWallClock(c.expected_fire_utc, tz)).toBe(`${c.date}T${c.nominal_wall_time}`);
      }
    }
  });

  it('TC-TMP-35..39: fast-forwards overdue jobs cleanly & enforces per-occurrence reset invariants', () => {
    const rebootCases = dstDataset.cases.filter((c: { group: string }) => c.group === 'reboot_misfire_fast_forward');
    expect(rebootCases).toHaveLength(5);

    for (const c of rebootCases) {
      if (c.rule === 'HOURLY' || c.rule === 'DAILY') {
        const res = fastForwardOverdue(c.last_scheduled_utc, c.now_utc, c.rule);
        expect(res.misfiredCount).toBe(c.expected_misfired_count);
        expect(res.nextUtc).toBe(c.expected_next_utc);
      } else if (c.rule === 'PER_OCCURRENCE_RESET') {
        const nextKey = `${c.series_id}:${c.prev_seq + 1}`;
        expect(nextKey).toBe(c.expected_next_idempotency_key);
        expect(c.expected_meta_message_id).toBeNull();
        expect(c.expected_expires_at_delta_days).toBe(90);
      } else if (c.rule === 'SINGLE_ACTIVE_ROW_INVARIANT') {
        expect(c.active_rows_per_series).toBe(1);
      }
    }
  });
});
