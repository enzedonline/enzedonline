// Usage: document.getElementById("id").innerHTML = convertUTCDateToLocalDate(new Date('02 Aug 2021 09:58:22'));
let convertUTCDateToLocalDate = (date) => {
    local_date = new Date(date.getTime() + date.getTimezoneOffset() * 60000);
    const date_options = {
      weekday: "short",
      year: "numeric",
      month: "long",
      day: "numeric",
    };
    const time_options = { hour: "2-digit", minute: "2-digit", hour12: false };
    return (
      local_date.toLocaleDateString(undefined, date_options) +
      " " +
      local_date.toLocaleTimeString(undefined, time_options)
    );
  };
  
  $(document).ready(function () {
    $('a[href^="http://"]').attr("target", "_blank");
    $('a[href^="http://"]').attr("rel", "nofollow noopener");
    $('a[href^="https://"]').attr("target", "_blank");
    $('a[href^="https://"]').attr("rel", "nofollow noopener");
  });
  
  $(document).ready(function () {
    fa_icons = document.getElementsByTagName('fa')  
    for (let i = 0; i < fa_icons.length; i++) {
      const fa_class = fa_icons[i].innerText
      fa_icons[i].innerText = ""
      const fa = fa_icons[i].appendChild(document.createElement("i"));
      fa.className = fa_class
    }
  });
  
  //========map block ============
  
  // get the map block settings
  let draw_mapblock = (uid) => {
    const map_settings = JSON.parse(
      document.getElementById(`${uid}`).textContent
    );
    add_mapbox(map_settings);
  };
  
  // add the map using supplied settings
  let add_mapbox = (map_settings) => {
    // map_settings should be similar structure to the below with max 25 waypoints
    //   {
    //     "uid": "block.id",
    //     "token": "your.mapbox.token",
    //     "route_type": "walking",
    //     "show_route_info": true,
    //     "padding": [
    //         50,
    //         50,
    //         50,
    //         50
    //     ],
    //     "waypoints": [
    //         {
    //             "longitude": 11.77624,
    //             "latitude": 42.1541,
    //             "pin_label": "a",
    //             "show_pin": true
    //         },
    //         {
    //             "longitude": 12.128261,
    //             "latitude": 42.168219,
    //             "pin_label": "b",
    //             "show_pin": true
    //         }
    //     ]
    // }
  
    // create base map object
    mapboxgl.accessToken = map_settings.token;
    const map = new mapboxgl.Map({
      container: `map-${map_settings.uid}`,
      style: "mapbox://styles/mapbox/outdoors-v11",
    });
    map.addControl(new mapboxgl.NavigationControl());
    map.addControl(new mapboxgl.ScaleControl({ position: "bottom-right" }));
    //   map.scrollZoom.disable();
  
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
  
    // create a function to make a directions request
    async function getRoute(coord_list) {
      // build the gps points query string
      let points = [];
      for (let i = 0; i < coord_list.length; i++) {
        points.push([coord_list[i].longitude, coord_list[i].latitude].join());
      }
      let gps_list = points.join(";");
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
          document.getElementById(`hours-${map_settings.uid}`).innerText = (
            Math.round(data.duration / 360) / 10
          ).toFixed(1);
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
    }
  
    map.on("load", () => {
      if (map_settings.method != "no-route") {
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
        let end_index = map_settings.waypoints.length - 1;
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
      map_settings.waypoints.forEach(function (waypoint) {
        if (waypoint.show_pin) {
          const marker = new mapboxgl.Marker()
            .setLngLat([waypoint.longitude, waypoint.latitude])
            .setPopup(
              new mapboxgl.Popup().setHTML(
                "<b>" +
                  waypoint.pin_label +
                  "</b><br/>" +
                  `<a href="https://www.google.com/maps?q=${waypoint.latitude},${waypoint.longitude}" 
                         target="_blank">${waypoint.latitude}, ${waypoint.longitude}</a>`
              )
            ) // add popup
            .addTo(map);
        }
      });
    });
  };