google.charts.load('current', {'packages':['corechart']});
function nrand() {
    return Math.floor(Math.random() * 5);
}
// random data in the format I assume we'll receive
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
});
function constructGraph(moveinfo, graph) {
    const data=google.visualization.arrayToDataTable(moveinfo);
    const colours=['rgb(159, 161, 159)', 'rgb(238, 135, 50)', 'rgb(141, 184, 234)', 'rgb(135, 69, 196)'];
    const options ={is3D:true, colors:colours};
    let chart=new google.visualization.PieChart(graph);
    chart.draw(data, options);
}

// im so sorry for this code

const xhr = new XMLHttpRequest();
if(document.URL.includes("visualise")) {
    google.charts.setOnLoadCallback(drawFunction);
}


var count = 0;
function drawFunction() {
    var poke_state;
    var part1 = document.querySelectorAll(".content > .replay-record > .part1");
    var graphs = document.querySelectorAll(".content > .part3-container > .part3");

    xhr.addEventListener('load', () => {
        poke_state = JSON.parse(xhr.response);
        part1[count].innerHTML = "<img src="+ poke_state.sprites.front_default + ">";
    });
    const pokemon_count = pokemon.length;
    for(; count < pokemon_count; count++) {
        const moves = pokemon[count]["moves"];
        constructGraph([["Move", "Movecount"]].concat((moves.map((k, j) =>
        [moves[j][0], moves[j][1]]))), graphs[count]
        );
        xhr.open('GET', 'https://pokeapi.co/api/v2/pokemon/' + pokemon[count]["name"] +'/', true);
        xhr.send(null);
        
    }
}