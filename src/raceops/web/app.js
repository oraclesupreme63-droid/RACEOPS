"use strict";

const API_BASE = "/api/v1";
const TOKEN_KEY = "raceops.validation.token";

const state = {
  token: sessionStorage.getItem(TOKEN_KEY),
  identity: null,
  sessions: [],
  activeSessionId: null,
  workspace: null,
};

const roleLabels = {
  ADMINISTRATOR: "Administración",
  TEAM_MANAGER: "Team Manager",
  ENGINEER: "Ingeniería",
  MECHANIC: "Mecánica",
  DRIVER: "Piloto",
};

const statusLabels = {
  PLANNED: "Planificada",
  ACTIVE: "Activa",
  PAUSED: "Pausada",
  COMPLETED: "Completada",
  CANCELLED: "Cancelada",
  OPEN: "Resultados abiertos",
  LOCKED: "Resultados cerrados",
  PROPOSED: "Propuesta",
  IN_PROGRESS: "En curso",
  IMPROVED: "Mejoró",
  WORSENED: "Empeoró",
  NO_MEASURABLE_EFFECT: "Sin efecto medible",
  INCONCLUSIVE: "Inconcluso",
  NOT_EVALUATED: "Sin evaluar",
  SUPPORTED: "Respaldada",
  PARTIALLY_SUPPORTED: "Parcialmente respaldada",
  REJECTED: "Rechazada",
  DRIVER_TECHNIQUE: "Técnica del piloto",
  VEHICLE_SETUP: "Setup del vehículo",
  MECHANICAL: "Mecánica",
  TIRES: "Neumáticos",
  TRACK_ENVIRONMENT: "Pista / entorno",
  UNKNOWN: "Desconocida",
  DRIVING: "Conducción",
  ENGINEERING: "Ingeniería",
  LOW: "Baja",
  MEDIUM: "Media",
  HIGH: "Alta",
  TEAM: "Equipo",
  ROLE_RESTRICTED: "Roles autorizados",
  ENGINEERING_CONFIDENTIAL: "Ingeniería confidencial",
};

const capabilities = {
  ADMINISTRATOR: {
    feedback: false,
    observations: false,
    analysis: false,
    priorities: false,
    actions: false,
    outcomes: false,
  },
  TEAM_MANAGER: {
    feedback: true,
    observations: false,
    analysis: false,
    priorities: true,
    actions: true,
    outcomes: true,
  },
  ENGINEER: {
    feedback: true,
    observations: true,
    analysis: true,
    priorities: true,
    actions: true,
    outcomes: true,
  },
  MECHANIC: {
    feedback: true,
    observations: true,
    analysis: false,
    priorities: false,
    actions: true,
    outcomes: true,
  },
  DRIVER: {
    feedback: true,
    observations: false,
    analysis: false,
    priorities: false,
    actions: false,
    outcomes: false,
  },
};

class ApiError extends Error {
  constructor(status, payload) {
    super(payload?.detail || payload?.title || "No se pudo completar la solicitud.");
    this.status = status;
    this.payload = payload;
  }
}

const $ = (selector, scope = document) => scope.querySelector(selector);
const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];

document.addEventListener("DOMContentLoaded", () => {
  bindStaticEvents();
  if (state.token) {
    boot().catch(handleBootError);
  } else {
    showLogin();
  }
});

function bindStaticEvents() {
  $("#login-form").addEventListener("submit", login);
  $("#logout-button").addEventListener("click", logout);
  $("#refresh-sessions").addEventListener("click", () => loadSessions(true));

  $$(".tab-button").forEach((button) => {
    button.addEventListener("click", () => selectTab(button.dataset.tab));
  });

  $("#toggle-observation-form").addEventListener("click", () => {
    $("#observation-form").classList.toggle("is-hidden");
  });
  $$(".form-cancel").forEach((button) => {
    button.addEventListener("click", () => {
      button.closest("form").classList.add("is-hidden");
    });
  });

  $("#feedback-form").addEventListener("submit", submitFeedback);
  $("#observation-form").addEventListener("submit", submitObservation);
  $("#analysis-form").addEventListener("submit", submitAnalysis);
  $("#hypothesis-form").addEventListener("submit", submitHypothesis);
  $("#priority-form").addEventListener("submit", submitPriority);
  $("#action-form").addEventListener("submit", submitAction);
  $("#outcome-form").addEventListener("submit", submitOutcome);

  $("#actions-content").addEventListener("click", handleActionClick);
  $("#learning-content").addEventListener("click", handleLearningClick);
  $("#session-list").addEventListener("click", (event) => {
    const button = event.target.closest("[data-session-id]");
    if (button) openSession(button.dataset.sessionId);
  });

  $$(".modal-close").forEach((button) => {
    button.addEventListener("click", () => button.closest("dialog").close());
  });
  $$("dialog").forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) dialog.close();
    });
  });
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("Accept", "application/json");
  if (state.token) headers.set("Authorization", `Bearer ${state.token}`);
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("json")
    ? await response.json()
    : null;

  if (!response.ok) {
    if (response.status === 401 && path !== "/auth/login") {
      logout("Tu sesión expiró. Vuelve a entrar.");
    }
    throw new ApiError(response.status, payload);
  }
  return payload;
}

async function optionalApi(path) {
  try {
    return await api(path);
  } catch (error) {
    if (error instanceof ApiError && [403, 404].includes(error.status)) return null;
    throw error;
  }
}

async function login(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const button = $("button[type='submit']", form);
  const errorRegion = $("#login-error");
  const payload = {
    email: $("#login-email").value.trim(),
    password: $("#login-password").value,
  };
  const teamId = $("#login-team").value;
  if (!$("#team-field").classList.contains("is-hidden") && teamId) {
    payload.team_id = teamId;
  }

  setButtonBusy(button, true, "Entrando…");
  errorRegion.textContent = "";
  try {
    const result = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.token = result.access_token;
    sessionStorage.setItem(TOKEN_KEY, state.token);
    $("#login-password").value = "";
    await boot();
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.status === 409 &&
      error.payload?.code === "team_context_required"
    ) {
      populateTeamChoices(error.payload.teams || []);
      errorRegion.textContent = "Selecciona el equipo con el que quieres trabajar.";
    } else {
      errorRegion.textContent = humanError(error);
    }
  } finally {
    setButtonBusy(button, false);
  }
}

function populateTeamChoices(teams) {
  const select = $("#login-team");
  select.innerHTML = teams
    .map(
      (team) =>
        `<option value="${escapeHtml(team.team_id)}">${escapeHtml(team.name)}</option>`,
    )
    .join("");
  $("#team-field").classList.remove("is-hidden");
  select.focus();
}

async function boot() {
  setBusy(true, "Preparando el pit wall…");
  try {
    state.identity = await api("/auth/me");
    showApplication();
    await loadSessions(false);
  } finally {
    setBusy(false);
  }
}

function handleBootError(error) {
  sessionStorage.removeItem(TOKEN_KEY);
  state.token = null;
  showLogin();
  $("#login-error").textContent = humanError(error);
}

function showLogin() {
  $("#login-view").classList.remove("is-hidden");
  $("#app-shell").classList.add("is-hidden");
}

function showApplication() {
  $("#login-view").classList.add("is-hidden");
  $("#app-shell").classList.remove("is-hidden");
  $("#identity-team").textContent = state.identity.team.name;
  $("#identity-role").textContent = roleLabels[currentRole()] || currentRole();
  applyRoleCapabilities();
}

function logout(message = "") {
  sessionStorage.removeItem(TOKEN_KEY);
  state.token = null;
  state.identity = null;
  state.sessions = [];
  state.activeSessionId = null;
  state.workspace = null;
  $("#team-field").classList.add("is-hidden");
  $("#workspace").classList.add("is-hidden");
  $("#workspace-empty").classList.remove("is-hidden");
  showLogin();
  if (message) $("#login-error").textContent = message;
}

function applyRoleCapabilities() {
  const allowed = currentCapabilities();
  toggle("#feedback-form", allowed.feedback);
  toggle("#toggle-observation-form", allowed.observations);
  toggle("#analysis-editor", allowed.analysis);
  toggle("#analysis-locked", !allowed.analysis);
  toggle("#decision-editor", allowed.priorities || allowed.actions);
  toggle("#priority-form", allowed.priorities);
  toggle("#action-form", allowed.actions);
  $$(".engineering-only-field").forEach((element) => {
    element.classList.toggle("is-hidden", currentRole() !== "ENGINEER");
  });
}

async function loadSessions(preserveSelection = true) {
  try {
    const page = await api("/sessions?limit=100&offset=0");
    state.sessions = [...page.items].sort(
      (a, b) => new Date(b.scheduled_at) - new Date(a.scheduled_at),
    );
    renderSessionList();
    if (
      preserveSelection &&
      state.activeSessionId &&
      state.sessions.some((item) => item.session_id === state.activeSessionId)
    ) {
      await openSession(state.activeSessionId, false);
    }
  } catch (error) {
    toast(humanError(error), true);
  }
}

function renderSessionList() {
  const container = $("#session-list");
  $("#session-empty").classList.toggle("is-hidden", state.sessions.length > 0);
  container.innerHTML = state.sessions
    .map((session) => {
      const date = new Date(session.scheduled_at);
      const active = session.session_id === state.activeSessionId;
      return `
        <button
          class="session-card ${active ? "is-active" : ""}"
          type="button"
          data-session-id="${escapeHtml(session.session_id)}"
        >
          <div class="session-card__top">
            <span>${escapeHtml(formatShortDate(date))}</span>
            <span class="status-mini">${escapeHtml(label(session.status))}</span>
          </div>
          <h3>${escapeHtml(session.session_type)}</h3>
          <div class="session-card__meta">
            <span>${escapeHtml(formatClock(date))}</span>
            <span>${escapeHtml(label(session.results_status))}</span>
          </div>
        </button>
      `;
    })
    .join("");
}

async function openSession(sessionId, showLoader = true) {
  state.activeSessionId = sessionId;
  renderSessionList();
  if (showLoader) setBusy(true);
  try {
    const session = await api(`/sessions/${sessionId}`);
    const [event, driver, vehicle] = await Promise.all([
      optionalApi(`/events/${session.event_id}`),
      optionalApi(`/drivers/${session.driver_id}`),
      optionalApi(`/vehicles/${session.vehicle_id}`),
    ]);
    const track = event ? await optionalApi(`/tracks/${event.track_id}`) : null;
    const engineering = currentRole() === "ENGINEER";

    const [feedback, summary, laps, conditions, observations, priorities, actions, analysisData] =
      await Promise.all([
        optionalApi(`/sessions/${sessionId}/feedback?limit=100`),
        optionalApi(`/sessions/${sessionId}/results-summary`),
        optionalApi(`/sessions/${sessionId}/laps?limit=100`),
        optionalApi(`/sessions/${sessionId}/conditions`),
        optionalApi(`/observations?session_id=${encodeURIComponent(sessionId)}&limit=100`),
        optionalApi(`/sessions/${sessionId}/priorities?limit=100`),
        optionalApi(`/sessions/${sessionId}/actions?limit=100`),
        engineering
          ? optionalApi(`/sessions/${sessionId}/analyses`)
          : optionalApi(`/sessions/${sessionId}/analysis-summaries`),
      ]);

    const analyses = engineering ? analysisData || [] : [];
    const summaries = engineering ? [] : analysisData || [];
    const hypotheses = engineering
      ? (
          await Promise.all(
            analyses.map((item) => optionalApi(`/analyses/${item.analysis_id}/hypotheses`)),
          )
        ).flatMap((items) => items || [])
      : [];

    state.workspace = {
      session,
      event,
      track,
      driver,
      vehicle,
      feedback: feedback?.items || [],
      summary,
      laps: laps?.items || [],
      conditions,
      observations: observations?.items || [],
      priorities: priorities?.items || [],
      actions: actions?.items || [],
      analyses,
      summaries,
      hypotheses,
    };
    renderWorkspace();
  } catch (error) {
    toast(humanError(error), true);
  } finally {
    if (showLoader) setBusy(false);
  }
}

function renderWorkspace() {
  const data = state.workspace;
  if (!data) return;
  $("#workspace-empty").classList.add("is-hidden");
  $("#workspace").classList.remove("is-hidden");

  const scheduled = new Date(data.session.scheduled_at);
  $("#session-status").textContent = label(data.session.status);
  $("#session-results-status").textContent = label(data.session.results_status);
  $("#session-event").textContent = data.event?.name || "Evento no disponible";
  $("#session-title").textContent = data.session.session_type;
  $("#session-context").textContent = [
    data.track?.name,
    data.driver?.display_name,
    data.vehicle?.identifier,
  ]
    .filter(Boolean)
    .join(" · ");
  $("#session-date").textContent = formatLongDate(scheduled);
  $("#session-time").textContent = formatClock(scheduled);

  renderMetrics(data);
  renderConditions(data.conditions);
  renderLaps(data.laps, data.summary);
  renderObservations(data.observations);
  renderFeedback(data.feedback);
  renderAnalysis(data);
  renderPriorities(data.priorities);
  renderActions(data.actions);
  renderLearning(data.actions);
  populateDecisionSelects(data);

  $("#feedback-count").textContent = String(data.feedback.length);
  $("#action-count").textContent = String(data.actions.length);
}

function renderMetrics(data) {
  const summary = data.summary || {};
  const metrics = [
    ["Mejor vuelta", formatDuration(summary.best_lap_us), "vueltas válidas"],
    ["Promedio", formatDuration(summary.average_lap_us), "ritmo de sesión"],
    ["Consistencia", formatDelta(summary.consistency_us), "desviación estándar"],
    ["Vueltas", summary.total_laps ?? "—", `${summary.eligible_laps ?? 0} elegibles`],
  ];
  $("#metric-strip").innerHTML = metrics
    .map(
      ([name, value, note]) => `
        <div class="metric-card">
          <span>${escapeHtml(name)}</span>
          <strong>${escapeHtml(String(value))}</strong>
          <small>${escapeHtml(note)}</small>
        </div>
      `,
    )
    .join("");
}

function renderConditions(conditions) {
  const container = $("#conditions-content");
  if (!conditions) {
    container.innerHTML = emptyRecord("No se registraron condiciones para esta sesión.");
    return;
  }
  const values = [
    [
      "Ambiente",
      measurement(conditions.ambient_temperature, conditions.ambient_temperature_unit),
    ],
    ["Pista", measurement(conditions.track_temperature, conditions.track_temperature_unit)],
    ["Clima", conditions.weather || "—"],
    ["Superficie", conditions.track_condition || "—"],
    ["Fuente", conditions.source || "Manual"],
  ];
  container.innerHTML = values
    .map(
      ([name, value]) => `
        <div class="detail-item">
          <span>${escapeHtml(name)}</span>
          <strong>${escapeHtml(String(value))}</strong>
        </div>
      `,
    )
    .join("");
}

function renderLaps(laps, summary) {
  const container = $("#laps-content");
  if (!laps.length) {
    container.innerHTML = emptyRecord("Todavía no hay vueltas registradas.");
    return;
  }
  container.innerHTML = [...laps]
    .sort((a, b) => a.lap_number - b.lap_number)
    .map(
      (lap) => `
        <div class="lap-row ${lap.lap_id === summary?.best_lap_id ? "is-best" : ""}">
          <span>V ${escapeHtml(lap.lap_number)}</span>
          <strong>${escapeHtml(formatDuration(lap.duration_us))}</strong>
          <small>${escapeHtml(label(lap.classification))}</small>
        </div>
      `,
    )
    .join("");
}

function renderObservations(observations) {
  const container = $("#observations-content");
  if (!observations.length) {
    container.innerHTML = emptyRecord("No hay observaciones técnicas visibles.");
    return;
  }
  container.innerHTML = observations
    .map(
      (item) => `
        <article class="record-card">
          <div class="record-card__meta">
            <span>${escapeHtml(item.category || "Observación")}</span>
            <span>${escapeHtml(label(item.visibility_level))}</span>
            <span>${escapeHtml(formatRelativeDate(item.created_at))}</span>
          </div>
          <p>${escapeHtml(item.description)}</p>
        </article>
      `,
    )
    .join("");
}

function renderFeedback(feedback) {
  const container = $("#feedback-content");
  if (!feedback.length) {
    container.innerHTML = emptyRecord("Aún no se ha registrado feedback del piloto.");
    return;
  }
  container.innerHTML = feedback
    .map((item) => {
      const context = [
        item.corner_or_zone,
        item.driving_phase,
        item.severity ? `Severidad ${label(item.severity)}` : null,
        item.confidence ? `Confianza ${label(item.confidence)}` : null,
      ].filter(Boolean);
      return `
        <article class="feedback-card">
          <div class="feedback-card__meta">
            ${context.map((value) => `<span>${escapeHtml(value)}</span>`).join("")}
            <span>${escapeHtml(formatRelativeDate(item.created_at))}</span>
          </div>
          <p>${escapeHtml(item.description)}</p>
        </article>
      `;
    })
    .join("");
}

function renderAnalysis(data) {
  const container = $("#analysis-content");
  if (currentRole() !== "ENGINEER") {
    if (!data.summaries.length) {
      container.innerHTML = emptyRecord("Ingeniería no ha compartido un resumen para este rol.");
      return;
    }
    container.innerHTML = data.summaries
      .map(
        (item) => `
          <article class="analysis-card">
            <div class="analysis-card__meta">
              <span>Resumen autorizado</span>
              <span>${escapeHtml(formatRelativeDate(item.updated_at))}</span>
            </div>
            <p>${escapeHtml(item.authorized_summary)}</p>
          </article>
        `,
      )
      .join("");
    return;
  }

  renderEvidenceOptions(data);
  if (!data.analyses.length) {
    container.innerHTML = emptyRecord("Aún no existe un análisis técnico para esta sesión.");
    return;
  }
  container.innerHTML = data.analyses
    .map((analysis, index) => {
      const related = data.hypotheses.filter(
        (item) => item.analysis_id === analysis.analysis_id,
      );
      return `
        <article class="analysis-card">
          <div class="analysis-card__meta">
            <span>Análisis ${index + 1}</span>
            <span>${analysis.evidence.length} fuentes</span>
            <span>Ingeniería confidencial</span>
          </div>
          <h3>${escapeHtml(analysis.technical_detail)}</h3>
          ${
            analysis.authorized_summary
              ? `<p class="analysis-card__summary">${escapeHtml(analysis.authorized_summary)}</p>`
              : ""
          }
          ${related.map(renderHypothesis).join("")}
        </article>
      `;
    })
    .join("");
}

function renderHypothesis(item) {
  return `
    <div class="hypothesis-row">
      <strong>${escapeHtml(label(item.status))} · ${escapeHtml(label(item.confidence))}</strong>
      <p>${escapeHtml(item.description)}</p>
      <div class="decision-meta">
        <span>${escapeHtml(label(item.cause_classification))}</span>
      </div>
    </div>
  `;
}

function renderEvidenceOptions(data) {
  const options = [
    ...data.feedback.map((item) => ({
      type: "DRIVER_FEEDBACK",
      id: item.feedback_id,
      text: `Feedback: ${item.description}`,
    })),
    ...data.laps.map((item) => ({
      type: "LAP",
      id: item.lap_id,
      text: `Vuelta ${item.lap_number}: ${formatDuration(item.duration_us)}`,
    })),
    ...data.observations.map((item) => ({
      type: "OBSERVATION",
      id: item.observation_id,
      text: `Observación: ${item.description}`,
    })),
    ...(data.conditions
      ? [
          {
            type: "CONDITION",
            id: data.conditions.condition_id,
            text: "Condiciones de la sesión",
          },
        ]
      : []),
  ];
  $("#evidence-options").innerHTML = options.length
    ? options
        .map(
          (item) => `
            <label class="check-option">
              <input
                type="checkbox"
                value="${escapeHtml(item.id)}"
                data-evidence-type="${escapeHtml(item.type)}"
              >
              <span title="${escapeHtml(item.text)}">${escapeHtml(item.text)}</span>
            </label>
          `,
        )
        .join("")
    : emptyRecord("Registra feedback, vueltas u observaciones antes de analizar.");
}

function renderPriorities(priorities) {
  const container = $("#priorities-content");
  if (!priorities.length) {
    container.innerHTML = emptyRecord("No hay prioridades definidas.");
    return;
  }
  container.innerHTML = [...priorities]
    .sort((a, b) => (a.rank || 99) - (b.rank || 99))
    .map(
      (item) => `
        <article class="priority-card">
          <span class="priority-rank">${escapeHtml(item.rank || "·")}</span>
          <div>
            <div class="decision-meta">
              <span>${escapeHtml(roleLabels[item.recipient_role] || item.recipient_role)}</span>
              <span>${escapeHtml(label(item.target_intent))}</span>
            </div>
            <p>${escapeHtml(item.description)}</p>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderActions(actions) {
  const container = $("#actions-content");
  if (!actions.length) {
    container.innerHTML = emptyRecord("No hay acciones asignadas.");
    return;
  }
  container.innerHTML = actions.map(renderActionCard).join("");
}

function renderActionCard(action) {
  const assigned = isAssignedToCurrentActor(action);
  const transition = nextActionTransition(action.status);
  const canTransition = assigned && transition && currentRole() !== "ADMINISTRATOR";
  const canEvaluate =
    currentCapabilities().outcomes &&
    action.status === "COMPLETED" &&
    action.evaluation_status === "NOT_EVALUATED";
  return `
    <article class="action-card" data-state="${escapeHtml(action.status)}">
      <div class="action-card__header">
        <div>
          <div class="decision-meta">
            <span>${escapeHtml(roleLabels[action.assignee_role] || action.assignee_role)}</span>
            <span>${escapeHtml(label(action.action_type))}</span>
          </div>
          <h4>${escapeHtml(action.public_summary || "Acción técnica restringida")}</h4>
        </div>
        <span class="status-pill status-pill--muted">${escapeHtml(label(action.status))}</span>
      </div>
      ${
        action.confidential_detail
          ? `<p class="confidential-note">${escapeHtml(action.confidential_detail)}</p>`
          : ""
      }
      <div class="action-card__buttons">
        ${
          canTransition
            ? `<button class="button button--secondary button--small" type="button" data-transition="${transition.command}" data-action-id="${escapeHtml(action.action_id)}">${escapeHtml(transition.label)}</button>`
            : ""
        }
        ${
          canEvaluate
            ? `<button class="button button--primary button--small" type="button" data-evaluate data-action-id="${escapeHtml(action.action_id)}">Evaluar</button>`
            : ""
        }
        <button class="button button--ghost button--small" type="button" data-learning data-action-id="${escapeHtml(action.action_id)}">Ver cadena</button>
        <span class="status-pill status-pill--muted">${escapeHtml(label(action.evaluation_status))}</span>
      </div>
    </article>
  `;
}

function renderLearning(actions) {
  const container = $("#learning-content");
  if (!actions.length) {
    container.innerHTML = emptyRecord("La memoria del equipo aparecerá cuando exista una acción.");
    return;
  }
  container.innerHTML = actions
    .map(
      (action) => `
        <article class="learning-card">
          <div>
            <div class="decision-meta">
              <span>${escapeHtml(label(action.action_type))}</span>
              <span>${escapeHtml(label(action.evaluation_status))}</span>
            </div>
            <h3>${escapeHtml(action.public_summary || "Acción restringida")}</h3>
          </div>
          <button class="button button--secondary button--small" type="button" data-learning data-action-id="${escapeHtml(action.action_id)}">Abrir →</button>
        </article>
      `,
    )
    .join("");
}

function populateDecisionSelects(data) {
  setSelectOptions(
    $("#hypothesis-form select[name='analysis_id']"),
    data.analyses.map((item, index) => ({
      value: item.analysis_id,
      label: `Análisis ${index + 1}: ${truncate(item.technical_detail, 60)}`,
    })),
    "Primero crea un análisis",
  );
  setSelectOptions(
    $("#priority-form select[name='hypothesis_id']"),
    data.hypotheses.map((item) => ({
      value: item.hypothesis_id,
      label: truncate(item.description, 65),
    })),
    "Sin hipótesis relacionada",
    true,
  );
  setSelectOptions(
    $("#action-form select[name='priority_id']"),
    data.priorities.map((item) => ({
      value: item.priority_id,
      label: `${item.rank || "·"} · ${truncate(item.description, 60)}`,
    })),
    "Sin prioridad relacionada",
    true,
  );
}

function setSelectOptions(select, options, emptyLabel, allowEmpty = false) {
  if (!select) return;
  const empty = `<option value="">${escapeHtml(emptyLabel)}</option>`;
  select.innerHTML = `${allowEmpty || !options.length ? empty : ""}${options
    .map(
      (item) =>
        `<option value="${escapeHtml(item.value)}">${escapeHtml(item.label)}</option>`,
    )
    .join("")}`;
  select.disabled = !allowEmpty && !options.length;
}

async function submitFeedback(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = compactPayload(form, [
    "description",
    "corner_or_zone",
    "driving_phase",
    "severity",
    "confidence",
  ]);
  await submitAndReload(
    form,
    `/sessions/${state.activeSessionId}/feedback`,
    payload,
    "Feedback registrado.",
  );
}

async function submitObservation(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = compactPayload(form, ["description", "category", "visibility_level"]);
  payload.session_id = state.activeSessionId;
  await submitAndReload(form, "/observations", payload, "Observación guardada.");
  form.classList.add("is-hidden");
}

async function submitAnalysis(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const evidence = $$('input[type="checkbox"]:checked', $("#evidence-options")).map(
    (input) => ({
      evidence_type: input.dataset.evidenceType,
      reference_id: input.value,
    }),
  );
  if (!evidence.length) {
    toast("Selecciona al menos una evidencia para el análisis.", true);
    return;
  }
  const payload = compactPayload(form, ["technical_detail", "authorized_summary"]);
  payload.evidence = evidence;
  await submitAndReload(
    form,
    `/sessions/${state.activeSessionId}/analyses`,
    payload,
    "Análisis guardado con su evidencia.",
  );
}

async function submitHypothesis(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = compactPayload(form, [
    "description",
    "cause_classification",
    "confidence",
  ]);
  const analysisId = form.elements.analysis_id.value;
  if (!analysisId) {
    toast("Primero crea o selecciona un análisis.", true);
    return;
  }
  await submitAndReload(
    form,
    `/analyses/${analysisId}/hypotheses`,
    payload,
    "Hipótesis propuesta sin asumir certeza.",
  );
}

async function submitPriority(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = compactPayload(form, ["description", "recipient_role", "hypothesis_id"]);
  payload.target_intent = "NEXT_SESSION";
  payload.is_main = true;
  payload.rank = Number(form.elements.rank.value);
  await submitAndReload(
    form,
    `/sessions/${state.activeSessionId}/priorities`,
    payload,
    "Prioridad añadida para la siguiente sesión.",
  );
}

async function submitAction(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = compactPayload(form, [
    "assignee_role",
    "action_type",
    "public_summary",
    "confidential_detail",
    "priority_id",
  ]);
  payload.target_intent = "NEXT_SESSION";
  await submitAndReload(
    form,
    `/sessions/${state.activeSessionId}/actions`,
    payload,
    "Acción asignada.",
  );
}

async function submitOutcome(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const actionId = form.elements.action_id.value;
  const payload = compactPayload(form, [
    "evaluation_session_id",
    "classification",
    "public_conclusion",
    "confidential_conclusion",
    "concluded_hypothesis_status",
  ]);
  const button = $("button[type='submit']", form);
  setButtonBusy(button, true, "Guardando…");
  try {
    await api(`/actions/${actionId}/outcome`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    $("#outcome-dialog").close();
    form.reset();
    toast("Resultado registrado. El aprendizaje ya es recuperable.");
    await openSession(state.activeSessionId, false);
  } catch (error) {
    toast(humanError(error), true);
  } finally {
    setButtonBusy(button, false);
  }
}

async function submitAndReload(form, path, payload, successMessage) {
  const button = $("button[type='submit']", form);
  setButtonBusy(button, true, "Guardando…");
  try {
    await api(path, { method: "POST", body: JSON.stringify(payload) });
    form.reset();
    toast(successMessage);
    await openSession(state.activeSessionId, false);
  } catch (error) {
    toast(humanError(error), true);
  } finally {
    setButtonBusy(button, false);
  }
}

async function handleActionClick(event) {
  const transitionButton = event.target.closest("[data-transition]");
  const evaluateButton = event.target.closest("[data-evaluate]");
  const learningButton = event.target.closest("[data-learning]");
  if (transitionButton) {
    await transitionAction(
      transitionButton.dataset.actionId,
      transitionButton.dataset.transition,
      transitionButton,
    );
  } else if (evaluateButton) {
    openOutcomeDialog(evaluateButton.dataset.actionId);
  } else if (learningButton) {
    await openLearningChain(learningButton.dataset.actionId);
  }
}

async function handleLearningClick(event) {
  const button = event.target.closest("[data-learning]");
  if (button) await openLearningChain(button.dataset.actionId);
}

async function transitionAction(actionId, command, button) {
  setButtonBusy(button, true, "Actualizando…");
  try {
    await api(`/actions/${actionId}/${command}`, { method: "POST" });
    toast("Estado de la acción actualizado.");
    await openSession(state.activeSessionId, false);
  } catch (error) {
    toast(humanError(error), true);
  } finally {
    setButtonBusy(button, false);
  }
}

function openOutcomeDialog(actionId) {
  const form = $("#outcome-form");
  form.reset();
  form.elements.action_id.value = actionId;
  const source = state.workspace.session;
  const laterSessions = state.sessions.filter(
    (item) =>
      item.session_id !== source.session_id &&
      new Date(item.scheduled_at) > new Date(source.scheduled_at),
  );
  setSelectOptions(
    form.elements.evaluation_session_id,
    laterSessions.map((item) => ({
      value: item.session_id,
      label: `${item.session_type} · ${formatShortDate(new Date(item.scheduled_at))}`,
    })),
    "No existe una sesión posterior",
  );
  $("#outcome-dialog").showModal();
}

async function openLearningChain(actionId) {
  const dialog = $("#learning-dialog");
  const content = $("#learning-chain-content");
  content.innerHTML = emptyRecord("Cargando la cadena autorizada…");
  dialog.showModal();
  try {
    const chain = await api(`/actions/${actionId}/learning-chain`);
    content.innerHTML = renderChain(chain);
  } catch (error) {
    content.innerHTML = emptyRecord(humanError(error));
  }
}

function renderChain(chain) {
  const nodes = [];
  if (chain.analysis) {
    nodes.push([
      "Análisis",
      "Evidencia interpretada",
      chain.analysis.technical_detail || chain.analysis.authorized_summary,
    ]);
  }
  if (chain.hypothesis) {
    nodes.push([
      "Hipótesis",
      label(chain.hypothesis.status),
      chain.hypothesis.description,
    ]);
  }
  if (chain.priority) {
    nodes.push([
      "Prioridad",
      roleLabels[chain.priority.recipient_role] || chain.priority.recipient_role,
      chain.priority.description,
    ]);
  }
  nodes.push([
    "Acción",
    label(chain.action.status),
    chain.action.public_summary || "Detalle técnico restringido para este rol.",
  ]);
  if (chain.evaluation?.outcome) {
    nodes.push([
      "Resultado",
      label(chain.evaluation.outcome.classification),
      chain.evaluation.outcome.public_conclusion ||
        chain.evaluation.outcome.confidential_conclusion ||
        "Conclusión restringida.",
    ]);
  } else {
    nodes.push([
      "Resultado",
      "Pendiente",
      "La acción todavía no tiene una evaluación posterior.",
    ]);
  }
  return nodes
    .map(
      ([type, title, description]) => `
        <section class="chain-node">
          <span>${escapeHtml(type)}</span>
          <h3>${escapeHtml(title)}</h3>
          <p>${escapeHtml(description || "—")}</p>
        </section>
      `,
    )
    .join("");
}

function selectTab(name) {
  $$(".tab-button").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.tab === name);
  });
  $$(".tab-panel").forEach((panel) => panel.classList.add("is-hidden"));
  $(`#tab-${name}`).classList.remove("is-hidden");
}

function compactPayload(form, names) {
  return names.reduce((payload, name) => {
    const field = form.elements[name];
    if (!field) return payload;
    const value = typeof field.value === "string" ? field.value.trim() : field.value;
    if (value !== "") payload[name] = value;
    return payload;
  }, {});
}

function currentRole() {
  return state.identity?.membership.role || "";
}

function currentCapabilities() {
  return capabilities[currentRole()] || capabilities.ADMINISTRATOR;
}

function isAssignedToCurrentActor(action) {
  if (action.assignee_user_id) {
    return action.assignee_user_id === state.identity.user.user_id;
  }
  return action.assignee_role === currentRole();
}

function nextActionTransition(status) {
  const transitions = {
    PROPOSED: { command: "plan", label: "Planificar" },
    PLANNED: { command: "start", label: "Iniciar" },
    IN_PROGRESS: { command: "complete", label: "Completar" },
  };
  return transitions[status] || null;
}

function toggle(selector, visible) {
  const element = $(selector);
  if (element) element.classList.toggle("is-hidden", !visible);
}

function setBusy(busy, text = "Cargando datos de la sesión…") {
  $("#busy-overlay").classList.toggle("is-hidden", !busy);
  $("#busy-overlay span:last-child").textContent = text;
}

function setButtonBusy(button, busy, busyLabel = "Procesando…") {
  if (!button) return;
  if (busy) {
    button.dataset.originalLabel = button.textContent;
    button.textContent = busyLabel;
    button.disabled = true;
  } else {
    button.textContent = button.dataset.originalLabel || button.textContent;
    button.disabled = false;
  }
}

function toast(message, isError = false) {
  const item = document.createElement("div");
  item.className = `toast${isError ? " is-error" : ""}`;
  item.textContent = message;
  $("#toast-region").append(item);
  window.setTimeout(() => item.remove(), 4800);
}

function humanError(error) {
  if (error instanceof ApiError) {
    const translatedProblems = {
      invalid_credentials: "El correo, la contraseña o el equipo no son válidos.",
      team_context_required: "Selecciona el equipo con el que quieres entrar.",
    };
    if (translatedProblems[error.payload?.code]) {
      return translatedProblems[error.payload.code];
    }
    if (error.status === 403) return "Este rol no tiene permiso para esa tarea.";
    if (error.status === 404) return "El recurso no existe o no es visible para este rol.";
    if (error.status === 409) return error.message || "El estado actual impide esta acción.";
    if (error.status === 422) return error.message || "Revisa los datos del formulario.";
    return error.message;
  }
  if (error instanceof TypeError) return "No fue posible conectar con RaceOps.";
  return "Ocurrió un error inesperado.";
}

function label(value) {
  if (value === null || value === undefined || value === "") return "—";
  return statusLabels[value] || roleLabels[value] || String(value).replaceAll("_", " ");
}

function measurement(value, unit) {
  if (value === null || value === undefined) return "—";
  return `${value} ${unit || ""}`.trim();
}

function formatDuration(microseconds) {
  if (!microseconds) return "—";
  const totalMilliseconds = Math.round(microseconds / 1000);
  const minutes = Math.floor(totalMilliseconds / 60000);
  const seconds = Math.floor((totalMilliseconds % 60000) / 1000);
  const milliseconds = totalMilliseconds % 1000;
  return `${minutes}:${String(seconds).padStart(2, "0")}.${String(milliseconds).padStart(3, "0")}`;
}

function formatDelta(microseconds) {
  if (microseconds === null || microseconds === undefined) return "—";
  return `±${(microseconds / 1_000_000).toFixed(3)} s`;
}

function formatShortDate(date) {
  return new Intl.DateTimeFormat("es-MX", {
    day: "2-digit",
    month: "short",
  }).format(date);
}

function formatLongDate(date) {
  return new Intl.DateTimeFormat("es-MX", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(date);
}

function formatClock(date) {
  return new Intl.DateTimeFormat("es-MX", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function formatRelativeDate(value) {
  const date = new Date(value);
  return `${formatShortDate(date)} · ${formatClock(date)}`;
}

function emptyRecord(message) {
  return `<div class="record-empty">${escapeHtml(message)}</div>`;
}

function truncate(value, length) {
  const text = String(value || "");
  return text.length > length ? `${text.slice(0, length - 1)}…` : text;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
