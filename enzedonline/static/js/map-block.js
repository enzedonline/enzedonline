//========map block ============

// get the map block settings
const draw_mapblock = (uid) => {
  const map_settings = JSON.parse(document.getElementById(uid).textContent);
  include_css("https://api.tiles.mapbox.com/mapbox-gl-js/v3.2.0/mapbox-gl.css");
  include_js("https://api.tiles.mapbox.com/mapbox-gl-js/v3.2.0/mapbox-gl.js")
    .then(() => {
      add_mapbox(map_settings);
    });
};

// add the map using supplied settings
const add_mapbox = (map_settings) => {
  // map_settings should be similar structure to the below with max 25 waypoints
  // {
  //   "uid": "block.id",
  //   "token": "your.mapbox.token",
  //   "route_type": "walking",
  //   "show_route_info": true,
  //   "padding": [50, 50, 50, 50],
  //   "waypoints": [
  //       {"longitude": 11.77624, "latitude": 42.1541, "pin_label": "a", "show_pin": true},
  //       {"longitude": 12.128261, "latitude": 42.168219, "pin_label": "b", "show_pin": true}
  //   ]
  // }

  // create base map object
  mapboxgl.accessToken = map_settings.token;
  const map = new mapboxgl.Map({
    container: `map-${map_settings.uid}`,
    style: "mapbox://styles/mapbox/outdoors-v12",
  });
  map.addControl(new mapboxgl.NavigationControl());
  map.addControl(new mapboxgl.ScaleControl({ position: "bottom-right" }));
  // map.scrollZoom.disable();

  // set the initial bounds of the map, bound set again after route loads
  const arrayColumn = (arr, n) => arr.map((x) => x[n]);
  const min_lat = Math.min(...arrayColumn(map_settings.waypoints, "latitude"));
  const max_lat = Math.max(...arrayColumn(map_settings.waypoints, "latitude"));
  const min_lng = Math.min(...arrayColumn(map_settings.waypoints, "longitude"));
  const max_lng = Math.max(...arrayColumn(map_settings.waypoints, "longitude"));
  map.fitBounds(
    [
      [min_lng, min_lat],
      [max_lng, max_lat],
    ],
    {
      padding: {
        top: map_settings.padding[0],
        right: map_settings.padding[1],
        bottom: map_settings.padding[2],
        left: map_settings.padding[3],
      },
    }
  );

  // add layers and markers after base map loads
  map.on("load", () => {
    if (map_settings.method !== "no-route") {
      getRoute(map_settings.waypoints);
      // Add starting and end points to the map
      map.addLayer({
        id: "start",
        type: "circle",
        source: {
          type: "geojson",
          data: {
            type: "FeatureCollection",
            features: [
              {
                type: "Feature",
                properties: {},
                geometry: {
                  type: "Point",
                  coordinates: [
                    map_settings.waypoints[0].longitude,
                    map_settings.waypoints[0].latitude,
                  ],
                },
              },
            ],
          },
        },
        paint: {
          "circle-radius": 10,
          "circle-color": "#3887be",
        },
      });
      const end_index = map_settings.waypoints.length - 1;
      map.addLayer({
        id: "end",
        type: "circle",
        source: {
          type: "geojson",
          data: {
            type: "FeatureCollection",
            features: [
              {
                type: "Feature",
                properties: {},
                geometry: {
                  type: "Point",
                  coordinates: [
                    map_settings.waypoints[end_index].longitude,
                    map_settings.waypoints[end_index].latitude,
                  ],
                },
              },
            ],
          },
        },
        paint: {
          "circle-radius": 10,
          "circle-color": "#f30",
        },
      });
    }

    // add markers with Google Maps links
    map_settings.waypoints.forEach((waypoint) => {
      if (waypoint.show_pin) {
        const waypointLabel = waypoint.pin_label ? `<b>${waypoint.pin_label}</b><br>` : '';
        const marker = new mapboxgl.Marker()
          .setLngLat([waypoint.longitude, waypoint.latitude])
          .setPopup(
            new mapboxgl.Popup().setHTML(
              `${waypointLabel}<a href="https://www.google.com/maps?q=${waypoint.latitude},${waypoint.longitude}" 
                       target="_blank">${waypoint.latitude}, ${waypoint.longitude}</a>`
            )
          ) // add popup
          .addTo(map);
      }
    });
  });

  // create a function to make a directions request
  const getRoute = async (coord_list) => {
    // build the gps points query string
    const points = coord_list.map((coord) => [coord.longitude, coord.latitude].join());
    const gps_list = points.join(";");
    const query = await fetch(
      `https://api.mapbox.com/directions/v5/mapbox/${map_settings.route_type}/${gps_list}?steps=false&geometries=geojson&access_token=${mapboxgl.accessToken}`,
      { method: "GET" }
    );
    // request json data
    const json = await query.json();
    const data = json.routes[0];
    const route = data.geometry.coordinates;
    const geojson = {
      type: "Feature",
      properties: {},
      geometry: {
        type: "LineString",
        coordinates: route,
      },
    };
    map.addLayer({
      id: `route-${map_settings.uid}`,
      type: "line",
      source: {
        type: "geojson",
        data: geojson,
      },
      layout: {
        "line-join": "round",
        "line-cap": "round",
      },
      paint: {
        "line-color": "#3887be",
        "line-width": 5,
        "line-opacity": 0.75,
      },
    });

    // send route length info back to page
    if (map_settings.show_route_info) {
      document.getElementById(`distance-${map_settings.uid}`).innerText = (
        Math.round(data.distance / 100) / 10
      ).toFixed(1);
      // document.getElementById(`hours-${map_settings.uid}`).innerText = (
      //   Math.round(data.duration / 360) / 10
      // ).toFixed(1);
      document.getElementById(`routesummary-${map_settings.uid}`).style.display =
        "block";
    }

    // set map bounds to fit route
    const bounds = new mapboxgl.LngLatBounds(route[0], route[0]);
    for (const coord of route) {
      bounds.extend(coord);
    }
    map.fitBounds(bounds, {
      padding: {
        top: map_settings.padding[0],
        right: map_settings.padding[1],
        bottom: map_settings.padding[2],
        left: map_settings.padding[3],
      },
    });
  };

};
