import http from 'k6/http';
import crypto from 'k6/crypto';
import { check } from 'k6';

/**
 * TC-LOAD-01: 3x Meta Webhook Receipt Storm + Fast-ACK Benchmark
 * Target SLOs (Model C v4.4 HYBRID):
 *   - Webhook Ingestion Fast-ACK p99 <= 50 ms (internal target p95 < 20 ms)
 *   - 0% HTTP 5xx / zero PostgreSQL pool exhaustion
 */
export const options = {
  scenarios: {
    receipt_storm: {
      executor: 'constant-arrival-rate',
      rate: 150, // 1,500 receipts per 10s window
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 50,
      maxVUs: 200
    }
  },
  thresholds: {
    http_req_duration: ['p(95)<20', 'p(99)<50'],
    http_req_failed: ['rate<0.001']
  }
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';
const APP_SECRET = __ENV.META_APP_SECRET || 'dev-meta-app-secret';
const TEST_RUN_ID = __ENV.TEST_RUN_ID || `k6-storm-${Date.now()}`;
const STATUSES = ['sent', 'delivered', 'read'];

export default function () {
  const status = STATUSES[__ITER % STATUSES.length];
  const nowSec = Math.floor(Date.now() / 1000);
  const payload = JSON.stringify({
    object: 'whatsapp_business_account',
    entry: [
      {
        id: 'WABA_LOAD_TEST',
        changes: [
          {
            field: 'messages',
            value: {
              messaging_product: 'whatsapp',
              metadata: {
                display_phone_number: '15551234567',
                phone_number_id: '15551234567'
              },
              statuses: [
                {
                  id: `wamid.LOAD.${__VU}.${__ITER}`,
                  status,
                  timestamp: String(nowSec),
                  recipient_id: '919123456789'
                }
              ]
            }
          }
        ]
      }
    ]
  });

  const sig = `sha256=${crypto.hmac('sha256', APP_SECRET, payload, 'hex')}`;
  const res = http.post(`${BASE_URL}/webhooks/whatsapp`, payload, {
    headers: {
      'Content-Type': 'application/json',
      'X-Hub-Signature-256': sig,
      'X-Test-Run-Id': TEST_RUN_ID
    }
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
    'ACK under 50ms': (r) => r.timings.duration <= 50
  });
}
