/* ==========================================================================
   Appointment booking  —  contact/appointments/
   --------------------------------------------------------------------------
   What this file does
     1. Loads availability.json (your hours, topics, rules).
     2. Asks the backend which slots are already taken, and subtracts them.
     3. Draws the calendar and time slots, all in Europe/Berlin local time.
     4. Validates the form and sends the request to the backend.

   Configuration is read from data-* attributes on <form id="booking">:
     data-api        base URL of the backend's api/ folder on the LRZ site
                     (see BACKEND-PLAN.md). Leave EMPTY for demo mode: no
                     network calls, a few pretend bookings, and "Submit" just
                     shows the confirmation page.

   All user-visible text lives in the I18N table below — German first, then
   English. To change wording, edit it there; the HTML only carries keys.
   ========================================================================== */

(function () {
	"use strict";

	/* ======================================================================
	   TEXT  (EDIT wording here)
	   ====================================================================== */

	var I18N = {
		de: {
			title:          "Termin vereinbaren",
			intro:          "Wählen Sie ein Thema, ein Format sowie Datum und Uhrzeit. Ich bestätige Ihre Anfrage per E-Mail, sobald ich sie geprüft habe.",
			demo:           "Vorschau-Modus: Diese Seite ist noch nicht mit dem Buchungssystem verbunden. Anfragen werden nicht gesendet.",
			step_topic:     "Thema",
			step_format:    "Format",
			step_when:      "Datum und Uhrzeit",
			step_details:   "Ihre Angaben",
			step_confirm:   "Prüfen und absenden",
			topic_label:    "Worum geht es?",
			topic_choose:   "Bitte wählen …",
			format_label:   "Wie möchten Sie den Termin wahrnehmen?",
			pick_day:       "Wählen Sie zuerst einen Tag; verfügbare Tage sind hervorgehoben.",
			pick_time:      "Verfügbare Uhrzeiten am",
			no_slots:       "An diesem Tag sind keine Termine mehr frei.",
			pick_topic_first: "Bitte wählen Sie zuerst ein Thema, damit die passenden Zeiten angezeigt werden können.",
			tz:             "Alle Zeiten sind mitteleuropäische Zeit (Europe/Berlin).",
			minutes:        "Min.",
			name:           "Name",
			email:          "E-Mail-Adresse",
			email_hint:     "An diese Adresse senden wir die Bestätigung.",
			message:        "Nachricht",
			message_hint:   "Worum geht es genau? Was soll vorab bekannt sein?",
			files:          "Dokumente anhängen",
			files_hint:     "Nur PDF, höchstens 50 MB pro Datei, bis zu 3 Dateien.",
			optional:       "(optional)",
			file_too_big:   "zu groß (max. 50 MB)",
			file_not_pdf:   "keine PDF-Datei",
			file_too_many:  "Höchstens 3 Dateien.",
			summary_title:  "Ihre Anfrage",
			summary_empty:  "Noch nichts ausgewählt.",
			s_topic:        "Thema",
			s_format:       "Format",
			s_when:         "Termin",
			s_length:       "Dauer",
			consent:        "Ich habe die Hinweise zum Datenschutz gelesen und bin mit der Verarbeitung meiner Angaben zur Bearbeitung dieser Terminanfrage einverstanden.",
			submit:         "Terminanfrage senden",
			sending:        "Wird gesendet …",
			err_required:   "Bitte ausfüllen.",
			err_email:      "Bitte eine gültige E-Mail-Adresse angeben.",
			err_topic:      "Bitte ein Thema wählen.",
			err_format:     "Bitte ein Format wählen.",
			err_slot:       "Bitte Datum und Uhrzeit wählen.",
			err_consent:    "Ohne Ihre Einwilligung können wir die Anfrage nicht bearbeiten.",
			err_network:    "Die Anfrage konnte nicht gesendet werden. Bitte versuchen Sie es später erneut oder schreiben Sie mir direkt per E-Mail.",
			err_taken:      "Dieser Termin wurde soeben anderweitig angefragt. Bitte wählen Sie eine andere Zeit.",
			dow:            ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
			months:         ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"],
			prev_month:     "Vorheriger Monat",
			next_month:     "Nächster Monat",
			privacy_h:      "Hinweise zum Datenschutz",
			privacy_p1:     "Zur Bearbeitung Ihrer Terminanfrage werden Name, E-Mail-Adresse, das gewählte Thema, Datum und Uhrzeit sowie – falls angegeben – Ihre Nachricht und angehängte Dokumente gespeichert (Art. 6 Abs. 1 lit. b DSGVO). Die Verarbeitung erfolgt ausschließlich auf Systemen des Leibniz-Rechenzentrums (LRZ) im Münchner Wissenschaftsnetz; eine Weitergabe an Dritte findet nicht statt. Die Daten dienen allein der Vereinbarung und Durchführung des Termins.",
			privacy_p2:     "Die Daten werden 30 Tage nach dem Termin – bzw. nach Ablehnung oder Verfall der Anfrage – automatisch gelöscht. Sie können jederzeit Auskunft oder Löschung verlangen; schreiben Sie dazu bitte an ryan.sandell@lrz.uni-muenchen.de.",
			privacy_p3:     "Bitte geben Sie in der Nachricht und in Anhängen keine Gesundheitsdaten oder andere besonders schutzwürdigen Angaben an; solche Anliegen besprechen wir besser im Gespräch."
		},
		en: {
			title:          "Book an appointment",
			intro:          "Choose a topic, a format, and a date and time. I'll confirm your request by email once I've reviewed it.",
			demo:           "Preview mode: this page is not yet connected to the booking system. Requests are not sent.",
			step_topic:     "Topic",
			step_format:    "Format",
			step_when:      "Date and time",
			step_details:   "Your details",
			step_confirm:   "Review and send",
			topic_label:    "What is it about?",
			topic_choose:   "Please choose …",
			format_label:   "How would you like to meet?",
			pick_day:       "Choose a day first; available days are highlighted.",
			pick_time:      "Available times on",
			no_slots:       "No appointments are left on this day.",
			pick_topic_first: "Please choose a topic first so the matching times can be shown.",
			tz:             "All times are Central European Time (Europe/Berlin).",
			minutes:        "min",
			name:           "Name",
			email:          "Email address",
			email_hint:     "We'll send the confirmation to this address.",
			message:        "Message",
			message_hint:   "What exactly is it about? Anything I should know in advance?",
			files:          "Attach documents",
			files_hint:     "PDF only, at most 50 MB per file, up to 3 files.",
			optional:       "(optional)",
			file_too_big:   "too large (max. 50 MB)",
			file_not_pdf:   "not a PDF file",
			file_too_many:  "At most 3 files.",
			summary_title:  "Your request",
			summary_empty:  "Nothing selected yet.",
			s_topic:        "Topic",
			s_format:       "Format",
			s_when:         "Appointment",
			s_length:       "Length",
			consent:        "I have read the privacy notice and consent to the processing of my details for the purpose of handling this appointment request.",
			submit:         "Send appointment request",
			sending:        "Sending …",
			err_required:   "Please fill this in.",
			err_email:      "Please enter a valid email address.",
			err_topic:      "Please choose a topic.",
			err_format:     "Please choose a format.",
			err_slot:       "Please choose a date and time.",
			err_consent:    "We can't process the request without your consent.",
			err_network:    "The request could not be sent. Please try again later, or email me directly.",
			err_taken:      "That slot was just requested by someone else. Please choose another time.",
			dow:            ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
			months:         ["January","February","March","April","May","June","July","August","September","October","November","December"],
			prev_month:     "Previous month",
			next_month:     "Next month",
			privacy_h:      "Privacy notice",
			privacy_p1:     "To handle your appointment request we store your name, email address, the chosen topic, date and time, and — if provided — your message and attached documents (Art. 6(1)(b) GDPR). Processing takes place solely on systems of the Leibniz Supercomputing Centre (LRZ) within the Munich Scientific Network; nothing is passed to third parties. The data is used only to arrange and hold the appointment.",
			privacy_p2:     "The data is deleted automatically 30 days after the appointment, or after the request is declined or lapses. You may request access or deletion at any time by writing to ryan.sandell@lrz.uni-muenchen.de.",
			privacy_p3:     "Please do not include health information or other especially sensitive details in your message or attachments; such matters are better discussed in person."
		}
	};

	/* ======================================================================
	   SET-UP
	   ====================================================================== */

	var form = document.getElementById("booking");
	if (!form) { return; }

	var API      = (form.dataset.api || "").replace(/\/$/, "");
	var DEMO     = !API;
	var TZ       = "Europe/Berlin";
	var MAX_FILES = 3;
	var MAX_BYTES = 50 * 1024 * 1024;

	var $ = function (sel, root) { return (root || document).querySelector(sel); };
	var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

	var lang = pickLanguage();
	var t = function (key) { return I18N[lang][key]; };

	var availability = null;      // contents of availability.json
	var taken = [];               // [{start:"YYYY-MM-DDTHH:MM", minutes:N}] from the backend
	var state = { topic: null, format: null, date: null, time: null, files: [] };
	var viewMonth = null;         // {y, m} of the month the calendar shows

	/* ---- Language ------------------------------------------------------- */

	function pickLanguage() {
		var q = new URLSearchParams(location.search).get("lang");
		if (q === "en" || q === "de") { return q; }
		try { var s = localStorage.getItem("lang"); if (s === "en" || s === "de") { return s; } } catch (e) {}
		return "de";                                      // German by default
	}

	function applyLanguage() {
		document.documentElement.lang = lang;
		$$("[data-i18n]").forEach(function (el) {
			var key = el.getAttribute("data-i18n");
			if (I18N[lang][key] !== undefined) { el.textContent = I18N[lang][key]; }
		});
		$$("[data-i18n-placeholder]").forEach(function (el) {
			el.placeholder = I18N[lang][el.getAttribute("data-i18n-placeholder")] || "";
		});
		$$(".lang-toggle button").forEach(function (b) {
			b.setAttribute("aria-pressed", b.dataset.lang === lang ? "true" : "false");
		});
		document.title = t("title") + " | Ryan Sandell";
		if (availability) { renderTopics(); renderFormats(); renderCalendar(); renderSlots(); renderSummary(); }
	}

	$$(".lang-toggle button").forEach(function (b) {
		b.addEventListener("click", function () {
			lang = b.dataset.lang;
			try { localStorage.setItem("lang", lang); } catch (e) {}
			applyLanguage();
		});
	});

	/* ======================================================================
	   TIME  —  everything is done in Europe/Berlin wall-clock time
	   ====================================================================== */

	var fmtParts = new Intl.DateTimeFormat("en-US", {
		timeZone: TZ, hour12: false,
		year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", weekday: "short"
	});

	/* Berlin wall-clock parts for an instant. */
	function berlin(epochMs) {
		var p = {};
		fmtParts.formatToParts(new Date(epochMs)).forEach(function (x) { p[x.type] = x.value; });
		return { y: +p.year, m: +p.month, d: +p.day, hh: (+p.hour) % 24, mm: +p.minute,
		         dow: ["sun","mon","tue","wed","thu","fri","sat"].indexOf(p.weekday.toLowerCase().slice(0, 3)) };
	}

	function pad(n) { return (n < 10 ? "0" : "") + n; }
	function dateKey(y, m, d) { return y + "-" + pad(m) + "-" + pad(d); }
	function slotKey(y, m, d, hh, mm) { return dateKey(y, m, d) + "T" + pad(hh) + ":" + pad(mm); }

	/* Berlin's UTC offset (minutes) at a given instant. */
	function berlinOffset(epochMs) {
		var b = berlin(epochMs);
		return (Date.UTC(b.y, b.m - 1, b.d, b.hh, b.mm) - epochMs) / 60000;
	}

	/* Berlin wall-clock -> epoch ms, correct across DST changes. */
	function berlinToEpoch(y, m, d, hh, mm) {
		var guess = Date.UTC(y, m - 1, d, hh, mm);
		var off = berlinOffset(guess);
		var epoch = guess - off * 60000;
		var off2 = berlinOffset(epoch);
		return off2 === off ? epoch : guess - off2 * 60000;
	}

	function parseSlot(key) {                         // "YYYY-MM-DDTHH:MM" -> parts
		return { y: +key.slice(0, 4), m: +key.slice(5, 7), d: +key.slice(8, 10), hh: +key.slice(11, 13), mm: +key.slice(14, 16) };
	}
	function slotEpoch(key) { var p = parseSlot(key); return berlinToEpoch(p.y, p.m, p.d, p.hh, p.mm); }

	function addDays(y, m, d, n) {                    // pure calendar arithmetic, no time zone involved
		var x = new Date(Date.UTC(y, m - 1, d + n));
		return { y: x.getUTCFullYear(), m: x.getUTCMonth() + 1, d: x.getUTCDate() };
	}

	/* ======================================================================
	   AVAILABILITY  —  which slots can be requested?
	   ====================================================================== */

	var DOW_KEYS = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];

	/* The [start,end] windows offered on a given date. */
	function windowsFor(y, m, d) {
		var key = dateKey(y, m, d);
		if ((availability.blocked || []).indexOf(key) !== -1) { return []; }
		var dow = new Date(Date.UTC(y, m - 1, d)).getUTCDay();
		var w = (availability.weekly || {})[DOW_KEYS[dow]] || [];
		var x = (availability.extra || {})[key] || [];
		return w.concat(x);
	}

	function overlaps(startA, minsA, startB, minsB) {
		var a0 = slotEpoch(startA), a1 = a0 + minsA * 60000;
		var b0 = slotEpoch(startB), b1 = b0 + minsB * 60000;
		return a0 < b1 && b0 < a1;
	}

	/* All bookable start times on a date for the chosen topic length. */
	function slotsFor(y, m, d, minutes) {
		var now = Date.now();
		var earliest = now + (availability.leadHours || 0) * 3600000;
		var out = [];
		windowsFor(y, m, d).forEach(function (win) {
			var s = win[0].split(":"), e = win[1].split(":");
			var cur = (+s[0]) * 60 + (+s[1]), end = (+e[0]) * 60 + (+e[1]);
			while (cur + minutes <= end) {
				var key = slotKey(y, m, d, Math.floor(cur / 60), cur % 60);
				var free = slotEpoch(key) >= earliest && !taken.some(function (b) { return overlaps(key, minutes, b.start, b.minutes); });
				if (free) { out.push(key); }
				cur += minutes;
			}
		});
		return out;
	}

	function bookingRange() {                        // [first, last] bookable dates (Berlin)
		var now = berlin(Date.now());
		var first = addDays(now.y, now.m, now.d, 0);
		var last = addDays(now.y, now.m, now.d, availability.horizonDays || 28);
		return { first: first, last: last };
	}

	function inRange(y, m, d) {
		var r = bookingRange(), k = dateKey(y, m, d);
		return k >= dateKey(r.first.y, r.first.m, r.first.d) && k <= dateKey(r.last.y, r.last.m, r.last.d);
	}

	/* ======================================================================
	   RENDERING
	   ====================================================================== */

	function currentTopic() {
		return (availability.topics || []).filter(function (x) { return x.id === state.topic; })[0] || null;
	}

	function renderTopics() {
		var sel = $("#topic");
		var keep = sel.value;
		sel.innerHTML = "";
		var o = document.createElement("option");
		o.value = ""; o.textContent = t("topic_choose"); sel.appendChild(o);
		(availability.topics || []).forEach(function (tp) {
			var op = document.createElement("option");
			op.value = tp.id;
			op.textContent = tp[lang] + " (" + tp.minutes + " " + t("minutes") + ")";
			sel.appendChild(op);
		});
		sel.value = keep;
	}

	function renderFormats() {
		var list = $("#formats");
		list.innerHTML = "";
		(availability.formats || []).forEach(function (f) {
			var li = document.createElement("li");
			var lab = document.createElement("label"); lab.className = "choice";
			var inp = document.createElement("input");
			inp.type = "radio"; inp.name = "format"; inp.value = f.id; inp.checked = state.format === f.id;
			inp.addEventListener("change", function () { state.format = f.id; setInvalid("format", false); renderSummary(); });
			var span = document.createElement("span"); span.className = "choice__text"; span.textContent = f[lang];
			lab.appendChild(inp); lab.appendChild(span); li.appendChild(lab); list.appendChild(li);
		});
	}

	function renderCalendar() {
		var tp = currentTopic();
		var r = bookingRange();
		if (!viewMonth) { viewMonth = { y: r.first.y, m: r.first.m }; }

		$("#cal-month").textContent = t("months")[viewMonth.m - 1] + " " + viewMonth.y;
		var prevOk = dateKey(viewMonth.y, viewMonth.m, 1) > dateKey(r.first.y, r.first.m, 1);
		var nextOk = dateKey(viewMonth.y, viewMonth.m, 1) < dateKey(r.last.y, r.last.m, 1);
		$("#cal-prev").disabled = !prevOk; $("#cal-next").disabled = !nextOk;
		$("#cal-prev").setAttribute("aria-label", t("prev_month"));
		$("#cal-next").setAttribute("aria-label", t("next_month"));

		var grid = $("#cal-grid");
		grid.innerHTML = "";
		t("dow").forEach(function (d) {
			var el = document.createElement("div"); el.className = "calendar__dow"; el.textContent = d; grid.appendChild(el);
		});

		var firstDow = (new Date(Date.UTC(viewMonth.y, viewMonth.m - 1, 1)).getUTCDay() + 6) % 7;   // Monday = 0
		var daysInMonth = new Date(Date.UTC(viewMonth.y, viewMonth.m, 0)).getUTCDate();
		var today = berlin(Date.now());

		for (var i = 0; i < firstDow; i++) {
			var pad_ = document.createElement("div"); pad_.className = "calendar__day calendar__day--empty"; grid.appendChild(pad_);
		}
		for (var d = 1; d <= daysInMonth; d++) {
			(function (day) {
				var btn = document.createElement("button");
				btn.type = "button"; btn.className = "calendar__day"; btn.textContent = day;
				var key = dateKey(viewMonth.y, viewMonth.m, day);
				var avail = tp && inRange(viewMonth.y, viewMonth.m, day) && slotsFor(viewMonth.y, viewMonth.m, day, tp.minutes).length > 0;
				btn.dataset.available = avail ? "true" : "false";
				btn.disabled = !avail;
				if (today.y === viewMonth.y && today.m === viewMonth.m && today.d === day) { btn.dataset.today = "true"; }
				btn.setAttribute("aria-pressed", state.date === key ? "true" : "false");
				btn.setAttribute("aria-label", key);
				btn.addEventListener("click", function () {
					state.date = key; state.time = null; setInvalid("slot", false);
					renderCalendar(); renderSlots(); renderSummary();
				});
				grid.appendChild(btn);
			})(d);
		}

		$("#cal-hint").textContent = tp ? t("pick_day") : t("pick_topic_first");
	}

	function renderSlots() {
		var box = $("#slots"), head = $("#slots-head");
		box.innerHTML = "";
		var tp = currentTopic();
		if (!tp || !state.date) { head.hidden = true; return; }
		var p = parseSlot(state.date + "T00:00");
		var list = slotsFor(p.y, p.m, p.d, tp.minutes);
		head.hidden = false;
		head.textContent = t("pick_time") + " " + formatDate(state.date) + ":";
		if (!list.length) {
			var e = document.createElement("p"); e.className = "slots__empty"; e.textContent = t("no_slots"); box.appendChild(e); return;
		}
		list.forEach(function (key) {
			var b = document.createElement("button");
			b.type = "button"; b.className = "slot"; b.textContent = key.slice(11, 16);
			b.setAttribute("aria-pressed", state.time === key ? "true" : "false");
			b.addEventListener("click", function () {
				state.time = key; setInvalid("slot", false);
				$$(".slot", box).forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
				b.setAttribute("aria-pressed", "true");
				renderSummary();
			});
			box.appendChild(b);
		});
	}

	function formatDate(key) {                       // "2026-10-06" -> "Dienstag, 6. Oktober 2026" / "Tuesday, 6 October 2026"
		var p = parseSlot(key + "T00:00");
		var dt = new Date(Date.UTC(p.y, p.m - 1, p.d));
		return new Intl.DateTimeFormat(lang === "de" ? "de-DE" : "en-GB", { timeZone: "UTC", weekday: "long", day: "numeric", month: "long", year: "numeric" }).format(dt);
	}

	function renderSummary() {
		var tp = currentTopic();
		var fmt = (availability.formats || []).filter(function (f) { return f.id === state.format; })[0];
		var box = $("#summary");
		if (!tp && !fmt && !state.time) {
			box.innerHTML = '<p class="summary__empty">' + t("summary_empty") + "</p>"; return;
		}
		var rows = [];
		if (tp) { rows.push([t("s_topic"), tp[lang]]); rows.push([t("s_length"), tp.minutes + " " + t("minutes")]); }
		if (fmt) { rows.push([t("s_format"), fmt[lang]]); }
		if (state.time) { rows.push([t("s_when"), formatDate(state.time.slice(0, 10)) + ", " + state.time.slice(11, 16)]); }
		var dl = document.createElement("dl");
		rows.forEach(function (r) {
			var dt = document.createElement("dt"); dt.textContent = r[0];
			var dd = document.createElement("dd"); dd.textContent = r[1];
			dl.appendChild(dt); dl.appendChild(dd);
		});
		box.innerHTML = ""; box.appendChild(dl);
	}

	/* ---- Files ------------------------------------------------------------ */

	function renderFiles() {
		var ul = $("#file-list"); ul.innerHTML = "";
		state.files.forEach(function (f) {
			var li = document.createElement("li");
			var name = document.createElement("span"); name.textContent = f.file.name;
			var meta = document.createElement("span");
			meta.textContent = f.problem ? f.problem : (f.file.size / 1048576).toFixed(1) + " MB";
			if (f.problem) { meta.className = "bad"; }
			li.appendChild(name); li.appendChild(meta); ul.appendChild(li);
		});
	}

	$("#files").addEventListener("change", function (e) {
		var picked = Array.prototype.slice.call(e.target.files);
		var problem = null;
		if (picked.length > MAX_FILES) { problem = t("file_too_many"); }
		state.files = picked.slice(0, MAX_FILES).map(function (file) {
			var bad = null;
			var isPdf = file.type === "application/pdf" || /\.pdf$/i.test(file.name);
			if (!isPdf) { bad = t("file_not_pdf"); }
			else if (file.size > MAX_BYTES) { bad = t("file_too_big"); }
			return { file: file, problem: bad };
		});
		setInvalid("files", !!problem || state.files.some(function (f) { return f.problem; }), problem || "");
		renderFiles();
	});

	/* ======================================================================
	   VALIDATION + SUBMIT
	   ====================================================================== */

	function setInvalid(field, bad, msg) {
		var wrap = $('[data-field="' + field + '"]');
		if (!wrap) { return; }
		wrap.dataset.invalid = bad ? "true" : "false";
		var err = $(".error", wrap);
		if (err && msg !== undefined) { err.textContent = msg; }
	}

	function validate() {
		var ok = true;
		var tp = currentTopic();
		if (!tp) { setInvalid("topic", true, t("err_topic")); ok = false; }
		if (!state.format) { setInvalid("format", true, t("err_format")); ok = false; }
		if (!state.time) { setInvalid("slot", true, t("err_slot")); ok = false; }
		var name = $("#name").value.trim();
		if (!name) { setInvalid("name", true, t("err_required")); ok = false; }
		var email = $("#email").value.trim();
		if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { setInvalid("email", true, t("err_email")); ok = false; }
		if (state.files.some(function (f) { return f.problem; })) { ok = false; }
		if (!$("#consent").checked) { setInvalid("consent", true, t("err_consent")); ok = false; }
		return ok;
	}

	["name", "email"].forEach(function (id) {
		$("#" + id).addEventListener("input", function () { setInvalid(id, false); });
	});
	$("#consent").addEventListener("change", function () { setInvalid("consent", false); });

	$("#topic").addEventListener("change", function () {
		state.topic = $("#topic").value || null; state.date = null; state.time = null;
		setInvalid("topic", false);
		renderCalendar(); renderSlots(); renderSummary();
	});

	$("#cal-prev").addEventListener("click", function () {
		viewMonth = viewMonth.m === 1 ? { y: viewMonth.y - 1, m: 12 } : { y: viewMonth.y, m: viewMonth.m - 1 }; renderCalendar();
	});
	$("#cal-next").addEventListener("click", function () {
		viewMonth = viewMonth.m === 12 ? { y: viewMonth.y + 1, m: 1 } : { y: viewMonth.y, m: viewMonth.m + 1 }; renderCalendar();
	});

	form.addEventListener("submit", function (e) {
		e.preventDefault();
		if (!validate()) {
			var firstBad = $('[data-invalid="true"]');
			if (firstBad) { firstBad.scrollIntoView({ behavior: "smooth", block: "center" }); }
			return;
		}
		var btn = $("#submit"), status = $("#submit-status");
		btn.disabled = true; btn.textContent = t("sending"); status.textContent = "";

		var tp = currentTopic();
		var fd = new FormData();
		fd.append("lang", lang);
		fd.append("topic", tp.id);
		fd.append("format", state.format);
		fd.append("start", state.time);                        // Berlin wall-clock, e.g. 2026-10-06T10:00
		fd.append("minutes", tp.minutes);
		fd.append("name", $("#name").value.trim());
		fd.append("email", $("#email").value.trim());
		fd.append("message", $("#message").value.trim());
		state.files.forEach(function (f) { fd.append("files", f.file, f.file.name); });
		fd.append("website", $("#website").value);              // honeypot: humans leave it empty

		var done = function () { location.href = "submitted/index.html?lang=" + lang; };

		if (DEMO) { setTimeout(done, 600); return; }

		fetch(API + "/request", { method: "POST", body: fd })
			.then(function (r) { return r.json().then(function (j) { return { ok: r.ok, status: r.status, body: j }; }); })
			.then(function (res) {
				if (res.ok) { done(); return; }
				var msg = res.status === 409 ? t("err_taken") : t("err_network");
				throw new Error(msg);
			})
			.catch(function (err) {
				status.textContent = err.message || t("err_network");
				btn.disabled = false; btn.textContent = t("submit");
				if (err.message === t("err_taken")) { loadTaken().then(function () { renderCalendar(); renderSlots(); }); }
			});
	});

	/* ======================================================================
	   DATA
	   ====================================================================== */

	function loadTaken() {
		if (DEMO) {
			/* Pretend bookings so the preview shows the effect of a taken slot:
			   the first slot on the 2nd and 3rd days that actually have hours. */
			var r = bookingRange(), found = 0;
			taken = [];
			for (var i = 1; i <= (availability.horizonDays || 28) && found < 3; i++) {
				var x = addDays(r.first.y, r.first.m, r.first.d, i);
				var w = windowsFor(x.y, x.m, x.d);
				if (!w.length) { continue; }
				found++;
				if (found >= 2) { taken.push({ start: dateKey(x.y, x.m, x.d) + "T" + w[0][0], minutes: 30 }); }
			}
			return Promise.resolve();
		}
		return fetch(API + "/taken").then(function (r) { return r.json(); }).then(function (j) { taken = j.taken || []; }).catch(function () { taken = []; });
	}

	fetch("availability.json", { cache: "no-store" })
		.then(function (r) { return r.json(); })
		.then(function (j) { availability = j; return loadTaken(); })
		.then(function () {
			$("#demo-banner").hidden = !DEMO;
			applyLanguage();
			form.hidden = false;
		})
		.catch(function () {
			$("#load-error").hidden = false;
		});
})();
