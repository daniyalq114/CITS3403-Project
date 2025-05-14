document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('.network-form');
  const input = document.getElementById('search-user-input');
  const datalist = document.getElementById('usernames');

  if (input && datalist) {
    input.addEventListener('input', function () {
      const query = input.value.toLowerCase();
      datalist.innerHTML = '';

      if (query.length >= 1) {
        const matches = allUsernames
          .filter(username =>
            username.toLowerCase().includes(query) &&
            !alreadyShared.includes(username)
          )
          .slice(0, 10); // Only show 10 matches

        // Hide if only exact match remains
        if (matches.length === 1 && matches[0].toLowerCase() === query) {
          input.removeAttribute('list');
          return;
        }

        input.setAttribute('list', 'usernames');

        for (const name of matches) {
          const option = document.createElement('option');
          option.value = name;
          datalist.appendChild(option);
        }
      } else {
        input.removeAttribute('list');
      }
    });
  }

  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    const username = input.value;
    const csrfToken = form.querySelector('input[name="csrf_token"]').value;

    try {
      const res = await fetch('/network', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ username })
      });

      const data = await res.json();
      const flashContainer = document.querySelector('.flashes');
      if (flashContainer) {
        flashContainer.innerHTML = '';
        const li = document.createElement('li');
        li.className = `flash ${data.success ? 'success' : 'error'}`;
        li.textContent = data.message;
        flashContainer.appendChild(li);
      }

      if (data.success) {
        alreadyShared.push(username); // Exclude newly shared user
      }
    } catch (err) {
      alert('An error occurred while sharing.');
    }

    input.value = '';
    input.removeAttribute('list');
  });
});
