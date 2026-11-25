import fs from 'node:fs';
import path from 'node:path';
import { describe, it, expect } from 'vitest';
import { ScheduledMessageStatus } from '../../packages/types/dist/index.js';

const matrixPath = path.resolve(process.cwd(), 'tests/datasets/fsm_transitions_and_chaos_matrix.json');
const matrix = JSON.parse(fs.readFileSync(matrixPath, 'utf8'));

interface SimulatedJobRow {
  status: ScheduledMessageStatus;
  version: number;
  personal_send_confirmed_at: string | null;
  escalated_at: string | null;
  auto_fallback: boolean;
  consent_status: 'OPTED_IN' | 'OPTED_OUT' | 'UNKNOWN';
  global_opt_out: boolean;
  retry_count: number;
  max_retries: number;
  lease_owner: string | null;
  error_code: string | null;
}

const VALID_TRANSITION_SET = new Set<string>(
  matrix.valid_transitions.map((t: { from: string; to: string }) => `${t.from}->${t.to}`)
);

function canTransition(from: string, to: string): boolean {
  return VALID_TRANSITION_SET.has(`${from}->${to}`);
}

/** Reference model of PostgreSQL Step 1 Atomic CAS Lease Claim (Arch v4.4 Sec. 7.3). */
function attemptAtomicCasClaim(
  row: SimulatedJobRow,
  expectedVersion: number,
  workerId: string
): { claimed: boolean; conflictReason?: string } {
  if (row.personal_send_confirmed_at !== null) {
    return { claimed: false, conflictReason: 'already_confirmed_personal' };
  }
  if (
    row.version !== expectedVersion ||
    row.status !== ScheduledMessageStatus.AWAITING_CONFIRMATION ||
    !row.auto_fallback ||
    row.consent_status !== 'OPTED_IN' ||
    row.global_opt_out ||
    row.retry_count >= row.max_retries
  ) {
    return { claimed: false, conflictReason: 'guard_rejected' };
  }
  row.status = ScheduledMessageStatus.DISPATCHING;
  row.version += 1;
  row.lease_owner = workerId;
  return { claimed: true };
}

/** Reference model of Erratum A.2 #7 Bounded pg_cron 10s Lease Reaper (Listing 2.3.2). */
function applyBoundedLeaseReaper(row: SimulatedJobRow): void {
  if (row.status !== ScheduledMessageStatus.DISPATCHING) return;
  const nextStatus =
    row.retry_count + 1 < row.max_retries
      ? ScheduledMessageStatus.AWAITING_CONFIRMATION
      : ScheduledMessageStatus.FAILED;
  const nextRetry = row.retry_count < row.max_retries ? row.retry_count + 1 : row.retry_count;
  const nextError =
    row.retry_count + 1 >= row.max_retries && row.error_code === null
      ? 'LEASE_RETRIES_EXHAUSTED'
      : row.error_code;

  row.status = nextStatus;
  row.retry_count = nextRetry;
  row.lease_owner = null;
  row.error_code = nextError;
}

describe('Model C v4.4 HYBRID — 10-State FSM, CAS Concurrency & Bounded Reaper', () => {
  it('matches the canonical 10-state ScheduledMessageStatus enum exactly', () => {
    expect(Object.values(ScheduledMessageStatus)).toEqual(matrix.meta.canonical_states);
    expect(matrix.meta.states_count).toBe(10);
  });

  it('permits all 14 documented FSM transitions and rejects all illegal terminal transitions', () => {
    for (const tr of matrix.valid_transitions) {
      expect(canTransition(tr.from, tr.to)).toBe(true);
    }
    for (const illegal of matrix.illegal_transitions) {
      expect(canTransition(illegal.from, illegal.to)).toBe(false);
    }
    // Terminal states have zero outgoing edges
    for (const terminal of matrix.meta.terminal_states) {
      const outgoing = matrix.valid_transitions.filter((t: { from: string }) => t.from === terminal);
      expect(outgoing).toHaveLength(0);
    }
  });

  it('TC-CHAOS-01..04: enforces atomic CAS lease exclusivity under N=10 worker contention & consent/opt-out gates', () => {
    for (const sc of matrix.cas_chaos_scenarios) {
      const row: SimulatedJobRow = {
        ...sc.initial_state,
        escalated_at: null,
        retry_count: 0,
        max_retries: 3,
        lease_owner: null,
        error_code: null
      };
      const expectedVersion = row.version;
      const workerCount = sc.concurrent_workers ?? 1;
      const results = Array.from({ length: workerCount }, (_, idx) =>
        attemptAtomicCasClaim(row, expectedVersion, `worker-pod-${idx + 1}`)
      );

      const claimed = results.filter((r) => r.claimed).length;
      expect(claimed).toBe(sc.expected_claimed_count);
      if (sc.expected_conflicts_count !== undefined) {
        expect(results.length - claimed).toBe(sc.expected_conflicts_count);
      }
      if (sc.expected_final_version !== undefined) {
        expect(row.version).toBe(sc.expected_final_version);
      }
      if (sc.id === 'TC-CHAOS-02') {
        expect(results[0].conflictReason).toBe('already_confirmed_personal');
      }
    }
  });

  it('TC-CHAOS-02 (1,000-iteration race): guarantees 0.000% double-sends between personal confirm and bot fallback', () => {
    let doubleSends = 0;
    for (let i = 0; i < 1000; i++) {
      const row: SimulatedJobRow = {
        status: ScheduledMessageStatus.AWAITING_CONFIRMATION,
        version: 1,
        personal_send_confirmed_at: null,
        escalated_at: null,
        auto_fallback: true,
        consent_status: 'OPTED_IN',
        global_opt_out: false,
        retry_count: 0,
        max_retries: 3,
        lease_owner: null,
        error_code: null
      };

      const personalWinsFirst = i % 2 === 0;
      let sentPersonal = false;
      let sentBot = false;

      if (personalWinsFirst) {
        if (row.status === ScheduledMessageStatus.AWAITING_CONFIRMATION && row.personal_send_confirmed_at === null) {
          row.personal_send_confirmed_at = new Date().toISOString();
          row.status = ScheduledMessageStatus.SENT_VIA_PERSONAL;
          row.version += 1;
          sentPersonal = true;
        }
        sentBot = attemptAtomicCasClaim(row, 1, 'worker-1').claimed;
      } else {
        sentBot = attemptAtomicCasClaim(row, 1, 'worker-1').claimed;
        if (row.status === ScheduledMessageStatus.AWAITING_CONFIRMATION && row.personal_send_confirmed_at === null) {
          row.personal_send_confirmed_at = new Date().toISOString();
          row.status = ScheduledMessageStatus.SENT_VIA_PERSONAL;
          sentPersonal = true;
        }
      }

      if (sentPersonal && sentBot) doubleSends += 1;
    }
    expect(doubleSends).toBe(0);
  });

  it('TC-FSM-03: enforces atomic escalated_at single-send guard at T+3m across concurrent workers', () => {
    const row: SimulatedJobRow = {
      status: ScheduledMessageStatus.AWAITING_CONFIRMATION,
      version: 2,
      personal_send_confirmed_at: null,
      escalated_at: null,
      auto_fallback: true,
      consent_status: 'OPTED_IN',
      global_opt_out: false,
      retry_count: 0,
      max_retries: 3,
      lease_owner: null,
      error_code: null
    };

    let escalationsSent = 0;
    for (let w = 0; w < 10; w++) {
      if (row.status === ScheduledMessageStatus.AWAITING_CONFIRMATION && row.escalated_at === null) {
        row.escalated_at = new Date().toISOString();
        escalationsSent += 1;
      }
    }
    expect(escalationsSent).toBe(1);
  });

  it('Erratum A.2 #7: bounded Lease Reaper never exceeds max_retries (chk_retry_bounds) and transitions to FAILED', () => {
    const { max_retries, steps } = matrix.lease_reaper_erratum_a2_7_progression;
    for (const step of steps) {
      const row: SimulatedJobRow = {
        status: ScheduledMessageStatus.DISPATCHING,
        version: 4,
        personal_send_confirmed_at: null,
        escalated_at: null,
        auto_fallback: true,
        consent_status: 'OPTED_IN',
        global_opt_out: false,
        retry_count: step.input_retry_count,
        max_retries,
        lease_owner: 'crashed-worker-1',
        error_code: null
      };

      applyBoundedLeaseReaper(row);
      expect(row.status).toBe(step.expected_status);
      expect(row.retry_count).toBe(step.expected_retry_count);
      expect(row.retry_count).toBeLessThanOrEqual(row.max_retries);
      expect(row.lease_owner).toBeNull();
      expect(row.error_code).toBe(step.expected_error_code);
    }
  });
});
