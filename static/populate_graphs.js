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
function constructGraph(moveinfo, graph, name) {
    const data=google.visualization.arrayToDataTable(moveinfo);
    const colours=['rgb(159, 161, 159)', 'rgb(238, 135, 50)', 'rgb(141, 184, 234)', 'rgb(135, 69, 196)'];
    const options ={is3D:true, colors:colours, title:name};
    let chart=new google.visualization.PieChart(graph);
    chart.draw(data, options);
}

// im so sorry for this code

if(document.URL.includes("visualise")) {
    google.charts.setOnLoadCallback(drawFunction);
}


var count = 0;
function drawFunction() {
    var graphs = document.querySelectorAll(".content > .part3-container > .part3");

    const pokemon_count = pokemon.length;
    for(; count < pokemon_count; count++) {
        const moves = pokemon[count]["moves"];
        constructGraph([["Move", "Movecount"]].concat((moves.map((k, j) =>
        [moves[j][0], moves[j][1]]))), graphs[count], pokemon[count]["name"]
        );  
    }
}