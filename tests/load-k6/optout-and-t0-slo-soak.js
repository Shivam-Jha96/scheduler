import http from 'k6/http';
import { check, sleep } from 'k6';

/**
 * TC-LOAD-02: T0 Dispatch & Instant Two-Tier Opt-Out (<5s SLA) Soak Test
 * Runs against isolated local Dockerized MockAPI_Server with X-Test-Run-Id header
 * and POST /mock/reset teardown so parallel CI runs never collide (M0-T3).
 */
export const options = {
  scenarios: {
    hybrid_and_optout_soak: {
      executor: 'ramping-vus',
      startVUs: 5,
      stages: [
        { duration: '15s', target: 25 },
        { duration: '60s', target: 25 },
        { duration: '15s', target: 0 }
      ]
    }
  },
  thresholds: {
    'http_req_duration{endpoint:opt_out}': ['p(99)<5000'],
    'http_req_duration{endpoint:parse_schedule}': ['p(95)<1000'],
    http_req_failed: ['rate<0.001']
  }
};

const MOCK_BASE_URL = __ENV.MOCK_BASE_URL || 'http://localhost:8080';
const TEST_RUN_ID = __ENV.TEST_RUN_ID || `k6-soak-${Date.now()}`;

const commonHeaders = {
  'Content-Type': 'application/json',
  'X-Test-Run-Id': TEST_RUN_ID
};

export function setup() {
  http.post(`${MOCK_BASE_URL}/mock/reset`, null, { headers: commonHeaders });
}

export default function () {
  // 1. Canonical v4.4 NLU parse request (Delta 6.6: raw_text)
  const parseRes = http.post(
    `${MOCK_BASE_URL}/v1/parse-schedule`,
    JSON.stringify({
      raw_text: `Remind Bob (+919123456789) tomorrow at 9:00 AM about sprint item ${__VU}-${__ITER}`,
      timezone: 'Asia/Kolkata'
    }),
    { headers: commonHeaders, tags: { endpoint: 'parse_schedule' } }
  );
  check(parseRes, { 'parse-schedule HTTP 200': (r) => r.status === 200 });

  // 2. Canonical Tier-2 STOP opt-out simulation (Delta 6.8: sender_e164 + keyword)
  const optOutRes = http.post(
    `${MOCK_BASE_URL}/mock/simulate/opt-out`,
    JSON.stringify({
      sender_e164: '+919123456789',
      keyword: 'STOP'
    }),
    { headers: commonHeaders, tags: { endpoint: 'opt_out' } }
  );
  check(optOutRes, {
    'opt-out HTTP 200': (r) => r.status === 200,
    'opt-out under 5000ms SLA': (r) => r.timings.duration <= 5000
  });

  sleep(0.5);
}

export function teardown() {
  http.post(`${MOCK_BASE_URL}/mock/reset`, null, { headers: commonHeaders });
}
