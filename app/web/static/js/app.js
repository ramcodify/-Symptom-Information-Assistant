// MediSafe AI — Complete Modern Frontend Application Logic

document.addEventListener('DOMContentLoaded', () => {
  // Robust Dynamic Backend API Base Detection
  const API_BASE = (window.location.protocol === 'file:' || (window.location.port && window.location.port !== '8000'))
    ? 'http://127.0.0.1:8000'
    : '';

  console.log('MediSafe AI initialized. Connected to backend API at:', API_BASE || window.location.origin);

  // --- Theme Management ---
  const themeToggle = document.getElementById('themeToggle');
  const htmlEl = document.documentElement;

  themeToggle.addEventListener('click', () => {
    const current = htmlEl.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    htmlEl.setAttribute('data-theme', next);
    themeToggle.innerHTML = next === 'dark' ? '<i class="fa-solid fa-moon"></i>' : '<i class="fa-solid fa-sun"></i>';
  });

  // --- Tab Navigation ---
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  function switchTab(tabId) {
    tabButtons.forEach(b => b.classList.toggle('active', b.getAttribute('data-tab') === tabId));
    tabPanes.forEach(p => p.classList.toggle('active', p.id === tabId));
  }

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.getAttribute('data-tab')));
  });

  // --- Voice Input & Speech Synthesis ---
  let voiceEnabled = true;
  const voiceToggleBtn = document.getElementById('voiceToggleBtn');
  const voiceStatusText = document.getElementById('voiceStatusText');
  const micBtn = document.getElementById('micBtn');

  voiceToggleBtn.addEventListener('click', () => {
    voiceEnabled = !voiceEnabled;
    voiceStatusText.innerText = voiceEnabled ? 'Voice On' : 'Voice Off';
    voiceToggleBtn.style.opacity = voiceEnabled ? '1' : '0.6';
  });

  function speakText(text) {
    if (!voiceEnabled || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    
    // Clean markdown symbols for natural speech
    const cleanSpeech = text
      .replace(/(\*\*|__|\*|_|`|#|>|\[.*?\]\(.*?\))/g, '')
      .replace(/⚠️|🚨|💊|🩺|💡|🔍|🔴|🟡|🟢/g, '')
      .substring(0, 300);

    const utterance = new SpeechSynthesisUtterance(cleanSpeech);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  }

  // Web Speech Recognition
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognizer = new SpeechRecognition();
    recognizer.continuous = false;
    recognizer.interimResults = false;
    recognizer.lang = 'en-US';

    let isRecording = false;

    micBtn.addEventListener('click', () => {
      if (!isRecording) {
        recognizer.start();
        micBtn.classList.add('active-recording');
        isRecording = true;
      } else {
        recognizer.stop();
        micBtn.classList.remove('active-recording');
        isRecording = false;
      }
    });

    recognizer.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      document.getElementById('chatInput').value = transcript;
      micBtn.classList.remove('active-recording');
      isRecording = false;
      handleSendMessage(transcript);
    };

    recognizer.onerror = () => {
      micBtn.classList.remove('active-recording');
      isRecording = false;
    };
  } else {
    micBtn.style.display = 'none';
  }

  // --- Emergency Modal & Banners ---
  const emergencyModal = document.getElementById('emergencyModal');
  const emergencyBanner = document.getElementById('emergencyBanner');
  const closeEmergencyModal = document.getElementById('closeEmergencyModal');
  const acknowledgeEmergencyBtn = document.getElementById('acknowledgeEmergencyBtn');
  const dismissBanner = document.getElementById('dismissBanner');
  const quickSosHeaderBtn = document.getElementById('quickSosHeaderBtn');

  function triggerEmergencyUI(condition, firstAid) {
    document.getElementById('modalEmergencySubtitle').innerText = `Identified Warning: ${condition}`;
    document.getElementById('modalFirstAidText').innerText = firstAid || 'Call 911 / 112 immediately and rest.';
    emergencyModal.classList.remove('hidden');

    document.getElementById('emergencyTitle').innerText = `🚨 CRITICAL EMERGENCY DETECTED: ${condition.toUpperCase()}`;
    emergencyBanner.classList.remove('hidden');
  }

  closeEmergencyModal.addEventListener('click', () => emergencyModal.classList.add('hidden'));
  acknowledgeEmergencyBtn.addEventListener('click', () => emergencyModal.classList.add('hidden'));
  dismissBanner.addEventListener('click', () => emergencyBanner.classList.add('hidden'));

  quickSosHeaderBtn.addEventListener('click', () => {
    triggerEmergencyUI('Acute Emergency Protocol', 'Call 911 (US/Canada), 112 (Europe/Intl), or 999 (UK) immediately.');
  });

  // --- TAB 1: Chat Assistant ---
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const chatMessages = document.getElementById('chatMessages');
  const promptChips = document.querySelectorAll('.prompt-chip');

  let chatHistory = [];

  function appendMessage(role, text, isEmergency = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}-message ${isEmergency ? 'emergency-msg' : ''}`;

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.innerHTML = role === 'user' ? '<i class="fa-solid fa-user"></i>' : (isEmergency ? '<i class="fa-solid fa-triangle-exclamation"></i>' : '<i class="fa-solid fa-shield-heart"></i>');

    const body = document.createElement('div');
    body.className = 'msg-body';

    const content = document.createElement('div');
    content.className = 'msg-content';
    content.innerHTML = marked.parse(text);

    body.appendChild(content);
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(body);

    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    if (role === 'assistant') {
      speakText(text);
    }
  }

  async function handleSendMessage(queryText) {
    const q = queryText || chatInput.value.trim();
    if (!q) return;

    appendMessage('user', q);
    chatInput.value = '';

    // Loading indicator
    const loaderId = 'loader-' + Date.now();
    const loaderDiv = document.createElement('div');
    loaderDiv.id = loaderId;
    loaderDiv.className = 'message assistant-message';
    loaderDiv.innerHTML = `
      <div class="msg-avatar"><i class="fa-solid fa-shield-heart"></i></div>
      <div class="msg-body"><p><i class="fa-solid fa-spinner fa-spin"></i> Analyzing query through Guardrails & Agents...</p></div>
    `;
    chatMessages.appendChild(loaderDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
      const resp = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, history: chatHistory })
      });

      const data = await resp.json();
      const loader = document.getElementById(loaderId);
      if (loader) loader.remove();

      if (resp.ok) {
        const isEmergency = data.escalation_triggered;
        appendMessage('assistant', data.response_text, isEmergency);

        if (isEmergency) {
          const condition = data.guardrail_result?.emergency_condition || 'Critical Warning Sign';
          const firstAid = data.guardrail_result?.emergency_first_aid;
          triggerEmergencyUI(condition, firstAid);
        }

        chatHistory.push({ role: 'user', content: q });
        chatHistory.push({ role: 'assistant', content: data.response_text });
      } else {
        appendMessage('assistant', '⚠️ An error occurred processing your request. Please try again.');
      }
    } catch (err) {
      const loader = document.getElementById(loaderId);
      if (loader) loader.remove();
      appendMessage('assistant', '⚠️ Connection error. Please ensure the backend server is running on port 8000.');
    }
  }

  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    handleSendMessage();
  });

  promptChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const q = chip.getAttribute('data-query');
      handleSendMessage(q);
    });
  });

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });


  // --- TAB 2: Drug Interaction Matrix ---
  const drugTagContainer = document.getElementById('drugTagContainer');
  const addDrugInput = document.getElementById('addDrugInput');
  const addDrugBtn = document.getElementById('addDrugBtn');
  const runInteractionBtn = document.getElementById('runInteractionBtn');
  const interactionResultsContent = document.getElementById('interactionResultsContent');
  const quickComboBtns = document.querySelectorAll('.quick-combo-btn');

  let currentDrugs = ['Ibuprofen', 'Lisinopril'];

  function renderTags() {
    drugTagContainer.innerHTML = '';
    currentDrugs.forEach((d, idx) => {
      const tag = document.createElement('span');
      tag.className = 'drug-tag';
      tag.innerHTML = `${d} <i class="fa-solid fa-xmark remove-tag" data-idx="${idx}"></i>`;
      drugTagContainer.appendChild(tag);
    });

    document.querySelectorAll('.remove-tag').forEach(icon => {
      icon.addEventListener('click', (e) => {
        const idx = parseInt(e.target.getAttribute('data-idx'));
        currentDrugs.splice(idx, 1);
        renderTags();
      });
    });
  }

  function addDrug(name) {
    const clean = name.trim();
    if (clean && !currentDrugs.includes(clean)) {
      currentDrugs.push(clean);
      renderTags();
    }
    addDrugInput.value = '';
  }

  addDrugBtn.addEventListener('click', () => addDrug(addDrugInput.value));
  addDrugInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addDrug(addDrugInput.value);
    }
  });

  quickComboBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      currentDrugs = btn.getAttribute('data-combo').split(',').map(s => s.trim());
      renderTags();
      runInteractionCheck();
    });
  });

  async function runInteractionCheck() {
    if (currentDrugs.length < 2) {
      interactionResultsContent.innerHTML = '<p style="color: var(--accent-red);">Please add at least 2 medications to check.</p>';
      return;
    }

    interactionResultsContent.innerHTML = '<p><i class="fa-solid fa-spinner fa-spin"></i> Checking multi-drug pharmacology database...</p>';

    try {
      const resp = await fetch(`${API_BASE}/api/check-interactions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ drugs: currentDrugs })
      });
      const data = await resp.json();

      if (data.interactions_found) {
        let html = `
          <div style="margin-bottom: 16px;">
            <strong>Highest Risk Level: </strong>
            <span style="color:${data.highest_severity.includes('High') || data.highest_severity.includes('Severe') ? 'var(--accent-red)' : 'var(--accent-amber)'}; font-weight:700;">
              ${data.highest_severity}
            </span>
          </div>
        `;

        data.results.forEach(res => {
          const sevColor = res.severity.includes('High') || res.severity.includes('Severe') ? 'var(--accent-red)' : 'var(--accent-amber)';
          html += `
            <div style="background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 12px; padding: 18px; margin-bottom: 14px;">
              <h4 style="margin-bottom: 8px;">💊 ${res.drug_pair.join(' ↔️ ')}</h4>
              <p><strong>Severity:</strong> <span style="color: ${sevColor}; font-weight:700;">${res.severity}</span></p>
              <p style="margin-top: 6px;"><strong>Clinical Effect:</strong> ${res.clinical_effect}</p>
              <p style="margin-top: 6px;"><strong>Biological Mechanism:</strong> ${res.mechanism}</p>
              <p style="margin-top: 6px; color: var(--accent-emerald);"><strong>Safety Guidance:</strong> ${res.clinical_management}</p>
              ${res.alternative_recommendation ? `<p style="margin-top: 6px; color: var(--accent-blue);"><strong>💡 Safer Choice:</strong> ${res.alternative_recommendation}</p>` : ''}
            </div>
          `;
        });
        interactionResultsContent.innerHTML = html;
      } else {
        interactionResultsContent.innerHTML = `
          <div style="text-align: center; padding: 32px;">
            <i class="fa-solid fa-circle-check" style="font-size: 2.8rem; color: var(--accent-emerald); margin-bottom: 12px;"></i>
            <h4>No Severe Known Interactions Flagged</h4>
            <p style="color: var(--text-secondary); margin-top: 8px;">No major contraindications identified between these drugs in our clinical reference dataset. Always verify with your pharmacist.</p>
          </div>
        `;
      }
    } catch (err) {
      interactionResultsContent.innerHTML = '<p style="color: var(--accent-red);">Failed to retrieve interaction data.</p>';
    }
  }

  runInteractionBtn.addEventListener('click', runInteractionCheck);
  renderTags();


  // --- TAB 3: Generic Finder & Savings Calculator ---
  const genericSearchInput = document.getElementById('genericSearchInput');
  const genericSearchBtn = document.getElementById('genericSearchBtn');
  const genericResultContainer = document.getElementById('genericResultContainer');
  const quickBrandBtns = document.querySelectorAll('.quick-brand-btn');
  const monthlySpendSlider = document.getElementById('monthlySpendSlider');
  const spendValueDisplay = document.getElementById('spendValueDisplay');
  const annualSavingsCalculated = document.getElementById('annualSavingsCalculated');

  // Calculator logic
  monthlySpendSlider.addEventListener('input', (e) => {
    const val = parseInt(e.target.value);
    spendValueDisplay.innerText = `$${val} / month`;
    const annualSpend = val * 12;
    const savings = Math.round(annualSpend * 0.80);
    annualSavingsCalculated.innerText = `$${savings.toLocaleString()} / year`;
  });

  async function searchGeneric(name) {
    const q = name || genericSearchInput.value.trim();
    if (!q) return;

    genericResultContainer.innerHTML = '<p><i class="fa-solid fa-spinner fa-spin"></i> Querying FDA Orange Book & bioequivalence datasets...</p>';

    try {
      const resp = await fetch(`${API_BASE}/api/generic-finder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ medicine_name: q })
      });
      const data = await resp.json();

      if (data.found) {
        genericResultContainer.innerHTML = `
          <div class="generic-card">
            <div>
              <span style="display:inline-block; background:rgba(16,185,129,0.15); color:var(--accent-emerald); padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:700; margin-bottom:12px;">
                <i class="fa-solid fa-certificate"></i> ${data.therapeutic_equivalence}
              </span>
              <h3>${data.brand_name} → <span style="color:var(--accent-blue);">${data.generic_name}</span></h3>
              <p style="margin-top:8px;"><strong>Active Ingredient:</strong> <code>${data.active_ingredient}</code></p>
              <p style="margin-top:6px;"><strong>Dosage Forms:</strong> ${data.common_forms ? data.common_forms.join(', ') : 'Tablets / Capsules'}</p>
              <p style="margin-top:6px;"><strong>Status:</strong> ${data.otc_availability}</p>
              <div style="margin-top:14px; background:var(--bg-primary); padding:14px; border-radius:8px; border-left:3px solid var(--accent-blue);">
                <strong>💡 Pharmacist Advice:</strong> ${data.switching_guidance}
              </div>
            </div>
            <div class="savings-circle">
              <div class="savings-val">${data.average_cost_savings}</div>
              <div class="savings-label">Average Cost Savings</div>
              <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">vs. Innovator Brand</div>
            </div>
          </div>
        `;
      } else {
        genericResultContainer.innerHTML = `
          <div class="glass-card" style="text-align:center; padding:32px;">
            <i class="fa-solid fa-circle-question" style="font-size:2.5rem; color:var(--accent-amber); margin-bottom:12px;"></i>
            <h4>Generic Equivalent Not Found</h4>
            <p style="color:var(--text-secondary); margin-top:8px;">${data.message}</p>
          </div>
        `;
      }
    } catch (err) {
      genericResultContainer.innerHTML = '<p style="color:var(--accent-red);">Failed to retrieve generic data.</p>';
    }
  }

  genericSearchBtn.addEventListener('click', () => searchGeneric());
  genericSearchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      searchGeneric();
    }
  });

  quickBrandBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const brand = btn.getAttribute('data-brand');
      genericSearchInput.value = brand;
      searchGeneric(brand);
    });
  });

  searchGeneric('Lipitor');


  // --- TAB 4: Symptom & Red-Flag Triage Map ---
  const regionButtons = document.querySelectorAll('.region-btn');
  const regionTitle = document.getElementById('regionTitle');
  const regionContent = document.getElementById('regionContent');

  const regionData = {
    chest: {
      title: "Chest & Cardiovascular Symptoms",
      redFlag: "Crushing chest pain, pressure, radiating to left arm or jaw, sweating, dyspnea.",
      condition: "Acute Coronary Syndrome / Heart Attack",
      action: "Call 911/112 immediately. Chew 325mg aspirin if conscious & not allergic. Rest sitting upright.",
      common: "Acid reflux, musculoskeletal strain, mild palpitations from caffeine."
    },
    head: {
      title: "Head & Neurological Symptoms",
      redFlag: "Facial droop, arm weakness, slurred speech (FAST signs), thunderclap headache.",
      condition: "Acute Stroke / Intracranial Hemorrhage",
      action: "Call 911/112 immediately. Note exact symptom onset time. Do NOT give food or aspirin.",
      common: "Tension headache, mild migraine, sinus pressure, eye strain."
    },
    respiratory: {
      title: "Airway & Respiratory Symptoms",
      redFlag: "Cannot speak full sentences, blue lips/fingers, severe wheezing at rest.",
      condition: "Severe Respiratory Failure / Asthma Exacerbation",
      action: "Call 911/112 immediately. Administer albuterol rescue inhaler if prescribed. Tripod position.",
      common: "Common cold, mild viral cough, allergic rhinitis, post-nasal drip."
    },
    abdomen: {
      title: "Abdomen & Toxic Ingestions",
      redFlag: "Severe sudden abdominal rigidity, vomiting blood profusely, accidental poison ingestion.",
      condition: "Acute Poisoning / Gastrointestinal Bleeding",
      action: "Call Poison Help 1-800-222-1222 or 911. Do NOT induce vomiting unless instructed.",
      common: "Mild dyspepsia, gas, viral gastroenteritis, lactose intolerance."
    },
    allergic: {
      title: "Allergies & Anaphylaxis",
      redFlag: "Throat swelling, difficulty breathing, tongue enlargement, widespread hives.",
      condition: "Acute Severe Anaphylaxis",
      action: "Inject EpiPen auto-injector into outer thigh immediately & dial 911/112.",
      common: "Mild localized seasonal allergies, minor skin redness, sneezing."
    },
    crisis: {
      title: "Mental Health & Crisis Support",
      redFlag: "Active suicidal ideation, intent to self-harm, severe psychiatric distress.",
      condition: "Mental Health Crisis",
      action: "Call or text 988 (Suicide & Crisis Lifeline - free, 24/7, confidential) or call 911.",
      common: "Mild transient stress, sleep fatigue, work burnout."
    }
  };

  function renderRegion(key) {
    const data = regionData[key];
    if (!data) return;
    regionTitle.innerText = data.title;
    regionContent.innerHTML = `
      <div style="background:rgba(239,68,68,0.12); border-left:4px solid var(--accent-red); padding:16px; border-radius:8px; margin-bottom:14px;">
        <div style="font-weight:700; color:var(--accent-red); margin-bottom:4px;">🚨 Critical Red-Flag Warning Sign:</div>
        <p><strong>${data.redFlag}</strong></p>
        <div style="margin-top:8px; font-size:0.85rem; color:#fca5a5;">Possible condition: <strong>${data.condition}</strong></div>
        <div style="margin-top:10px; font-weight:700; color:white;">🚑 Action: ${data.action}</div>
      </div>
      <div style="background:var(--bg-primary); padding:14px; border-radius:8px; border:1px solid var(--border-color);">
        <strong style="color:var(--text-secondary); font-size:0.85rem;">Common Benign / Self-Limiting Symptoms:</strong>
        <p style="margin-top:4px; font-size:0.9rem;">${data.common}</p>
      </div>
    `;
  }

  regionButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      regionButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderRegion(btn.getAttribute('data-region'));
    });
  });

  renderRegion('chest');


  // --- TAB 5: Drug Monographs Explorer ---
  const monographsGrid = document.getElementById('monographsGrid');
  const monographSearchInput = document.getElementById('monographSearchInput');

  const sampleMonographs = [
    {
      name: "Paracetamol (Acetaminophen)",
      class: "Analgesic & Antipyretic",
      brands: "Tylenol, Panadol, Calpol, Mapap",
      uses: "Mild to moderate pain relief, fever reduction in children & adults.",
      sideEffects: "Nausea (mild), rare rash. Hepatotoxicity in overdose (>4g/day).",
      boxedWarning: "Black Box: Severe acute liver failure risk at doses over 4000mg/24h."
    },
    {
      name: "Ibuprofen",
      class: "Nonsteroidal Anti-inflammatory (NSAID)",
      brands: "Advil, Motrin, Nurofen, Brufen",
      uses: "Pain, inflammatory conditions, arthritis, dysmenorrhea, fever.",
      sideEffects: "Dyspepsia, GI ulceration/bleeding, acute renal strain.",
      boxedWarning: "Black Box: Serious cardiovascular thrombotic events & GI bleeding."
    },
    {
      name: "Lisinopril",
      class: "ACE Inhibitor (Antihypertensive)",
      brands: "Prinivil, Zestril, Qbrelis",
      uses: "Essential hypertension, heart failure, post-myocardial infarction.",
      sideEffects: "Dry cough, dizziness, hyperkalemia, angioedema.",
      boxedWarning: "Black Box: Fetal toxicity (discontinue immediately upon pregnancy)."
    },
    {
      name: "Metformin Hydrochloride",
      class: "Biguanide Antidiabetic",
      brands: "Glucophage, Fortamet, Glumetza",
      uses: "Type 2 Diabetes Mellitus, insulin resistance, PCOS.",
      sideEffects: "Diarrhea, nausea, metallic taste, B12 depletion.",
      boxedWarning: "Black Box: Lactic acidosis risk in renal impairment or alcohol excess."
    },
    {
      name: "Amoxicillin",
      class: "Beta-Lactam Antibiotic",
      brands: "Amoxil, Moxatag, Trimox",
      uses: "Bacterial respiratory infections, otitis media, strep throat.",
      sideEffects: "Diarrhea, nausea, rash. Anaphylaxis in penicillin allergy.",
      boxedWarning: "Caution: Finish full course to prevent antimicrobial resistance."
    },
    {
      name: "Atorvastatin Calcium",
      class: "HMG-CoA Reductase Inhibitor (Statin)",
      brands: "Lipitor, Atorva",
      uses: "Hypercholesterolemia, cardiovascular secondary event prevention.",
      sideEffects: "Myalgia, dyspepsia, mild elevation of transaminases.",
      boxedWarning: "Caution: Report unexplained muscle pain/dark urine (rhabdomyolysis)."
    }
  ];

  function renderMonographs(filter = '') {
    monographsGrid.innerHTML = '';
    const q = filter.toLowerCase();

    sampleMonographs
      .filter(m => m.name.toLowerCase().includes(q) || m.class.toLowerCase().includes(q) || m.brands.toLowerCase().includes(q))
      .forEach(m => {
        const card = document.createElement('div');
        card.className = 'monograph-card glass-card';
        card.innerHTML = `
          <div>
            <div class="mono-class-tag">${m.class}</div>
            <h4 class="mono-title">${m.name}</h4>
            <div class="mono-brands">Brands: ${m.brands}</div>
            <p><strong>Approved Uses:</strong> ${m.uses}</p>
            <p style="margin-top:6px;"><strong>Side Effects:</strong> ${m.sideEffects}</p>
            ${m.boxedWarning ? `<div class="mono-boxed-warning">⚠️ ${m.boxedWarning}</div>` : ''}
          </div>
          <button class="btn btn-sm btn-outline mt-3 ask-about-drug-btn" data-drug="${m.name}">
            <i class="fa-solid fa-message"></i> Ask AI about ${m.name.split(' ')[0]}
          </button>
        `;
        monographsGrid.appendChild(card);
      });

    document.querySelectorAll('.ask-about-drug-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const drug = btn.getAttribute('data-drug');
        switchTab('chatTab');
        handleSendMessage(`What is ${drug} used for and what are its side effects?`);
      });
    });
  }

  monographSearchInput.addEventListener('input', (e) => renderMonographs(e.target.value));
  renderMonographs();


  // --- TAB 6: Benchmark & Guardrail AI Dashboard ---
  const runLiveEvalBtn = document.getElementById('runLiveEvalBtn');
  const exportBenchmarkBtn = document.getElementById('exportBenchmarkBtn');
  const evalStatusText = document.getElementById('evalStatusText');
  const benchmarkTableBody = document.getElementById('benchmarkTableBody');

  let latestBenchmarkData = null;

  async function loadEvaluationResults() {
    evalStatusText.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Running 28-query automated test benchmark...';
    try {
      const resp = await fetch(`${API_BASE}/api/evaluate`);
      const data = await resp.json();
      latestBenchmarkData = data;

      document.getElementById('metricRecall').innerText = `${data.emergency_detection.recall}%`;
      document.getElementById('metricPolicy').innerText = `${data.policy_adherence_accuracy_percent}%`;
      document.getElementById('metricIntent').innerText = `${data.intent_classification_accuracy_percent}%`;
      document.getElementById('metricLatency').innerText = `${data.average_pipeline_latency_ms} ms`;

      evalStatusText.innerText = `Evaluated ${data.total_test_cases} test cases successfully at ${new Date().toLocaleTimeString()}`;

      benchmarkTableBody.innerHTML = '';
      data.detailed_results.forEach(row => {
        const isPass = row.intent_match && row.action_match;
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><code>${row.id}</code></td>
          <td>${row.category}</td>
          <td><em>"${row.query.substring(0, 45)}..."</em></td>
          <td><span style="font-size:0.8rem; color:var(--text-muted);">${row.expected_intent}</span></td>
          <td><strong style="color:var(--accent-blue); font-size:0.8rem;">${row.actual_intent}</strong></td>
          <td><span class="badge-pass">${isPass ? '✅ PASS' : '⚠️ MISMATCH'}</span></td>
          <td>${row.latency_ms} ms</td>
        `;
        benchmarkTableBody.appendChild(tr);
      });
    } catch (err) {
      evalStatusText.innerText = 'Failed to load evaluation benchmark results.';
    }
  }

  runLiveEvalBtn.addEventListener('click', loadEvaluationResults);
  exportBenchmarkBtn.addEventListener('click', () => {
    if (!latestBenchmarkData) return;
    const blob = new Blob([JSON.stringify(latestBenchmarkData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'guardrail_benchmark_results.json';
    a.click();
  });

  loadEvaluationResults();


  // --- TAB 7: WHO Guidelines Knowledge Base ---
  const whoCardsContainer = document.getElementById('whoCardsContainer');
  const sampleWhoArticles = [
    {
      tag: "WHO Essential Medicines",
      title: "Pain Management & Non-Opioid Analgesics",
      content: "Paracetamol and Ibuprofen form the baseline of global pain management. Paracetamol is preferred in gastrointestinal or renal vulnerabilities, while Ibuprofen targets acute musculoskeletal inflammation."
    },
    {
      tag: "Antimicrobial Resistance",
      title: "Global Action Plan on Antibiotic Stewardship",
      content: "Antibiotics are strictly indicated for bacterial infections. Taking antibiotics for viral colds or acute viral bronchitis accelerates antimicrobial resistance and diminishes future drug efficacy."
    },
    {
      tag: "Cardiovascular Health",
      title: "Hypertension Pharmacotherapy Guidelines",
      content: "ACE inhibitors (Lisinopril) and Calcium Channel Blockers (Amlodipine) represent first-line antihypertensive therapies. Routine combination with NSAIDs is discouraged due to blunted efficacy."
    },
    {
      tag: "Emergency Protocols",
      title: "Acute Coronary Syndrome & Stroke Recognition",
      content: "Immediate recognition of heart attacks (crushing chest pressure) and strokes (FAST signs) reduces permanent morbidity. Immediate emergency dispatch is paramount."
    }
  ];

  sampleWhoArticles.forEach(art => {
    const card = document.createElement('div');
    card.className = 'who-card glass-card';
    card.innerHTML = `
      <div class="who-tag"><i class="fa-solid fa-bookmark"></i> ${art.tag}</div>
      <h4>${art.title}</h4>
      <p>${art.content}</p>
    `;
    whoCardsContainer.appendChild(card);
  });
});
