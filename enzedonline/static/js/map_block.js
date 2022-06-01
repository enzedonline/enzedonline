$(document).ready(function () {
  // pull in django template values
  const coords = JSON.parse(document.getElementById("waypoint_list").textContent);
  const method = JSON.parse(document.getElementById("method").textContent);
  const show_route_info = JSON.parse(document.getElementById("show_route_info").textContent);
  const uid = JSON.parse(document.getElementById("uid").textContent);
  const padding = JSON.parse(document.getElementById("padding").textContent);
  const token = JSON.parse(document.getElementById("token").textContent);
  let end_index = coords.length - 1;

  // create base map object
  mapboxgl.accessToken = token;
  const map = new mapboxgl.Map({
    container: "map-" + uid,
    style: "mapbox://styles/mapbox/outdoors-v11",
  });
  map.addControl(new mapboxgl.NavigationControl());
  map.addControl(new mapboxgl.ScaleControl({ position: "bottom-right" }));

  // set the initial bounds of the map, bound set again after route loads
  const arrayColumn = (arr, n) => arr.map((x) => x[n]);
  const min_lat = Math.min(...arrayColumn(coords, 0));
  const max_lat = Math.max(...arrayColumn(coords, 0));
  const min_lng = Math.min(...arrayColumn(coords, 1));
  const max_lng = Math.max(...arrayColumn(coords, 1));
  map.fitBounds(
    [
      [min_lng, min_lat],
      [max_lng, max_lat],
    ],
    {
      padding: {
        top: padding[0],
        right: padding[1],
        bottom: padding[2],
        left: padding[3],
      },
    }
  );

  // create a function to make a directions request
  async function getRoute(coord_list) {
    // build the gps points query string
    let points = [];
    for (let i = 0; i < coord_list.length; i++) {
      points.push([coord_list[i][1], coord_list[i][0]].join());
    }
    let gps_list = points.join(";");
    const query = await fetch(
      `https://api.mapbox.com/directions/v5/mapbox/${method}/${gps_list}?steps=false&geometries=geojson&access_token=${mapboxgl.accessToken}`,
      { method: "GET" }
    );
    // request json data
    const json = await query.json();
    const data = json.routes[0];
    console.log(data);
    const route = data.geometry.coordinates;
    const geojson = {
      type: "Feature",
      properties: {},
      geometry: {
        type: "LineString",
        coordinates: route,
      },
    };
    // if the route already exists on the map, we'll reset it using setData
    if (map.getSource("route")) {
      map.getSource("route").setData(geojson);
    }
    // otherwise, we'll make a new request
    else {
      map.addLayer({
        id: "route",
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
    }
    // set map bounds to fit route
    const bounds = new mapboxgl.LngLatBounds(route[0], route[0]);
    for (const coord of route) {
      bounds.extend(coord);
    }
    map.fitBounds(bounds, {
      padding: {
        top: padding[0],
        right: padding[1],
        bottom: padding[2],
        left: padding[3],
      },
    });
    // send route length info back to page
    if (show_route_info){
      document.getElementById("distance-" + uid).innerText = (
        Math.round(data.distance / 100) / 10
      ).toFixed(1);
      document.getElementById("hours-" + uid).innerText = (
        Math.round(data.duration / 360) / 10
      ).toFixed(1);
      document.getElementById("route-" + uid).style.display = "block";
    }
  }

  map.on("load", () => {
    if (method != "no-route") {
      getRoute(coords);
    }
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
                coordinates: [coords[0][1], coords[0][0]],
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
                coordinates: [coords[end_index][1], coords[end_index][0]],
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

    // add markers with Google Maps links
    for (let i = 0; i <= end_index; i++) {
      if (coords[i][3]) {
        const marker = new mapboxgl.Marker()
          .setLngLat([coords[i][1], coords[i][0]])
          .setPopup(
            new mapboxgl.Popup().setHTML(
              "<b>" +
                coords[i][2] +
                "</b><br/>" +
                `<a href="https://www.google.com/maps?q=${coords[i]
                  .slice(0, 2)
                  .join()}" target="_blank">${coords[i]
                  .slice(0, 2)
                  .join(", ")}</a>`
            )
          ) // add popup
          .addTo(map);
      }
    }

    // call route last
  });
});
