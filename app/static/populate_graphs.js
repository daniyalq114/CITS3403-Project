google.charts.load('current', {'packages':['corechart']});
function nrand() {
    return Math.floor(Math.random() * 5);
}
// random data in the format I assume we'll receive
/*
pokemon = [
    {"name":"Reshiram", "moves":[["Giga Impact",], ["Light Screen",], ["Protect",], ["Reflect",]]},
    {"name":"Darkrai", "moves":[["Dark Pulse",], ["Hyper Beam",], ["Throat Chop",], ["Thunder Wave",]]}, 
    {"name":"Glalie", "moves":[["Avalanche",], ["Blizzard",], ["Body Slam",], ["Chilling Water",]]}, 
    {"name":"Deoxys", "moves":[["Agility",], ["Brick Break",], ["Calm Mind",], ["Dark Pulse",]]},
    {"name":"Regigigas", "moves":[["Giga Impact",], ["Hyper Beam",], ["Crush Grip",], ["Thunder",]]},
    {"name":"Rayquaza", "moves":[["Giga Impact",], ["Draco Meteor",], ["Dragon Ascent",], ["Meteor Beam",]]}
] // populate team
pokemon.forEach(mon => {
    mon["moves"].forEach(move_arr =>
        move_arr[1] = nrand()
    )
})*/

if(document.URL.includes("visualise")) {
    google.charts.setOnLoadCallback(drawFunction);
}

function drawFunction() {
    const moveData = JSON.parse(document.getElementById("move-data").textContent);
    const container = document.querySelector(".part3-container");

    for (const [pokemon, moves] of Object.entries(moveData)) {
        const graphDiv = document.createElement("div");
        graphDiv.className = "part3 placeholder-table";
        container.appendChild(graphDiv);

        const moveArray = [["Move", "Usage"]];
        for (const [move, count] of Object.entries(moves)) {
            moveArray.push([move, count]);
        }

        const data = google.visualization.arrayToDataTable(moveArray);
        const options = {
            title: pokemon,
            is3D: true,
            colors: ["#90caf9", "#ff6b6b", "#ffcc80", "#a5d6a7"],
        };

        const chart = new google.visualization.PieChart(graphDiv);
        chart.draw(data, options);
    }
}