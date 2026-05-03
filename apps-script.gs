// Daily Log Tracker — Google Apps Script backend.
// Paste this whole file into a new Apps Script project at https://script.google.com,
// then Deploy → New deployment → Web app, "Execute as: Me", "Who has access: Anyone".
// Copy the resulting Web App URL into config.js on the front-end.

function doGet(e) {
  const action = (e && e.parameter && e.parameter.action) || '';
  if (action === 'list') {
    return jsonResponse({ ok: true, events: listDailyLogs() });
  }
  return ContentService
    .createTextOutput('Daily Log Tracker endpoint is live. POST JSON to log a day, or GET ?action=list to read.')
    .setMimeType(ContentService.MimeType.TEXT);
}

function listDailyLogs() {
  // Pull every "Daily log" all-day event from the user's default calendar
  // over a wide window. Adjust the window if you ever want a longer history.
  const cal = CalendarApp.getDefaultCalendar();
  const start = new Date();
  start.setFullYear(start.getFullYear() - 2);
  const end = new Date();
  end.setDate(end.getDate() + 1);

  const events = cal.getEvents(start, end)
    .filter(ev => ev.getTitle().startsWith('Daily log'));

  return events.map(ev => {
    const date = ev.getAllDayStartDate();
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    return {
      date: yyyy + '-' + mm + '-' + dd,
      title: ev.getTitle(),
      description: ev.getDescription() || '',
      eventId: ev.getId()
    };
  });
}

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const result = logDay(data);
    return jsonResponse({ ok: true, action: result.action, eventId: result.eventId });
  } catch (err) {
    return jsonResponse({ ok: false, error: String(err) });
  }
}

function logDay(data) {
  // data shape: { date: "YYYY-MM-DD", carbs: "high"|"medium"|"low",
  //               exercise: ["Animal Moves","Cardio","Resistance"], sleep: true|false }
  const [y, m, d] = data.date.split('-').map(Number);
  const day = new Date(y, m - 1, d);

  const title = formatTitle(data);
  const description = formatDescription(data);

  const cal = CalendarApp.getDefaultCalendar();
  const existing = cal.getEventsForDay(day)
    .filter(ev => ev.getTitle().startsWith('Daily log'));

  if (existing.length > 0) {
    // Update the first matching event so re-submitting the same day overwrites.
    const ev = existing[0];
    ev.setTitle(title);
    ev.setDescription(description);
    return { action: 'updated', eventId: ev.getId() };
  } else {
    const ev = cal.createAllDayEvent(title, day, { description: description });
    return { action: 'created', eventId: ev.getId() };
  }
}

function formatTitle(data) {
  const parts = [];
  parts.push('carbs:' + data.carbs);
  if (data.exercise && data.exercise.length) parts.push('ex:' + data.exercise.join('+'));
  if (data.sleep) parts.push('sleep:Y'); else parts.push('sleep:N');
  return 'Daily log — ' + parts.join(' | ');
}

function formatDescription(data) {
  const lines = [
    'Carbs: ' + data.carbs,
    'Exercise: ' + ((data.exercise && data.exercise.length) ? data.exercise.join(', ') : 'none'),
    'Sleep 7.5h uninterrupted: ' + (data.sleep ? 'Y' : 'N'),
    '',
    'Logged at: ' + new Date().toISOString()
  ];
  return lines.join('\n');
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
