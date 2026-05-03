(function () {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('sw.js').catch((err) => {
        console.warn('SW registration failed:', err);
      });
    });
  }

  const form = document.getElementById('log-form');
  const dateInput = document.getElementById('date');
  const btn = document.getElementById('submit-btn');
  const status = document.getElementById('status');

  // Default the date field to today, in the user's local timezone.
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const dd = String(today.getDate()).padStart(2, '0');
  dateInput.value = `${yyyy}-${mm}-${dd}`;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    status.className = '';
    status.textContent = '';

    if (!window.APPS_SCRIPT_URL || window.APPS_SCRIPT_URL.includes('PASTE')) {
      status.className = 'err';
      status.textContent = 'Set APPS_SCRIPT_URL in config.js first.';
      return;
    }

    const fd = new FormData(form);
    const payload = {
      date: fd.get('date'),
      carbs: fd.get('carbs'),
      exercise: fd.getAll('exercise'),
      sleep: fd.get('sleep') === 'on',
      alcohol: fd.get('alcohol') === 'on',
    };

    btn.disabled = true;
    status.textContent = 'Saving…';

    try {
      // text/plain body avoids a CORS preflight against Apps Script.
      const res = await fetch(window.APPS_SCRIPT_URL, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      const result = await res.json();
      if (result.ok) {
        status.className = 'ok';
        status.textContent = result.action === 'updated'
          ? 'Updated existing entry for this day.'
          : 'Saved to calendar.';
      } else {
        status.className = 'err';
        status.textContent = 'Error: ' + (result.error || 'unknown');
      }
    } catch (err) {
      status.className = 'err';
      status.textContent = 'Network error: ' + err.message;
    } finally {
      btn.disabled = false;
    }
  });
})();
