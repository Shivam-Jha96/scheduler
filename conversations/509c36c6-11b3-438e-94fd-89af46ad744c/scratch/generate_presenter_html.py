import os
import subprocess
import shutil

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WhatsApp Message Scheduler Chatbot — Master Architectural Plan</title>
  
  <!-- Inter & JetBrains Mono Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  
  <!-- Mermaid.js for Diagrams -->
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script>
    mermaid.initialize({
      startOnLoad: true,
      theme: 'base',
      themeVariables: {
        primaryColor: '#e0e7ff',
        primaryTextColor: '#1e1b4b',
        primaryBorderColor: '#6366f1',
        lineColor: '#4f46e5',
        secondaryColor: '#f1f5f9',
        tertiaryColor: '#ffffff',
        fontFamily: 'Inter, sans-serif',
        fontSize: '13px'
      }
    });
  </script>

  <style>
    :root {
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --wa-green: #25D366;
      --wa-dark: #075E54;
      --wa-teal: #128C7E;
      --wa-light: #DCF8C6;
      --wa-chat-bg: #EFEAE2;
      --bg-dark: #0f172a;
      --bg-card: #ffffff;
      --text-main: #1e293b;
      --text-muted: #64748b;
      --border: #e2e8f0;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      color: var(--text-main);
      background-color: #f8fafc;
      line-height: 1.6;
      font-size: 14px;
    }

    /* Top Sticky Navigation */
    .top-nav {
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(15, 23, 42, 0.95);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding: 12px 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: #fff;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      font-weight: 700;
      font-size: 16px;
      letter-spacing: -0.3px;
    }

    .brand-icon {
      width: 28px;
      height: 28px;
      background: var(--wa-green);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 16px;
    }

    .nav-links {
      display: flex;
      gap: 20px;
      font-size: 13px;
      font-weight: 500;
    }

    .nav-links a {
      color: #94a3b8;
      text-decoration: none;
      transition: color 0.2s;
    }

    .nav-links a:hover {
      color: #38bdf8;
    }

    .status-pill {
      background: rgba(37, 211, 102, 0.15);
      color: #4ade80;
      border: 1px solid rgba(74, 222, 128, 0.3);
      padding: 4px 12px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      background: #4ade80;
      border-radius: 50%;
      box-shadow: 0 0 8px #4ade80;
    }

    /* Hero Banner */
    .hero {
      background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f2b38 100%);
      color: #fff;
      padding: 60px 32px 50px 32px;
      text-align: center;
      position: relative;
      overflow: hidden;
    }

    .hero h1 {
      font-size: 38px;
      font-weight: 800;
      letter-spacing: -1px;
      line-height: 1.2;
      margin-bottom: 16px;
      background: linear-gradient(120deg, #ffffff 0%, #93c5fd 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .hero p {
      font-size: 17px;
      color: #94a3b8;
      max-width: 820px;
      margin: 0 auto 36px auto;
      font-weight: 400;
    }

    .metrics-bar {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      max-width: 1040px;
      margin: 0 auto;
    }

    .metric-card {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 18px 20px;
      text-align: left;
    }

    .metric-value {
      font-size: 26px;
      font-weight: 800;
      color: #38bdf8;
      font-family: 'JetBrains Mono', monospace;
    }

    .metric-label {
      font-size: 12px;
      color: #94a3b8;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-top: 4px;
    }

    /* Content Container */
    .container {
      max-width: 1200px;
      margin: 40px auto;
      padding: 0 24px;
    }

    .section {
      background: var(--bg-card);
      border-radius: 16px;
      border: 1px solid var(--border);
      box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
      padding: 36px;
      margin-bottom: 40px;
    }

    .section-title {
      font-size: 22px;
      font-weight: 800;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 20px;
      padding-bottom: 14px;
      border-bottom: 2px solid #f1f5f9;
    }

    .section-badge {
      font-size: 11px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      background: #e0f2fe;
      color: #0369a1;
    }

    /* Cards Grid */
    .grid-2 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
      gap: 24px;
      margin-top: 24px;
    }

    .arch-card {
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .arch-card.highlight {
      border-color: #93c5fd;
      background: #f0f7ff;
    }

    .arch-card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 16px;
    }

    .arch-card-title {
      font-size: 17px;
      font-weight: 700;
      color: #0f172a;
    }

    .arch-card-subtitle {
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .tag-compliant {
      background: #dcfce7;
      color: #15803d;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 4px;
    }

    .tag-autonomous {
      background: #fef3c7;
      color: #b45309;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 4px;
    }

    /* WhatsApp Simulator Frame */
    .wa-preview-wrapper {
      display: flex;
      justify-content: center;
      margin: 30px 0;
    }

    .phone-mockup {
      width: 440px;
      background: #111b21;
      border-radius: 36px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 10px #1e293b;
      overflow: hidden;
      border: 4px solid #334155;
    }

    .phone-header {
      background: var(--wa-dark);
      color: #fff;
      padding: 14px 18px;
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .phone-avatar {
      width: 36px;
      height: 36px;
      background: var(--wa-teal);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 15px;
    }

    .phone-title {
      font-size: 14px;
      font-weight: 600;
      line-height: 1.2;
    }

    .phone-subtitle {
      font-size: 11px;
      color: #a7f3d0;
    }

    .phone-chat-body {
      background: var(--wa-chat-bg);
      background-image: radial-gradient(#d1d5db 1px, transparent 1px);
      background-size: 16px 16px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      font-size: 12.5px;
      max-height: 560px;
      overflow-y: auto;
    }

    .chat-bubble {
      max-width: 82%;
      padding: 10px 14px;
      border-radius: 12px;
      position: relative;
      box-shadow: 0 1px 2px rgba(0,0,0,0.1);
      line-height: 1.45;
    }

    .chat-user {
      align-self: flex-end;
      background: var(--wa-light);
      border-bottom-right-radius: 2px;
    }

    .chat-bot {
      align-self: flex-start;
      background: #ffffff;
      border-bottom-left-radius: 2px;
    }

    .chat-time {
      font-size: 9.5px;
      color: #64748b;
      text-align: right;
      margin-top: 4px;
    }

    .chat-btn-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-top: 8px;
      border-top: 1px solid #e2e8f0;
      padding-top: 8px;
    }

    .chat-btn {
      background: #f1f5f9;
      color: #0284c7;
      font-weight: 600;
      font-size: 12px;
      padding: 8px 12px;
      border-radius: 6px;
      text-align: center;
      border: 1px solid #cbd5e1;
      cursor: default;
    }

    .chat-btn.active {
      background: #0284c7;
      color: #fff;
      border-color: #0284c7;
    }

    .vcard-chip {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 8px 12px;
      display: flex;
      align-items: center;
      gap: 10px;
      margin-top: 4px;
    }

    .vcard-icon {
      width: 32px;
      height: 32px;
      background: #3b82f6;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-weight: 700;
    }

    /* Tables */
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      font-size: 13px;
    }

    th {
      background: #f1f5f9;
      color: #0f172a;
      font-weight: 600;
      text-align: left;
      padding: 12px 14px;
      border: 1px solid var(--border);
    }

    td {
      padding: 10px 14px;
      border: 1px solid var(--border);
      color: #334155;
    }

    tr:nth-child(even) td {
      background: #f8fafc;
    }

    /* Diagram Wrappers */
    .diagram-container {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      margin: 20px 0;
      overflow-x: auto;
      text-align: center;
    }

    /* Code Blocks */
    pre {
      background: #0f172a;
      color: #f1f5f9;
      padding: 18px 20px;
      border-radius: 10px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12.5px;
      line-height: 1.5;
      overflow-x: auto;
      margin: 16px 0;
      border: 1px solid #1e293b;
    }

    code {
      font-family: 'JetBrains Mono', monospace;
      font-size: 12.5px;
      background: #f1f5f9;
      color: #0f172a;
      padding: 2px 6px;
      border-radius: 4px;
    }

    pre code {
      background: transparent;
      color: inherit;
      padding: 0;
    }

    /* Roadmap Timeline */
    .timeline {
      display: flex;
      flex-direction: column;
      gap: 20px;
      margin-top: 24px;
    }

    .timeline-item {
      display: flex;
      gap: 20px;
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      position: relative;
    }

    .timeline-badge {
      width: 90px;
      flex-shrink: 0;
      background: #e0e7ff;
      color: #4338ca;
      font-weight: 700;
      font-size: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 8px;
      height: 40px;
      text-align: center;
    }

    .timeline-content h4 {
      font-size: 15px;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 6px;
    }

    .timeline-content p {
      font-size: 13px;
      color: var(--text-muted);
      margin-bottom: 8px;
    }

    .timeline-tags {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .timeline-tag {
      background: #e2e8f0;
      color: #475569;
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 4px;
      font-weight: 500;
    }

    /* Print Styles */
    @media print {
      .top-nav {
        display: none;
      }
      .hero {
        background: #0f172a !important;
        color: #fff !important;
        -webkit-print-color-adjust: exact;
      }
      .section {
        box-shadow: none;
        border: 1px solid #cbd5e1;
        page-break-inside: avoid;
        margin-bottom: 24px;
        padding: 20px;
      }
      .phone-mockup {
        box-shadow: none;
        border: 2px solid #334155;
      }
    }
  </style>
</head>
<body>

  <!-- Top Navigation -->
  <nav class="top-nav">
    <div class="brand">
      <div class="brand-icon">✓</div>
      <span>WhatsApp Scheduler Bot — Master Specification</span>
    </div>
    <div class="nav-links">
      <a href="#overview">Overview</a>
      <a href="#feasibility">Feasibility & Models</a>
      <a href="#conversational-ux">Chatbot Wizard</a>
      <a href="#hybrid-scheduler">Hybrid Scheduler</a>
      <a href="#database-ddl">Database Schema</a>
      <a href="#roadmap">Roadmap</a>
    </div>
    <div class="status-pill">
      <div class="status-dot"></div>
      Approved Architecture
    </div>
  </nav>

  <!-- Hero Section -->
  <header class="hero" id="overview">
    <h1>In-WhatsApp Message Scheduler Chatbot</h1>
    <p>A comprehensive architectural blueprint for scheduling personal & group WhatsApp messages directly within the chat interface, featuring zero-double-send idempotency, wall-clock DST invariance, and anti-ban safeguards.</p>
    
    <div class="metrics-bar">
      <div class="metric-card">
        <div class="metric-value">100% P2P</div>
        <div class="metric-label">Sender Identity Parity</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">&lt; 1.0 ms</div>
        <div class="metric-label">DB Index Polling Latency</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">0 Double-Sends</div>
        <div class="metric-label">SHA-256 Distributed Mutex</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">DST-Proof</div>
        <div class="metric-label">Wall-Clock Anchor Recurrence</div>
      </div>
    </div>
  </header>

  <main class="container">

    <!-- Section 1: Executive Framing & Feasibility -->
    <section class="section" id="feasibility">
      <div class="section-title">
        <span>1. Platform Feasibility & The Sender Identity Dilemma</span>
        <span class="section-badge">Meta Policy & Feasibility</span>
      </div>
      
      <p>Building a message scheduler that operates <em>inside</em> WhatsApp faces fundamental platform constraints: Meta's official <strong>Cloud API (B2C)</strong> enforces a strict 24-hour customer service window and originates messages from corporate business numbers, while <strong>Personal Automation (P2P)</strong> enables true background peer-to-peer delivery but requires behavioral anti-ban pacing.</p>

      <div class="grid-2">
        <!-- Model A -->
        <div class="arch-card">
          <div>
            <div class="arch-card-header">
              <div>
                <div class="arch-card-title">Model A: Cloud API Assistive CTA</div>
                <div class="arch-card-subtitle">Official Meta Business Platform</div>
              </div>
              <span class="tag-compliant">100% Compliant</span>
            </div>
            <p>Alice converses with an official business bot. At the scheduled time, the bot sends an urgent alert to <strong>Alice</strong> with an interactive Call-to-Action button (<code>[ Send to Bob ]</code>). Tapping the button launches Alice's native WhatsApp chat with Bob with the text pre-populated.</p>
            <ul style="margin: 14px 0 14px 18px; color: #475569; font-size: 13px;">
              <li><strong>Ban Risk:</strong> Zero (Official Graph API v21.0)</li>
              <li><strong>Cost:</strong> Free incoming / utility template fees</li>
              <li><strong>Sender:</strong> Alice sends with one tap from her native app</li>
              <li><strong>Trade-off:</strong> Semi-autonomous (requires Alice's tap)</li>
            </ul>
          </div>
          <div style="background: #f1f5f9; padding: 10px; border-radius: 6px; font-size: 11.5px; font-family: monospace;">
            Flow: Alice schedules &rarr; Bot alerts Alice &rarr; One-click deep link opens chat to Bob
          </div>
        </div>

        <!-- Model B -->
        <div class="arch-card highlight">
          <div>
            <div class="arch-card-header">
              <div>
                <div class="arch-card-title">Model B: Baileys Companion Node</div>
                <div class="arch-card-subtitle">Multi-Device WebSocket Protocol</div>
              </div>
              <span class="tag-autonomous">100% Autonomous</span>
            </div>
            <p>Alice links her personal account by scanning a multi-device QR code. The scheduler runs as an official companion device using <code>@whiskeysockets/baileys</code>. At the scheduled time, the worker dispatches the message directly from Alice's number to Bob in the background.</p>
            <ul style="margin: 14px 0 14px 18px; color: #475569; font-size: 13px;">
              <li><strong>Ban Risk:</strong> Mitigated via multi-modal typing simulation & pacing</li>
              <li><strong>Cost:</strong> $0.00 Meta fees (self-hosted Node.js / Docker)</li>
              <li><strong>Sender:</strong> Directly from Alice's personal phone number</li>
              <li><strong>Benefit:</strong> 100% autonomous (Alice can be asleep or offline)</li>
            </ul>
          </div>
          <div style="background: #e0f2fe; padding: 10px; border-radius: 6px; font-size: 11.5px; font-family: monospace; color: #0369a1;">
            Flow: Alice links companion &rarr; Schedules job &rarr; Autonomous delivery directly to Bob
          </div>
        </div>
      </div>

      <!-- Comparative Table -->
      <h3 style="margin-top: 30px;">Multi-Dimensional Platform Trade-Off Matrix</h3>
      <table>
        <thead>
          <tr>
            <th>Evaluation Criteria</th>
            <th>WhatsApp Cloud API</th>
            <th>Baileys Multi-Device (Recommended)</th>
            <th>Puppeteer (whatsapp-web.js)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Runtime Engine</strong></td>
            <td>Official Meta Cloud REST API</td>
            <td>Pure Node.js WebSocket (Noise_XX)</td>
            <td>Headless Chromium Browser</td>
          </tr>
          <tr>
            <td><strong>Memory per Session</strong></td>
            <td>0 MB (Stateless)</td>
            <td>30 MB – 60 MB</td>
            <td>250 MB – 500 MB</td>
          </tr>
          <tr>
            <td><strong>Autonomous Delivery</strong></td>
            <td>Yes (from Business Number)</td>
            <td><strong>Yes (from Alice's Number)</strong></td>
            <td>Yes (from Alice's Number)</td>
          </tr>
          <tr>
            <td><strong>24-Hour Window Constraint</strong></td>
            <td>Strictly enforced (Error 131047)</td>
            <td><strong>Bypassed (Native P2P)</strong></td>
            <td>Bypassed (Native P2P)</td>
          </tr>
          <tr>
            <td><strong>Ban Mitigation Safeguards</strong></td>
            <td>Not needed</td>
            <td><strong>Typing delay, rate limits & jitter</strong></td>
            <td>Browser fingerprinting defense</td>
          </tr>
          <tr>
            <td><strong>Per-Message Cost</strong></td>
            <td>$0.0042 – $0.0380 / msg</td>
            <td><strong>$0.00 Meta Fees</strong></td>
            <td>$0.00 Meta Fees</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Section 2: Conversational UX & Mobile Simulator -->
    <section class="section" id="conversational-ux">
      <div class="section-title">
        <span>2. Conversational UX: The 5-Step Guided Wizard</span>
        <span class="section-badge">WhatsApp Mobile UI</span>
      </div>

      <p>The chatbot features a dual-mode conversational engine: an interactive <strong>5-Step Mobile Wizard</strong> for casual users (utilizing WhatsApp buttons, lists, and vCard attachments) and a <strong>Fast-Path CLI</strong> (<code>/schedule &lt;contact&gt; &lt;time&gt; | &lt;msg&gt;</code>) for power users.</p>

      <!-- Live Mockup of WhatsApp Chat -->
      <div class="wa-preview-wrapper">
        <div class="phone-mockup">
          <div class="phone-header">
            <div class="phone-avatar">🤖</div>
            <div>
              <div class="phone-title">Scheduler Assistant</div>
              <div class="phone-subtitle">Online • Business Account</div>
            </div>
          </div>
          <div class="phone-chat-body">
            <!-- Message 1 -->
            <div class="chat-bubble chat-user">
              Schedule a message
              <div class="chat-time">10:14 AM ✓✓</div>
            </div>

            <!-- Message 2 -->
            <div class="chat-bubble chat-bot">
              👋 Let's set up your scheduled message!
              <br><br>
              <strong>Step 1 of 5: Who is the recipient?</strong>
              <br>You can attach a contact card (vCard), type a phone number with country code, or choose a saved alias.
              <div class="chat-btn-group">
                <div class="chat-btn">📁 Share Contact vCard</div>
                <div class="chat-btn">⚡ Select Saved Alias</div>
              </div>
              <div class="chat-time">10:14 AM</div>
            </div>

            <!-- Message 3 -->
            <div class="chat-bubble chat-user">
              <div class="vcard-chip">
                <div class="vcard-icon">👤</div>
                <div>
                  <strong>Bob Smith</strong><br>
                  <span style="font-size: 11px; color: #64748b;">+1 (415) 555-0199</span>
                </div>
              </div>
              <div class="chat-time">10:15 AM ✓✓</div>
            </div>

            <!-- Message 4 -->
            <div class="chat-bubble chat-bot">
              Recipient confirmed: <strong>Bob Smith</strong> (+14155550199).
              <br><br>
              <strong>Step 2 of 5: What message should I send?</strong>
              <br>Type your message text, or send a photo, voice note, or document.
              <div class="chat-time">10:15 AM</div>
            </div>

            <!-- Message 5 -->
            <div class="chat-bubble chat-user">
              Hey Bob! The Q4 roadmap report is finalized. Let's review it during tomorrow morning's sync!
              <div class="chat-time">10:16 AM ✓✓</div>
            </div>

            <!-- Message 6 -->
            <div class="chat-bubble chat-bot">
              Message captured.
              <br><br>
              <strong>Step 3 of 5: When should this be sent?</strong>
              <br><em>(Your timezone: America/New_York)</em>
              <br>Examples: <em>"tomorrow at 9:30 AM"</em>, <em>"in 2 hours"</em>, <em>"Friday at 5pm"</em>
              <div class="chat-time">10:16 AM</div>
            </div>

            <!-- Message 7 -->
            <div class="chat-bubble chat-user">
              tomorrow at 9:30 AM
              <div class="chat-time">10:16 AM ✓✓</div>
            </div>

            <!-- Message 8 -->
            <div class="chat-bubble chat-bot">
              Parsed: <strong>Tomorrow, 9:30 AM EST</strong>.
              <br><br>
              <strong>Step 4 of 5: Recurrence?</strong>
              <div class="chat-btn-group">
                <div class="chat-btn active">One-off (Send once)</div>
                <div class="chat-btn">Daily</div>
                <div class="chat-btn">Weekdays (Mon-Fri)</div>
              </div>
              <div class="chat-time">10:16 AM</div>
            </div>

            <!-- Message 9 -->
            <div class="chat-bubble chat-bot">
              📋 <strong>Schedule Confirmation:</strong>
              <br>• <strong>To:</strong> Bob Smith (+14155550199)
              <br>• <strong>When:</strong> Nov 9, 2026 at 9:30 AM EST
              <br>• <strong>Repeat:</strong> Once
              <br>• <strong>Text:</strong> "Hey Bob! The Q4 roadmap report..."
              <div class="chat-btn-group">
                <div class="chat-btn active" style="background: #22c55e; border-color: #22c55e;">✅ Confirm Schedule</div>
                <div class="chat-btn">✏️ Edit Details</div>
                <div class="chat-btn" style="color: #ef4444;">❌ Cancel</div>
              </div>
              <div class="chat-time">10:17 AM</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 3: End-to-End System Architecture -->
    <section class="section" id="hybrid-scheduler">
      <div class="section-title">
        <span>3. Two-Tier Hybrid Scheduling Engine & System Topology</span>
        <span class="section-badge">Distributed Systems</span>
      </div>

      <p>To eliminate memory saturation from millions of pending jobs while maintaining sub-second delivery accuracy, the architecture uses a <strong>Two-Tier Hybrid Scheduler</strong>: PostgreSQL 14+ acts as the persistent ledger, while a 60-second Look-Ahead Feeder loads due jobs into BullMQ/Redis for exact millisecond dispatch.</p>

      <div class="diagram-container">
        <pre class="mermaid">
flowchart LR
    subgraph ClientLayer ["WhatsApp Client Layer"]
        Alice([Alice User])
        Bob([Bob Recipient])
    end

    subgraph Ingress ["Ingress & FSM"]
        Socket[Baileys Socket / Webhook]
        FSM[Conversational FSM Engine]
        RedisDraft[(Redis Draft Session)]
    end

    subgraph Ledger ["Tier 1: Persistence"]
        PG[(PostgreSQL 14+ Master)]
    end

    subgraph Scheduler ["Tier 2: Scheduling & Execution"]
        Feeder[60s Look-Ahead Feeder]
        BullMQ[BullMQ Delayed Queue]
        WorkerPool[Distributed Workers]
        Sweeper[Dead-Man Recovery Sweeper]
    end

    Alice -->|Incoming Msg / vCard| Socket
    Socket --> FSM
    FSM <--> RedisDraft
    FSM -->|ACID Insert Job| PG

    Feeder -->|SKIP LOCKED 5-min Window| PG
    Feeder -->|Stage Delayed Job| BullMQ
    BullMQ -->|Exact Millisecond Trigger| WorkerPool
    
    WorkerPool -->|SHA-256 Idempotency Lock| RedisDraft
    WorkerPool -->|Human Paced Socket Send| Socket
    Socket -->|Direct Peer Message| Bob
    
    WorkerPool -->|Update Status & Recurrence| PG
    Sweeper -.->|Re-queue Stalled PROCESSING| PG
        </pre>
      </div>

      <div class="grid-2">
        <div class="arch-card">
          <div class="arch-card-title">Why Single-Tier Schedulers Fail:</div>
          <ul style="margin: 12px 0 0 18px; color: #475569; font-size: 13px;">
            <li><strong>Pure Redis:</strong> 1,000,000 future jobs consume ~1.8 GB of unpageable RAM. Server crashes without RDB/AOF risk catastrophic data loss.</li>
            <li><strong>Pure PostgreSQL Polling:</strong> 50 workers querying <code>SKIP LOCKED</code> every 1s generate 4.3 million queries/day, choking CPU and connections.</li>
          </ul>
        </div>
        <div class="arch-card highlight">
          <div class="arch-card-title">The Two-Tier Solution:</div>
          <ul style="margin: 12px 0 0 18px; color: #0369a1; font-size: 13px;">
            <li><strong>Durable Master:</strong> PostgreSQL stores 100% of jobs durably (0 MB RAM). Partial index scans take <strong>&lt; 1.0 ms</strong>.</li>
            <li><strong>Sliding Queue:</strong> BullMQ only holds jobs firing in the next 5 minutes (&lt; 250 KB RAM). Workers fire with millisecond precision.</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Section 4: Production PostgreSQL DDL Schema -->
    <section class="section" id="database-ddl">
      <div class="section-title">
        <span>4. Relational Data Architecture (PostgreSQL 14+)</span>
        <span class="section-badge">Production DDL</span>
      </div>

      <p>The persistent data model enforces relational integrity, partial indexing for instant poller queries, and cryptographic storage for WhatsApp Signal pre-keys.</p>

      <pre><code>-- Primary Master Scheduled Jobs Table
CREATE TABLE scheduled_jobs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_uid VARCHAR(32) NOT NULL UNIQUE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipient_jid VARCHAR(64) NOT NULL,
    recipient_type recipient_type_enum NOT NULL DEFAULT 'INDIVIDUAL',
    message_type message_type_enum NOT NULL DEFAULT 'TEXT',
    payload JSONB NOT NULL,
    user_timezone VARCHAR(64) NOT NULL,
    recurrence_type recurrence_type_enum NOT NULL DEFAULT 'ONCE',
    anchor_day_of_month INT,                     -- Month-end invariant (e.g. 31)
    scheduled_at_utc TIMESTAMPTZ NOT NULL,
    next_run_at_utc TIMESTAMPTZ,
    misfire_policy misfire_policy_enum NOT NULL DEFAULT 'FIRE_IMMEDIATELY',
    status job_status_enum NOT NULL DEFAULT 'PENDING',
    idempotency_key VARCHAR(128) NOT NULL UNIQUE, -- SHA-256 Zero-Double-Send Key
    locked_at TIMESTAMPTZ,
    locked_by VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- High-Performance Poller Index: Scans ONLY active pending jobs!
CREATE INDEX idx_scheduled_jobs_polling 
ON scheduled_jobs (next_run_at_utc ASC) 
WHERE status = 'PENDING';

-- Multi-Device Baileys Signal Pre-Keys & E2EE State
CREATE TABLE whatsapp_signal_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES whatsapp_sessions(id) ON DELETE CASCADE,
    key_type VARCHAR(32) NOT NULL,
    key_id VARCHAR(128) NOT NULL,
    key_data BYTEA NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_session_key UNIQUE (session_id, key_type, key_id)
);</code></pre>
    </section>

    <!-- Section 5: Recurrence & Safeguard Mathematics -->
    <section class="section">
      <div class="section-title">
        <span>5. Recurrence Math & Anti-Ban Safeguards</span>
        <span class="section-badge">Algorithms & Math</span>
      </div>

      <div class="grid-2">
        <div class="arch-card">
          <div class="arch-card-title">Wall-Clock DST Invariance & Anchor Days</div>
          <p style="margin-top: 8px;">To prevent daily reminders from shifting by &plusmn;1 hour when clocks change for Daylight Saving Time, recurrence is calculated in the calendar dimension:</p>
          <pre style="margin-top: 10px;"><code>// Wall-clock calculation in user timezone
1. t_local = toLocal(t_last_utc, user_tz)
2. t_next_local = t_local + 1 day (calendar dimension)
3. t_next_utc = toUTC(t_next_local)

// Month-End Anchor Day Logic
if (anchor_day == 31) {
  // Jan 31 -> Feb 28 -> Mar 31 -> Apr 30
  next_date = clampToMonthEnd(month, anchor_day);
}</code></pre>
        </div>

        <div class="arch-card">
          <div class="arch-card-title">Multi-Modal Human Typing Simulation</div>
          <p style="margin-top: 8px;">Automated clients that dispatch instantaneous socket messages trigger Meta heuristic bans. The delivery worker emulates human composition:</p>
          <pre style="margin-top: 10px;"><code>// Human typing delay calculation
T_type = min(5.0, len * 0.05 + Normal(1.5, 0.4)) sec

1. Send presence: 'available'
2. Send presence: 'composing'
3. Sleep(T_type)
4. Send presence: 'paused'
5. Send message with deterministic client MsgId
6. Space subsequent messages by 3-6s jitter</code></pre>
        </div>
      </div>
    </section>

    <!-- Section 6: Phased Implementation Roadmap -->
    <section class="section" id="roadmap">
      <div class="section-title">
        <span>6. Phased Implementation Roadmap</span>
        <span class="section-badge">10-Week Delivery</span>
      </div>

      <div class="timeline">
        <div class="timeline-item">
          <div class="timeline-badge">Weeks 1–2</div>
          <div class="timeline-content">
            <h4>Phase 1: Core Database DDL & WhatsApp Socket Sync</h4>
            <p>Deploy PostgreSQL 14+ schemas, range partitioning, and establish the Baileys multi-device pairing & Noise_XX handshake state machine.</p>
            <div class="timeline-tags">
              <span class="timeline-tag">PostgreSQL DDL</span>
              <span class="timeline-tag">Baileys WebSocket</span>
              <span class="timeline-tag">Signal Pre-Keys</span>
            </div>
          </div>
        </div>

        <div class="timeline-item">
          <div class="timeline-badge">Weeks 3–4</div>
          <div class="timeline-content">
            <h4>Phase 2: Conversational FSM & Natural Language Parser</h4>
            <p>Implement the 5-step guided wizard state machine in Redis, integrate <code>chrono-node</code> for date parsing, and support vCard extraction.</p>
            <div class="timeline-tags">
              <span class="timeline-tag">Redis Session Store</span>
              <span class="timeline-tag">chrono-node NLP</span>
              <span class="timeline-tag">libphonenumber-js</span>
            </div>
          </div>
        </div>

        <div class="timeline-item">
          <div class="timeline-badge">Weeks 5–6</div>
          <div class="timeline-content">
            <h4>Phase 3: Two-Tier Hybrid Scheduling Engine</h4>
            <p>Construct the 60-second Look-Ahead Feeder daemon with <code>SKIP LOCKED</code> queries and wire into BullMQ delayed execution queues.</p>
            <div class="timeline-tags">
              <span class="timeline-tag">Look-Ahead Feeder</span>
              <span class="timeline-tag">BullMQ</span>
              <span class="timeline-tag">Luxon DST Math</span>
            </div>
          </div>
        </div>

        <div class="timeline-item">
          <div class="timeline-badge">Weeks 7–8</div>
          <div class="timeline-content">
            <h4>Phase 4: Reliability, Anti-Ban & Failure Recovery</h4>
            <p>Incorporate the dead-man's-switch recovery sweeper, deterministic SHA-256 idempotency locks, and human typing indicators.</p>
            <div class="timeline-tags">
              <span class="timeline-tag">SHA-256 Mutex</span>
              <span class="timeline-tag">Recovery Sweeper</span>
              <span class="timeline-tag">Typing Pacing</span>
            </div>
          </div>
        </div>

        <div class="timeline-item">
          <div class="timeline-badge">Weeks 9–10</div>
          <div class="timeline-content">
            <h4>Phase 5: E2E Chaos Testing & Production Rollout</h4>
            <p>Execute burst load testing (10,000 msgs/hr), socket kill simulations, Prometheus/Grafana dashboards, and Docker/Helm deployment packaging.</p>
            <div class="timeline-tags">
              <span class="timeline-tag">Chaos Injection</span>
              <span class="timeline-tag">Prometheus Metrics</span>
              <span class="timeline-tag">Docker Compose</span>
            </div>
          </div>
        </div>
      </div>
    </section>

  </main>

</body>
</html>
"""

# Write HTML file to workspace
target_html = r"C:\Users\Lenovo\teamwork_projects\whatsapp_scheduler_bot\WhatsApp_Scheduler_Master_Technical_Plan.html"
artifact_html = r"C:\Users\Lenovo\.gemini\antigravity\brain\509c36c6-11b3-438e-94fd-89af46ad744c\WhatsApp_Scheduler_Master_Technical_Plan.html"

with open(target_html, "w", encoding="utf-8") as f:
    f.write(html_content)

shutil.copy2(target_html, artifact_html)
print(f"Updated HTML written to: {target_html} and copied to {artifact_html}")

# Re-run Headless Chrome to generate corresponding presentation PDF
pdf_path = r"C:\Users\Lenovo\teamwork_projects\whatsapp_scheduler_bot\WhatsApp_Scheduler_Master_Technical_Plan.pdf"
artifact_pdf = r"C:\Users\Lenovo\.gemini\antigravity\brain\509c36c6-11b3-438e-94fd-89af46ad744c\WhatsApp_Scheduler_Master_Technical_Plan.pdf"

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    "--virtual-time-budget=5000",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={pdf_path}",
    target_html
]

print("Compiling updated PDF with Chrome Headless...")
res = subprocess.run(cmd, capture_output=True, text=True)
print(f"Chrome return code: {res.returncode}")

if os.path.exists(pdf_path):
    shutil.copy2(pdf_path, artifact_pdf)
    size_kb = os.path.getsize(pdf_path) / 1024
    print(f"Successfully generated updated PDF: {size_kb:.1f} KB")
