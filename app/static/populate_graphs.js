google.charts.load('current', {'packages':['corechart']});
function nrand() {
    return Math.floor(Math.random() * 5);
}

if(document.URL.includes("visualise")) {
    google.charts.setOnLoadCallback(drawPartThree);
}


document.addEventListener("DOMContentLoaded", function() {
  const default_activeScript = document.getElementById("default-active-match");
  let default_active = null;
  if (default_activeScript) {
    try {
      default_active = JSON.parse(default_activeScript.textContent);
      console.log("active match:", default_active);

      // Add "active" class to the tr whose data-match-id == default_active
      document.querySelectorAll('.replay-record tbody tr').forEach(row => {
        if (row.getAttribute('data-match-id') == default_active) {
          row.classList.add('active');
        }
      });
      fetch(`/visualise/match_data/${default_active}`)
          .then(response => response.json())
          .then(data => {
            // Call your graph population function with the new data
            // drawPartThree(data);
            console.log("data:", data)
            drawPartTwo(data)
            drawPartThree(data)
          });
    } catch (e) {
      console.error("Failed to parse pokemon data JSON:", e);
    }
  }
  document.querySelectorAll(".replay-record tbody tr").forEach(row => {
    row.addEventListener("click", function() {
      // Remove 'active' class from all rows
      document.querySelectorAll(".replay-record tbody tr").forEach(r => r.classList.remove("active"));
      // Add 'active' class to the clicked row
      this.classList.add("active");

      // Get the match id from the data attribute
      const matchId = this.getAttribute("data-match-id");
      if (matchId) {
        // AJAX GET request to the server
        fetch(`/visualise/match_data/${matchId}`)
          .then(response => response.json())
          .then(data => {
            // Call your graph population function with the new data
            // drawPartThree(data);
            drawPartTwo(data); 
            drawPartThree(data);
          });
      }
    });
  });
});

function drawPartTwo(poke_dict) {
    let part2_body = document.querySelectorAll(".part2-container .part2 > tbody");
    // Row follows format <td><img></td> <td>pokemon defeated to losses</td> <td>games won</td>
    var part2_table_contents = "";
    for (const pokemonName in poke_dict) {
        if (poke_dict.hasOwnProperty(pokemonName)) {
            const pokeData = poke_dict[pokemonName];
            // Example: add a row for each pokemon
            part2_table_contents += `<tr>
                <td>${pokemonName}</td>
                <td>${pokeData.wins}</td>
                <td>${pokeData.losses}</td>`
            var per_str = ""
            if (pokeData.wins > 0 && pokeData.losses == 0)
                part2_table_contents += `<td>${pokeData.wins}</td>`
            else if (pokeData.wins == 0 && pokeData.losses == 0)
                part2_table_contents += `<td>N/A</td>`
            else
                part2_table_contents += `<td>${pokeData.wins/pokeData.losses}</td>`
            part2_table_contents += `<td>${pokeData.matches_won}</td>
            </tr>`;
        }
    }
    // Set the table body HTML
    part2_body.forEach(tb => tb.innerHTML = part2_table_contents);
}

// Modify drawPartThree to accept data as an argument
function drawPartThree(poke_dict) {
    const container = document.querySelector(".part3-container");
    container.innerHTML = ""; // Clear previous graphs

    for (const pokemon in poke_dict) {
        const moveArray = [["Move", "Usage"]];
        const moves = poke_dict[pokemon].moves;
        for (const move in moves) {
            moveArray.push([move, moves[move]]);
        }

        // Only draw chart if there are moves
        if (moveArray.length > 1) {
            const data = google.visualization.arrayToDataTable(moveArray);
            const options = {
                title: pokemon,
                is3D: true,
                colors: ["#90caf9", "#ff6b6b", "#ffcc80", "#a5d6a7"],
            };
            const graphDiv = document.createElement("div");
            graphDiv.className = "part3 placeholder-table";
            container.appendChild(graphDiv);

            const chart = new google.visualization.PieChart(graphDiv);
            chart.draw(data, options);
        } 
    }
}