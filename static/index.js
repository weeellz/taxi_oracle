ymaps.ready(init);

var g_coords = [[0,0], [0,0]];
var g_cur = 0;
var g_ready = false;
var myPlacemark1;
var myPlacemark2;
var myMap;

var set_cur = function(coords) {
    if (g_ready){
        return
    }
    g_coords[g_cur] = coords;
    g_cur = (g_cur + 1) % 2;
    if(g_cur == 0) {
        g_ready = true;
    }
};

var reset = function(){
    g_ready = false;
    g_coords = [[0,0], [0,0]];
    myMap.geoObjects.removeAll();
    $("#count").val("");
    //alert("done");
}

var send = function(){
    var data = createJson();
    console.log(data);
    //$.post("/api", json, function(data) {console.log(data)}, "json");
    $.ajax({
        url:"/api",
        type:"POST",
        data:JSON.stringify(data),
        contentType:"application/json; charset=utf-8",
        dataType:"json",
        success: function(data){
          alert(data.result + " долларов") 
      }
  })
}

var createJson = function(){
    var json = {
        "pickup_datetime": new Date().format("Y-m-d H:i:s") + " UTC",
        "pickup_longitude": g_coords[0][1],
        "pickup_latitude": g_coords[0][0],
        "dropoff_longitude": g_coords[1][1],
        "dropoff_latitude": g_coords[1][0],
        "passenger_count": 1
    };
    return json;
}

function init() {
    $("#reset").click(reset);
    $("#send").click(send);
    myMap = new ymaps.Map('map', {
        center: [40.731262, -73.998213],
        zoom: 12
    }, {
        searchControlProvider: 'yandex#search'
    });

    // Слушаем клик на карте.
    myMap.events.add('click', function (e) {
        if(g_ready){
            //alert("full");
            return
        }
        else{
            var coords = e.get('coords');
            set_cur(coords);
            myPlacemark1 = createPlacemark(g_coords[0]);
            myMap.geoObjects.add(myPlacemark1);
            myPlacemark2 = createPlacemark(g_coords[1]);
            myMap.geoObjects.add(myPlacemark2);
        }
        //getAddress(coords);
    });

    // Создание метки.
    function createPlacemark(coords) {
        return new ymaps.Placemark(coords, {
            iconCaption: coords
        }, {
            preset: 'islands#violetDotIconWithCaption',
            draggable: false
        });
    }
}