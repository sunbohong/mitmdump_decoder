var map = L.map('map');
var hash = new L.Hash(map);

L.tileLayer.provider('OpenStreetMap.Mapnik', {retina: true}).addTo(map);
//Add UI controls to toggle later
//L.tileLayer.provider('Watercolor').addTo(map);

var filters = document.getElementById('filters');
filters.onclick = function() {
  gmo.update();
  player.update();
};

var autoloadOptions = {
  interval: 10 * 1000,
  style: function(feature) { return feature.properties; },
  pointToLayer: customStyle,

  filter: checkboxFilter,
  onEachFeature: function (feature, layer) {
    layer.bindPopup(feature.properties.title);
    layer.on('mouseover', function (e) {
      this.openPopup();
    });
    layer.on('mouseout', function (e) {
      this.closePopup();
    });
  }
}

var player = L.realtime({url: 'player.json', type: 'json'}, autoloadOptions).addTo(map);
var gmo = L.realtime({url: 'get_map_objects.json', type: 'json'}, autoloadOptions).addTo(map);

var loaded = false;
gmo.on('update', function(updateEvent) {
  if(!loaded && Object.keys(updateEvent.features).length > 0) {
    loaded = true;
    //Set the view after the first load
    map.fitBounds(gmo.getBounds(), {maxZoom: 16});
  } else {
    if ("geolocation" in navigator){
      //This will ask the user to use their location data.
      map.locate({setView : true});
    }
  }
});

function checkboxFilter(feature) {
  if (!loaded) {
    return true;
  }
  var box = document.getElementById(feature.properties.type);
  return box == null || box.checked;
}

//https://gist.github.com/tmcw/3861338
function simplestyle(f, latlon) {
    var sizes = {
      small: [20, 50],
      medium: [30, 70],
      large: [35, 90]
    };
    var fp = f.properties || {};
    var size = fp['marker-size'] || 'medium';
    var symbol = (fp['marker-symbol']) ? '-' + fp['marker-symbol'] : '';
    var color = fp['marker-color'] || '7e7e7e';
    color = color.replace('#', '');
    var url = 'http://a.tiles.mapbox.com/v3/marker/' +
          'pin-' +
          // Internet Explorer does not support the `size[0]` syntax.
          size.charAt(0) + symbol + '+' + color +
          ((window.devicePixelRatio === 2) ? '@2x' : '') +
          '.png';

    var icon = new L.icon({
        iconUrl: url,
        iconSize: sizes[size],
        iconAnchor: [sizes[size][0] / 2, sizes[size][1]/2],
        popupAnchor: [-3, -sizes[size][1]/2]
      });

    return new L.Marker(latlon, {
      icon: icon
    });
}

function customStyle(f, latlon) {
    var marker = simplestyle(f, latlon);
    var properties = f.properties;

    if (properties.distance > 0) {
      var marker = L.circle(latlon, properties.distance, {
        fill: false,
      });
    }

    if (properties.type == 'pokestop') {
      if(properties.lure){
          marker.setIcon(pokestopLureIcon);
      } else {
          marker.setIcon(pokestopIcon);
      }
    } else if (properties.type == 'pokemon') {
      marker.setIcon(pokemonIcon);
    } else if (properties.type == 'gym') {
        if (properties.team == "TEAM_BLUE") {
            marker.setIcon(blueGymIcon);
        } else if (properties.team == "TEAM_RED") {
            marker.setIcon(redGymIcon);
        } else if (properties.team == "TEAM_YELLOW") {
            marker.setIcon(yellowGymIcon);
        } else {
          marker.setIcon(neutralGymIcon);
        }
    }

    return marker;
}

var GymIcon = L.Icon.extend({
  options: {
     iconSize:     [45, 48],
     iconAnchor:   [22, 48],
     popupAnchor:  [-3, -58]
  }
});

var PokemonIcon = L.Icon.extend({
  options: {
     iconSize:     [32, 48],
     iconAnchor:   [16, 48],
     popupAnchor:  [-3, -58]
  }
});

var PokestopIcon = PokemonIcon; //Coincidentially the same size

var blueGymIcon = new GymIcon({iconUrl: 'img/arena_blue.png'});
var redGymIcon = new GymIcon({iconUrl: 'img/arena_red.png'});
var yellowGymIcon = new GymIcon({iconUrl: 'img/arena_yellow.png'});
var neutralGymIcon = new GymIcon({iconUrl: 'img/arena_white.png'});

var pokemonIcon = new PokemonIcon({iconUrl: 'img/pokemon.png'});

var pokestopIcon = new PokestopIcon({iconUrl: 'img/pokestop.png'});
var pokestopLureIcon = new PokestopIcon({iconUrl: 'img/pokestoppink.png'});
