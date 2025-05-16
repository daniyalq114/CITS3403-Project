document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('.shared-user-form');
  const input = document.getElementById('shared-user-input');
  const datalist = document.getElementById('shared-usernames');

  if (!form || !input || !datalist || typeof sharedUsernames === 'undefined') return;

  // Debounce function
  function debounce(func, delay) {
    let timer;
    return function () {
      clearTimeout(timer);
      timer = setTimeout(func, delay);
    };
  }

  // Populate datalist with filtered usernames
  const updateSuggestions = debounce(() => {
    const query = input.value.toLowerCase();
    datalist.innerHTML = '';

    if (query.length >= 1) {
      const matches = sharedUsernames
        .filter(name => name.toLowerCase().includes(query))
        .slice(0, 10);

      // Restore list if removed
      input.setAttribute('list', 'shared-usernames');

      // If input exactly matches the only remaining user, hide suggestions
      if (matches.length === 1 && matches[0].toLowerCase() === query) {
        input.removeAttribute('list');
        return;
      }

      for (const name of matches) {
        const option = document.createElement('option');
        option.value = name;
        datalist.appendChild(option);
      }
    } else {
      input.removeAttribute('list');
    }
  }, 150);

  input.addEventListener('input', updateSuggestions);

  // Handle form submission via AJAX
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const username = input.value;

    try {
      const res = await fetch('/set_shared_user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username })
      });

      const data = await res.json();
      if (data.success) {
        location.reload(); // Refresh page to show new user's data
      } else {
        showFlashMessage(data.message, 'error');
      }
    } catch (err) {
      showFlashMessage('An error occurred while switching users.', 'error');
    }
  });

  // Optional helper to show messages (reuse Flask-style flash output if desired)
  function showFlashMessage(message, category) {
    const ul = document.querySelector('.flashes') || createFlashList();
    const li = document.createElement('li');
    li.className = `flash ${category}`;
    li.innerText = message;
    ul.appendChild(li);
  }

  function createFlashList() {
    const main = document.querySelector('main');
    const ul = document.createElement('ul');
    ul.className = 'flashes';
    main.prepend(ul);
    return ul;
  }
});
