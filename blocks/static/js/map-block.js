// mapSettings should be similar structure to the below with max 25 waypoints
// {
//   uid: "id",
//   token: "your.mapbox.token",
//   urls: {
//     mapboxGlCSS: "https://api.tiles.mapbox.com/mapbox-gl-js/v3.8.0/mapbox-gl.css",
//     mapboxGlJS: "https://api.tiles.mapbox.com/mapbox-gl-js/v3.8.0/mapbox-gl.js",
//     directionsAPI: "https://api.mapbox.com/directions/v5/mapbox/"
//   },
//   pitch: 0,
//   bearing: 0,
//   padding: {top: 5, right: 10, bottom: 5, left:10},
//   styles = { 
//     "satellite": {
//         "description": "Satellite",
//         "url": "mapbox://styles/mapbox/satellite-v9",
//         "tileImage": "/media/images/sattelite_tile.png"
//     },
//     "terrain": {
//         "description": "Terrain",
//         "url": "mapbox://styles/mapbox/outdoors-v12",
//         "tileImage": "/media/images/terrain_tile.png"
//     }
//   }
//   initialStyle: "terrain", 
//   waypoints: [
//       {longitude: 11.77624, latitude": 42.1541, pinLabel: "a", showPin: true},
//       {longitude: 12.128261, latitude": 42.168219, pinLabel: "b", showPin: true}
//   ]
//   route: {
//      type: "walking",
//      showSummary: true,
//      summaryHeading: "Route Summary"
//   }
// }
// Notes:
// padding values are integers expressing padding as a percentage of the map, not pixels

class MapBlock {
    static colours = {
        route: '#0060f0',
        start: '#02b875',
        end: '#d9534f'
    }

    constructor(uid) {
        window.mapBlock = this;
        // read settings and dispose the json element
        const settingsElement = document.getElementById(uid);
        this.mapSettings = JSON.parse(settingsElement.textContent);
        settingsElement.remove();
        // set minimum pitch value
        if (this.mapSettings.pitch < 5) this.mapSettings.pitch = 5;
        // load mapbox-gl js & css
        include_js(this.mapSettings.urls.mapboxGlJS)
            .then(() => {
                this.initialiseMap(uid);
            });
        include_css(this.mapSettings.urls.mapboxGlCSS);
        this.mapSettings.showElevationProfile = (
            ['cycling', 'walking'].includes(this.mapSettings.route.type) && this.mapSettings.route.showSummary === 'detailed'
        );
        if (this.mapSettings.showElevationProfile) include_js("https://cdn.jsdelivr.net/npm/chart.js");
    }

    initialiseMap = () => {
        mapboxgl.accessToken = this.mapSettings.token;
        this.blockContainer = document.getElementById(`mapblock-${this.mapSettings.uid}`);
        this.mapContainer = this.blockContainer.querySelector(`#map-${this.mapSettings.uid}`);
        // create placeholder route table if relevant
        if (this.mapSettings.route.type && this.mapSettings.route.showSummary) {
            this.createRouteInfoTable()
        };
        // extract [lng, lat] from waypoint objects
        this.points = this.mapSettings.waypoints.map(
            waypoint => [waypoint.longitude, waypoint.latitude]
        );
        // calculate padding as px relative to map block container
        this.absolutePadding = {
            top: this.blockContainer.offsetHeight * this.mapSettings.padding.top / 100,
            right: this.blockContainer.offsetWidth * this.mapSettings.padding.right / 100,
            bottom: this.blockContainer.offsetHeight * this.mapSettings.padding.bottom / 100,
            left: this.blockContainer.offsetWidth * this.mapSettings.padding.left / 100
        };
        // create map
        this.add_mapbox();
        // add markers for any waypoints with 'show pin'
        this.addMarkers();

    }

    add_mapbox = () => {
        // get bounding box of waypoints
        const initialBounds = this.findInitialBounds(this.points);
        // create base map object with camera options based on settings & bounds
        // do not apply pitch before calculating screen bounding box
        this.map = new mapboxgl.Map({
            container: `map-${this.mapSettings.uid}`,
            style: this.mapSettings.styles[this.mapSettings.initialStyle].url,
            bounds: initialBounds,
            fitBoundsOptions: {
                bearing: this.mapSettings.bearing,
                padding: { ...this.absolutePadding },
            }
        });
        // add style load handler
        this.map.once('style.load', this.onInitialStyleLoad);
        // add compass, scale and full-screen controls
        this.map.addControl(new mapboxgl.NavigationControl({ visualizePitch: true }));
        this.map.addControl(new mapboxgl.ScaleControl({ position: "bottom-right" }));
        this.map.addControl(new mapboxgl.FullscreenControl());
        // add feature class instance
        this.mapFeature = new MapFeature(this.map, ['doc-huts', 'doc-campsites', 'doc-tracks-eam-clickable', 'doc-tracks-api-clickable']);
    }

    onInitialStyleLoad = async () => {
        // first run, fetch any route data and fit bounds to container if route, bearing or pitch applied
        // cache any custom layers for later use
        this.customLayers = [];
        if (!!this.mapSettings.route.type) {
            await this.getRouteLayers();
            this.addCustomLayers();
            if (this.mapSettings.route.showSummary) {
                this.map.once('idle', async () => {
                    if (this.mapSettings.showElevationProfile) {
                        await this.getElevationProfile();
                        this.drawElevationProfile();
                    }
                    this.showRouteInfo();
                })
            }
            // set map bounds to fit route
            this.fitBoundsToContainer(new ScreenBounds(this.map, this.routeData.geometry.coordinates));
        } else if (this.mapSettings.bearing !== 0 || this.mapSettings.pitch !== 0) {
            // refit map if pitch and/or bearing is non-zero
            this.fitBoundsToContainer(new ScreenBounds(this.map, this.points));
        }
        // add style tiles if multiple styles available
        this.addStyleOptions();
        // add listener for subsequent style loads to re-add custom layers
        this.map.on('style.load', this.onStyleLoad);

        // add click event listener to show map feature info
        // define timeout to distinguish between single and double clicks
        this.clickTimeout = null;
        this.map.on('click', (e) => {
            // Clear any pending click event
            if (this.clickTimeout) {
                clearTimeout(this.clickTimeout);
                this.clickTimeout = null;
                return; // Ignore click if it's part of a double-click
            }
            // Schedule the click event with a short delay
            this.clickTimeout = setTimeout(() => {
                this.showFeatureInfo(e);
                this.clickTimeout = null; // Reset timeout after execution
            }, 250);
        });
        this.map.on('dblclick', () => {
            // If a double-click occurs, cancel the scheduled click event
            if (this.clickTimeout) {
                clearTimeout(this.clickTimeout);
                this.clickTimeout = null;
            }
        });
    }

    onStyleLoad = async () => {
        // custom layers must be re-added if style changes after loading
        if (this['customLayers']) {
            this.addCustomLayers();
        }
        // update displayed selected style tile
        this.previousStyle.classList.remove('active');
        this.activeStyle.classList.add('active');
    }

    addCustomLayers = async () => {
        // add all the layers in the customLayers array to the map
        this.customLayers.forEach(layer => {
            this.map.addLayer(layer);
        });
    }

    addStyleOptions = async () => {
        if (Object.entries(this.mapSettings.styles).length > 1) {
            // create tile for each available style
            // set style tile initial value and add click listener
            this.styleTileContainer = document.createElement('div');
            this.styleTileContainer.classList = 'mapbox-style-tile-container';
            for (const [key, value] of Object.entries(this.mapSettings.styles)) {
                const styleTile = document.createElement('img');
                styleTile.src = value.tileImage;
                styleTile.title = value.description;
                styleTile.dataset.mapStyle = key;
                if (key === this.mapSettings.initialStyle) {
                    styleTile.classList = 'active';
                    this.activeStyle = styleTile;
                };
                this.styleTileContainer.append(styleTile);
            }
            this.mapContainer.after(this.styleTileContainer);
            this.styleTileContainer.onclick = (event) => {
                const clickedStyle = event.target.closest("[data-map-style]");
                if (clickedStyle && clickedStyle !== this.activeStyle) {
                    this.map.setStyle(this.mapSettings.styles[clickedStyle.dataset.mapStyle].url);
                    this.previousStyle = this.activeStyle;
                    this.activeStyle = clickedStyle;
                }
            }
        }
    }

    addMarkers = async () => {
        // add markers with Google Maps links
        const showRoute = (!!this.mapSettings.route.type)
        this.mapSettings.waypoints.forEach((waypoint, index) => {
            // Set marker configuration for the first and last waypoint if showRoute is true
            const config = showRoute
                ? (index === 0
                    ? { color: MapBlock.colours.start }
                    : index === this.mapSettings.waypoints.length - 1
                        ? { color: MapBlock.colours.end }
                        : {})
                : {};
            if (waypoint.showPin) {
                // Construct waypoint label
                const waypointLabel = `${waypoint.pinLabel ? `<b>${waypoint.pinLabel}</b><br>` : ''}` +
                    `<a href="https://www.google.com/maps?q=${waypoint.latitude},${waypoint.longitude}" 
                        target="_blank" class="map-block-waypoint-link">${waypoint.latitude}, ${waypoint.longitude}</a>`;
                // Create a popup and marker for the waypoint
                new mapboxgl.Marker(config)
                    .setLngLat([waypoint.longitude, waypoint.latitude])
                    .setPopup(new mapboxgl.Popup().setHTML(waypointLabel))
                    .addTo(this.map);
            }
        });
    }

    showFeatureInfo = (e) => {
        this.mapFeature.showFeatureInfo(e);
    }

    getRouteLayers = async () => {
        // fetch route data and add layer configs to customLayers()
        // build the gps points query string
        const points = this.mapSettings.waypoints.map((coord) => [coord.longitude, coord.latitude].join()).join(";");
        // get directions API response - set steps=true to return data on each route leg
        let options = `steps=true&geometries=geojson&access_token=${mapboxgl.accessToken}`
        if (this.mapSettings.route.type === 'walking') { options += '&walkway_bias=1' }
        const query = await fetch(
            `${this.mapSettings.urls.directionsAPI}${this.mapSettings.route.type}/${points}?${options}`,
            { method: "GET" }
        );
        // return if api call not successful
        if (!query.ok) {
            console.warn("Map Block: Error determining route");
            return
        }
        // read body stream
        const json = await query.json();
        // routes is an array, no alternatives requested, array has ony one member
        // routeData used to display route information (distance, duration etc)
        this.routeData = json.routes[0];
        const stepCoordinates = this.routeData.legs.flatMap(leg =>
            leg.steps.reduce((acc, step) => acc.concat(step.geometry.coordinates), [])
        ).filter((coord, index, array) =>
            index === 0 || Math.abs(coord[0] - array[index - 1][0]) > 1e-6 || Math.abs(coord[1] - array[index - 1][1]) > 1e-6
        );
        const geojson = {
            type: "Feature",
            properties: {},
            geometry: {
                type: "LineString",
                coordinates: stepCoordinates
            },
        };
        // add layer configs to customLayers array
        this.customLayers.push(this.getRouteLayerConfig(geojson));
        this.customLayers.push(this.getEndpointLayerConfig('start', this.mapSettings.waypoints[0], MapBlock.colours.start));
        this.customLayers.push(this.getEndpointLayerConfig('end', this.mapSettings.waypoints.at(-1), MapBlock.colours.end));
    }

    showRouteInfo = async () => {
        if (this.mapSettings.route.showSummary === 'detailed') {
            // Populate route info table with distance data
            const tbody = this.routeSummaryElement.querySelector('tbody');
            const rows = tbody.querySelectorAll('tr');
            // Populate distance for each leg
            this.routeData.legs.forEach((leg, index) => {
                const cells = rows[index]?.querySelectorAll('td');
                if (cells[1]) cells[1].textContent = `${(leg.distance / 1000).toFixed(1)}km`;
                if (this.mapSettings.showElevationProfile) {
                    if (cells[2]) cells[2].textContent = `${leg.elevation.gain.toFixed(0)}m`;
                    if (cells[3]) cells[3].textContent = `${leg.elevation.loss.toFixed(0)}m`;
                }
            });
            // Populate total distance in the footer
            const footerCells = this.routeSummaryElement.querySelectorAll('tfoot td');
            if (footerCells[1]) footerCells[1].textContent = `${(this.routeData.distance / 1000).toFixed(1)}km`;
            if (this.mapSettings.showElevationProfile) {
                if (footerCells[2]) footerCells[2].textContent = `${this.routeData.elevationGain.toFixed(0)}m`;
                if (footerCells[3]) footerCells[3].textContent = `${this.routeData.elevationLoss.toFixed(0)}m`;
            }
        } else {
            this.routeSummaryElement.append(`${(this.routeData.distance / 1000).toFixed(1)}km`);
        }
    }

    createRouteInfoTable = async () => {
        if (this.mapSettings.showElevationProfile) {
            // Create a new div element for the chart
            const chartContainer = document.createElement("div");
            chartContainer.style.width = "100%";
            chartContainer.style.height = "180px";
            chartContainer.style.position = "relative"; // Ensure proper sizing
            this.elevationPlaceholder = document.createElement("div");
            this.elevationPlaceholder.style.height = "100%";
            this.elevationPlaceholder.className = "d-flex mt-2 justify-content-center align-items-center border border-secondary-subtle rounded-3";
            this.elevationPlaceholder.textContent = "Loading elevation profile...";
            chartContainer.appendChild(this.elevationPlaceholder);
            this.blockContainer.appendChild(chartContainer); // Append to block container            
            // Create a canvas for Chart.js
            this.chartCanvas = document.createElement("canvas");
            chartContainer.appendChild(this.chartCanvas);
        }

        // Create route info table for populating once route data is available 
        this.routeSummaryElement = document.createElement('div');
        this.routeSummaryElement.class = 'map-block-routesummary';
        if (this.mapSettings.route.showSummary == 'detailed') {
            if (this.mapSettings.showElevationProfile) {
                // add arrow svg only if not already present in document
                if (!document.getElementById('mapblock-arrow-container')) {
                    const arrowContainer = document.createElement('div');
                    arrowContainer.id = "mapblock-arrow-container";
                    arrowContainer.style.display = 'none';
                    arrowContainer.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512" id="elevation-increase"> 
                        <path d="M384 160c-17.7 0-32-14.3-32-32s14.3-32 32-32l160 0c17.7 0 32 14.3 32 32l0 160c0 17.7-14.3 32-32 32s-32-14.3-32-32l0-82.7L342.6 374.6c-12.5 12.5-32.8 12.5-45.3 0L192 269.3 54.6 406.6c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3l160-160c12.5-12.5 32.8-12.5 45.3 0L320 306.7 466.7 160 384 160z"/>
                    </svg>`;
                    this.routeSummaryElement.appendChild(arrowContainer);
                }
            }
            const table = document.createElement('table');
            table.className = 'table table-sm table-hover route-summary-table';
            const dataColCount = this.mapSettings.showElevationProfile ? 3 : 1;

            // table heading
            const thead = document.createElement('thead');
            thead.className = "table-light font-headings";
            const theadRow = document.createElement('tr');
            let th = document.createElement('th');
            th.textContent = this.mapSettings.route.summaryHeading;
            th.setAttribute("colspan", "2");
            if (this.mapSettings.showElevationProfile) {
                // Add columns for ascent, descent
                theadRow.appendChild(th);
                th = document.createElement('th');
                th.classList = "text-end"
                const svgAscent = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                svgAscent.setAttribute('width', '1.2em');
                svgAscent.setAttribute('height', '1em');
                const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
                use.setAttribute('href', '#elevation-increase');
                svgAscent.appendChild(use);
                th.appendChild(svgAscent);
                theadRow.appendChild(th);
                th = document.createElement('th');
                th.classList = "text-end"
                const svgDescent = svgAscent.cloneNode(true);
                svgDescent.style.transform = 'rotateX(180deg)';
                svgDescent.style.transformOrigin = 'center';
                th.appendChild(svgDescent);
                theadRow.appendChild(th);
            }
            thead.appendChild(theadRow);
            table.appendChild(thead);
            // table body
            const tbody = document.createElement('tbody');
            table.appendChild(tbody);
            // Loop through legs and populate rows - each leg is between 2 waypoints (n - n+1)
            this.mapSettings.waypoints.forEach((waypoint, index) => {
                if (index < this.mapSettings.waypoints.length - 1) {
                    const row = document.createElement('tr');
                    // First column: waypoint labels
                    const label1 = waypoint.pinLabel || `Waypoint ${index}`;
                    const label2 = this.mapSettings.waypoints[index + 1].pinLabel || `Waypoint ${index + 1}`;
                    const descriptionCell = document.createElement('td');
                    descriptionCell.textContent = `${label1} - ${label2}`;
                    row.appendChild(descriptionCell);
                    // distance, ascent, descent columns

                    [...Array(dataColCount)].forEach(() => {
                        const cell = document.createElement('td');
                        cell.classList.add('route-distance-cell');
                        cell.textContent = '-';
                        row.appendChild(cell);
                    });
                    // Append row to the table body
                    tbody.appendChild(row);
                }
            });
            // Footer: Add the total distance as the final row
            const totalRow = document.createElement('tr');
            totalRow.appendChild(document.createElement('td'));
            [...Array(dataColCount)].forEach(() => {
                const cell = document.createElement('td');
                cell.classList.add('route-distance-cell');
                cell.textContent = '-';
                totalRow.appendChild(cell);
            });
            const tfoot = document.createElement('tfoot');
            tfoot.className = "table-group-divider table-light";
            tfoot.appendChild(totalRow);
            table.appendChild(tfoot);
            // Append the table to the route summary element
            this.routeSummaryElement.appendChild(table);
        } else {
            this.routeSummaryElement.textContent = `${this.mapSettings.route.summaryHeading}: `
        }
        // Append container to map block container
        this.blockContainer.append(this.routeSummaryElement);
    }

    getElevationProfile = async () => {
        let cumulativeDistance = 0;
        this.routeData.elevationGain = 0;
        this.routeData.elevationLoss = 0;
        this.routeData.elevationProfile = [];

        const getElevations = async (coordinates) => {
            const elevationPromises = coordinates.map(async coordinate => {
                const elevation = await this.map.queryTerrainElevation(coordinate, { exaggerated: false });
                return elevation;
            });
            return Promise.all(elevationPromises);
        };

        // Loop through each leg and step to calculate cumulative distance and elevation
        for (const [index, leg] of this.routeData.legs.entries()) {
            leg.elevation = {
                gain: 0,
                loss: 0,
                start: undefined
            }

            for (const step of leg.steps) {
                const stepCoordinates = step.geometry.coordinates;
                let elevations = [];
                if (this.mapSettings.showElevationProfile) {
                    // Get elevations for all coordinates in the step
                    elevations = await getElevations(stepCoordinates);
                    if (!leg.elevation.start) leg.elevation.start = elevations[0];
                    leg.elevation.end = elevations.at(-1);
                }

                // Process each coordinate and calculate the cumulative distance and elevation
                for (let index = 1; index < stepCoordinates.length; index++) {
                    // Calculate the distance between the current and previous coordinate
                    const fromLngLat = new mapboxgl.LngLat(...stepCoordinates[index - 1]);
                    const toLngLat = new mapboxgl.LngLat(...stepCoordinates[index]);
                    const distance = fromLngLat.distanceTo(toLngLat);
                    cumulativeDistance += distance;
                    if (this.mapSettings.showElevationProfile) {
                        const elevation = elevations[index];
                        this.routeData.elevationProfile.push({ distance: cumulativeDistance, elevation });
                        const previousElevation = elevations[index - 1];
                        const elevationDiff = elevation - previousElevation;
                        if (elevationDiff > 0) {
                            // Increase in elevation (gain)
                            leg.elevation.gain += elevationDiff;
                        } else if (elevationDiff < 0) {
                            // Decrease in elevation (loss)
                            leg.elevation.loss -= elevationDiff; // Subtract negative value to get a positive loss
                        }
                    }
                }
            }

            leg.endDistance = cumulativeDistance;
            leg.label = this.mapSettings.waypoints[index + 1].pinLabel ?? undefined;

            if (this.mapSettings.showElevationProfile) {
                // Update the total elevation gain/loss for the entire route
                this.routeData.elevationGain += leg.elevation.gain;
                this.routeData.elevationLoss += leg.elevation.loss;
            }
        }

        // After all promises resolve, you now have the elevation profile data and total elevation gain/loss
        // Elevation Profile Data: this.routeData.elevationProfile
        // Leg Elevation Data: this.routeData.legs
        // Total Elevation Gain: this.routeData.elevationGain
        // Total Elevation Loss: this.routeData.elevationLoss

    }

    drawElevationProfile = async () => {

        // Extract data for the chart
        const profileData = this.routeData.elevationProfile
            .map(point => ({
                x: point.distance / 1000, // Distance
                y: Math.round(point.elevation), // Elevation
            }));
        const tooltipData = this.routeData.legs
            .filter(leg => (!!leg.label))
            .map(leg => ({
                x: leg.endDistance / 1000, // Convert to km
                y: leg.elevation.end,
                label: leg.label, // Tooltip text (empty if no label)
            }));
        tooltipData.unshift({
            x: 0,
            y: this.routeData.legs[0].elevation.start,
            label: this.mapSettings.waypoints[0].pinLabel ?? 'Start'
        })

        // Configure Chart.js
        const droplinesPlugin = {
            id: 'droplines',
            beforeDatasetsDraw: (chart) => {
                const { ctx, scales } = chart;
                const xScale = scales.x;
                const yScale = scales.y;

                tooltipData.forEach(dataPoint => {
                    const xPixel = xScale.getPixelForValue(dataPoint.x);
                    const yPixel = yScale.getPixelForValue(dataPoint.y);

                    // Draw dropline
                    ctx.save();
                    ctx.strokeStyle = '#96B578'; // Light gray dropline
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(xPixel, yPixel); // Start at the endpoint
                    ctx.lineTo(xPixel, yScale.getPixelForValue(yScale.min)); // Drop to the bottom
                    ctx.stroke();
                    ctx.restore();
                });
            },
        };

        const titleFont = getComputedStyle(document.documentElement)
            .getPropertyValue('--font-family-headings')
            .trim();
        const bodyFont = getComputedStyle(document.documentElement)
            .getPropertyValue('--font-family-body')
            .trim();
        this.elevationPlaceholder.remove();

        new Chart(this.chartCanvas, {
            type: 'line',
            data: {
                datasets: [
                    {
                        label: 'Leg Endpoints',
                        data: tooltipData,
                        borderColor: 'rgba(0,0,0,0)',
                        backgroundColor: '#0060f0',
                        pointRadius: 5,
                        pointHoverRadius: 10,
                        showLine: false,
                    },
                    {
                        label: 'Elevation Profile',
                        data: profileData,
                        borderColor: '#96B578',
                        backgroundColor: '#e1f3ca',
                        borderWidth: 2,
                        fill: 'start',
                        pointRadius: 0,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'linear', // Linear scale for distance
                        title: {
                            display: true,
                            text: 'Distance (km)',
                            font: {
                                family: titleFont
                            },
                        },
                        ticks: {
                            maxTicksLimit: 10,
                        },
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Elevation (m)',
                            font: {
                                family: titleFont
                            },
                        },
                        ticks: {
                            maxTicksLimit: 5,
                        },
                    },
                },
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        displayColors: false,
                        bodyFont: {
                            family: bodyFont
                        },
                        titleFont: {
                            family: titleFont
                        },
                        callbacks: {
                            label: function (context) {
                                const xValue = context.raw.x.toFixed(1);
                                const yValue = context.raw.y.toFixed(0);
                                return [`Distance: ${xValue}km`, `Elevation: ${yValue}m`]; // replace with x/y labels
                            },
                            title: function (context) {
                                try {
                                    if (context[0].dataset.label === 'Leg Endpoints') {
                                        return context[0].raw.label;
                                    }
                                } catch { }
                                return '';
                            },
                        },
                    },
                },
                elements: {
                    line: {
                        tension: 0.2, // Smooth the line slightly
                    },
                },
            },
            plugins: [droplinesPlugin],
        });
    }

    getRouteLayerConfig = (geojson) => {
        return {
            id: `route-${this.mapSettings.uid}`,
            type: "line",
            metadata: { route: true },
            source: {
                type: "geojson",
                data: geojson,
            },
            layout: {
                "line-join": "round",
                "line-cap": "round",
            },
            paint: {
                "line-color": MapBlock.colours.route,
                "line-width": 5,
                "line-opacity": 0.75,
            },
        }
    }

    getEndpointLayerConfig = (id, waypoint, color) => {
        return {
            id: `${id}-${this.mapSettings.uid}`,
            type: "circle",
            metadata: { route: true },
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
                                    waypoint.longitude,
                                    waypoint.latitude,
                                ],
                            },
                        },
                    ],
                },
            },
            paint: {
                "circle-radius": 10,
                "circle-color": color,
            },
        };
    }

    // get initial bounding box from points array
    // IN: [[lng, lat], [lng, lat] ...]
    // OUT: bounds object
    findInitialBounds = (points) => {
        const { swX, neX, swY, neY } = points.reduce(
            (acc, [x, y]) => ({
                swX: Math.min(acc.swX, x),
                neX: Math.max(acc.neX, x),
                swY: Math.min(acc.swY, y),
                neY: Math.max(acc.neY, y),
            }),
            { swX: Infinity, neX: -Infinity, swY: Infinity, neY: -Infinity }
        );
        return new mapboxgl.LngLatBounds([[swX, swY], [neX, neY]])
    }

    fitBoundsToContainer = (screenBounds) => {
        // Get the map's container dimensions
        const effectiveMapWidth = this.mapContainer.offsetWidth - this.absolutePadding.left - this.absolutePadding.right;
        const effectiveMapHeight = this.mapContainer.offsetHeight - this.absolutePadding.top - this.absolutePadding.bottom;

        let offset = null;
        if (
            (this.absolutePadding.left !== this.absolutePadding.right) ||
            (this.absolutePadding.top !== this.absolutePadding.bottom)
        ) {
            offset = [
                this.absolutePadding.right - this.absolutePadding.left,
                this.absolutePadding.bottom - this.absolutePadding.top
            ];
        }

        const finaliseMap = () => {
            const bl = this.map.project(screenBounds.geo.vertices.bottomLeft);
            const br = this.map.project(screenBounds.geo.vertices.bottomRight);
            if (br.x - bl.x > effectiveMapWidth) {
                this.map.easeTo({ zoom: this.map.getZoom() - 0.1 });
                this.map.once('moveend', () => {
                    finaliseMap();
                });
            } else {
                if (offset) this.map.panBy(offset);
            }
        }

        this.map.easeTo({
            center: screenBounds.geo.bounds.getCenter(),
            pitch: this.mapSettings.pitch
        });
        this.map.once('moveend', () => {
            const tl = this.map.project(screenBounds.geo.vertices.topLeft);
            const tr = this.map.project(screenBounds.geo.vertices.topRight);
            const bl = this.map.project(screenBounds.geo.vertices.bottomLeft);
            const br = this.map.project(screenBounds.geo.vertices.bottomRight);
            const boundsWidth = br.x - bl.x;
            const boundsHeight = bl.y - tl.y;
            let scale = 1;
            const mapAspectRatio = effectiveMapWidth / effectiveMapHeight;
            const boundsAspectRatio = boundsWidth / boundsHeight;
            if (mapAspectRatio > boundsAspectRatio) {
                scale = effectiveMapHeight / boundsHeight;
            } else {
                scale = effectiveMapWidth / boundsWidth;
            }

            const zoomAdjustment = Math.log2(scale);
            const optimalZoom = this.map.getZoom() + zoomAdjustment;
            this.map.easeTo({
                zoom: optimalZoom
            });
            this.map.once('moveend', () => {
                finaliseMap();
            });
        });
    }

}

class ScreenBounds {
    constructor(map, points, debug = false) {
        this.map = map.stop();
        this.getScreenBounds(points);
        if (debug) this.drawBounds();
    }

    getScreenBounds = (points) => {
        // Use to calculate min/max x/y values in screen space
        const { minX, maxX, minY, maxY } = points.reduce(
            (acc, point) => {
                const screenPos = this.map.project([point[0], point[1]]);
                return {
                    minX: Math.min(acc.minX, screenPos.x),
                    maxX: Math.max(acc.maxX, screenPos.x),
                    minY: Math.min(acc.minY, screenPos.y),
                    maxY: Math.max(acc.maxY, screenPos.y),
                };
            },
            { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity }
        );
        // attributes in the screen space
        this.screen = {
            minX: minX, maxX: maxX, minY: minY, maxY: maxY,
            vertices: {
                topLeft: [minX, minY],
                topRight: [maxX, minY],
                bottomLeft: [minX, maxY],
                bottomRight: [maxX, maxY]
            },
            center: [(minX + maxX) / 2, (minY + maxY) / 2]
        };
        // geo coordinates for the screen values
        this.geo = {
            vertices: {
                topLeft: this.map.unproject(this.screen.vertices.topLeft),
                topRight: this.map.unproject(this.screen.vertices.topRight),
                bottomRight: this.map.unproject(this.screen.vertices.bottomRight),
                bottomLeft: this.map.unproject(this.screen.vertices.bottomLeft)
            },
        }
        // geo bounding box MapBox object
        this.geo.bounds = new mapboxgl.LngLatBounds([
            this.geo.vertices.bottomLeft,
            this.geo.vertices.topRight
        ])
    }

    drawBounds = () => {
        const quadGeoJSON = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            this.geo.vertices.topLeft.toArray(),
                            this.geo.vertices.topRight.toArray(),
                            this.geo.vertices.bottomRight.toArray(),
                            this.geo.vertices.bottomLeft.toArray(),
                            this.geo.vertices.topLeft.toArray()
                        ]
                    }
                }
            ]
        };
        this.map.addSource('screenBounds-box', {
            "type": "geojson",
            "data": quadGeoJSON
        });
        this.map.addLayer({
            "id": "screenBounds-box-layer",
            "type": "line",
            "source": "screenBounds-box",
            "layout": {
                "line-join": "round",
                "line-cap": "round"
            },
            "paint": {
                "line-color": "#ff0000",
                "line-width": 4
            }
        });
    }

}

class MapFeature {
    constructor(map, featureLayers) {
        this.features = new Features();
        this.map = map;
        this.featureLayers = featureLayers;
    }

    async showFeatureInfo(mapClickEvent) {
        // Check if the clicked element is a marker
        const clickedElement = mapClickEvent.originalEvent.target;
        // Don't show additional popup if marker is clicked
        const isMarker = clickedElement.closest('div.mapboxgl-marker');
        if (isMarker) {
            return;
        }

        const features = this.map.queryRenderedFeatures(mapClickEvent.point, { layers: this.featureLayers });
        // show feature info in an offcanvas if a feature is clicked
        if (features.length) {
            const feature = JSON.parse(JSON.stringify(features[0]), (_, v) => {
                try { return JSON.parse(v); } catch { return v; }
            });
            console.log(features[0])
            console.log(feature)
            if (feature.layer.type === 'symbol') {
                this.showSymbolInfo(feature);
                return;
            } else if (feature.layer.type === 'line') {
                this.showTrackInfo(feature);
                return;
            }
        }
        // show coordinates in a popup if no feature is clicked
        const coordinateshtml = await this.getCoordinatesHTML(mapClickEvent.lngLat);
        new mapboxgl.Popup()
            .setLngLat(mapClickEvent.lngLat)
            .setHTML(coordinateshtml)
            .addTo(this.map);
    }

    showSymbolInfo = async (feature) => {
        // Show feature info in an offcanvas
        const coordinateshtml = await this.getCoordinatesHTML(feature.geometry.coordinates);
        let html = `<div class="offcanvas-header">`;
        html += `<h4 class="feature-name">${feature.properties.name}</h4>`
        html += `<button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>`;
        html += `<div>${feature.properties.locationString ?? feature.properties.place ?? ''}</div>`;
        html += `</div><div class="offcanvas-body">`;
        if (feature.properties.region) {
            const facilityIcons = this.features.icons(feature.properties.facilities, 'facilities');
            if (feature.properties.introductionThumbnail && !feature.properties.introductionThumbnail.includes('no-photo'))
                html += `<p><img src="${feature.properties.introductionThumbnail.replace('large', 'hero')}" alt="${feature.properties.name}" onerror="this.parentElement.remove();"></p>`;
            html += `<p>${feature.properties.introduction}</p>`;
            html += `<div id="feature-alerts"></div>`;
            // Get feature alerts
            this.getFeatureAlerts(feature);
            if (feature.layer.id === 'doc-huts') {
                html += `<div class="features-icons facilities-icons">`;
                html += `<svg class="features-icon" aria-labelledby="capacity-title" role="img"><title id="capacity-title">Capacity</title>
                                    <use href="#bunk-bed"></use></svg><span>${parseFloat(feature.properties.numberOfBunks)}</span>`;
                html += `${facilityIcons}</div>`;
                html += `<div class="row align-items-center">
                                    <div class="col-auto features-icons"><svg class="features-icon" aria-labelledby="bookings-title" role="img"><title id="bookings-title">Bookings</title>
                                        <use href="#bookings"></use></svg></div>
                                    <div class="col"><span>Bookings ${feature.properties.bookable ? "" : "not "}required</span></div>
                                </div>`;
                html += `<div class="row align-items-center">
                                <div class="col-auto features-icons"><svg class="features-icon" aria-labelledby="gps-title" role="img"><title id="gps-title">GPS Location</title>
                                    <use href="#gps"></use></svg></div>
                                <div class="col gps-coordinates"><span>${coordinateshtml}</span></div>
                            </div>`;
            } else if (feature.layer.id === 'doc-campsites') {
                html += `<p><span class="fw-semibold">Category:</span> ${feature.properties.campsiteCategory}</p>`;
                html += `<div class="features-icons facilities-icons">`
                if (!!feature.properties.numberOfPoweredSites)
                    html += `<svg class="features-icon" aria-labelledby="powered-site-title" role="img"><title id="powered-site-title">Powered Sites</title>
                                    <use href="#powered-site"></use></svg><span>${feature.properties.numberOfPoweredSites}</span>`;
                html += `<svg class="features-icon" aria-labelledby="unpowered-site-title" role="img"><title id="unpowered-site-title">Unpowered Sites</title>
                                    <use href="#unpowered-site"></use></svg><span>${feature.properties.numberOfUnpoweredSites}</span>`;
                html += `${facilityIcons}</div>`;
                html += `<table class="table table-sm table-borderless align-middle"><tbody>`;
                if (feature.properties.access.length)
                    html += `<tr><th scope="row">Access:</th><td class="features-icons">${this.features.icons(feature.properties.access, 'access')}</td></tr>`;
                if (feature.properties.landscape.length)
                    html += `<tr><th scope="row">Landscape:</th><td class="features-icons">${this.features.icons(feature.properties.landscape, 'landscape')}</td></tr>`;
                if (feature.properties.activities.length)
                    html += `<tr><th scope="row">Activities:</th><td class="features-icons">${this.features.icons(feature.properties.activities, 'activities')}</td></tr>`;
                html += `</tbody></table>`;
                html += `<div class="row align-items-center">
                                    <div class="col-auto features-icons"><svg class="features-icon" aria-labelledby="bookings-title" role="img"><title id="bookings-title">Bookings</title>
                                        <use href="#bookings"></use></svg></div>
                                    <div class="col"><span>Bookings ${feature.properties.bookable ? "" : "not "}required</span></div>
                                </div>`;
                if (feature.properties.dogsAllowed)
                    html += `<div class="row align-items-center">
                                <div class="col-auto features-icons">${this.features.icons([feature.properties.dogsAllowed], 'dogsAllowed')}</div>
                                <div class="col dog-info">${feature.properties.dogsAllowed}</div>
                                </div>`;
                html += `<div class="row align-items-center">
                                    <div class="col-auto features-icons"><svg class="features-icon" aria-labelledby="gps-title" role="img"><title id="gps-title">GPS Location</title>
                                        <use href="#gps"></use></svg></div>
                                    <div class="col gps-coordinates"><span>${coordinateshtml}</span></div>
                                </div>`;
            }
        } else {
            html += this.warningAlert("DOC does not provide specific details for this facility.");
            html += `<p class="mt-3">See DOC's website for more information.</p>`;
            feature.properties.staticLink = `https://www.doc.govt.nz/search-results/?query=${encodeURIComponent(feature.properties.name)}`;
        }

        html += `<p class="more-information">
                    <a href="${feature.properties.staticLink}" target="_blank">More Information</a>
                    <svg><use href="#feature-open_external"></use></svg>
                </p>`;
        html += `</div>`;
        this.offcanvasElement = document.createElement('div');
        this.offcanvasElement.classList.add('offcanvas', 'offcanvas-start', 'map-block-feature');
        this.offcanvasElement.tabIndex = -1;
        this.offcanvasElement.innerHTML = html;

        // Append to body
        this.map.getContainer().appendChild(this.offcanvasElement);

        // Initialize and show the offcanvas
        const bsOffcanvas = new bootstrap.Offcanvas(this.offcanvasElement);
        bsOffcanvas.show();

        // Event listener to remove the offcanvas element after hiding
        this.offcanvasElement.addEventListener('hidden.bs.offcanvas', () => {
            this.offcanvasElement.remove();
        });
    }

    showTrackInfo = async (feature) => {
        // Show track info in an offcanvas
        let html = `<div class="offcanvas-header">`;
        if (feature.layer.id === 'doc-tracks-eam-clickable') {
            // EAM tracks - limited information
            // CharValue3: "WEB_CATEGORY_TRACK"
            // CharValue4: "WEB_WALKING_DURATION"
            // CharValue6: "WEB_DOGS_ALLOWED"
            // CharValue7: "WEB_TRACK_TYPE" (one way, loop etc)\
            // CharValue9: "WEB_MTB_CATEGORY"

            html += `<h4 class="feature-name">${feature.properties.TechObjectName}</h4>`;
            html += `<button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>`;
            html += `</div><div class="offcanvas-body">`;
            if (feature.properties.SubObjectType)
                html += `<div><span>Track Grade: ${feature.properties.SubObjectType}</span></div>`;
            html += this.warningAlert("DOC does not provide detailed information for this track.");
            if (feature.properties.CharValue4)
                html += `<div class="row align-items-center">
                    <div class="col-auto features-icons"><svg class="features-icon" aria-labelledby="bookings-title" role="img"><title id="bookings-title">Bookings</title>
                        <use href="#hiking"></use></svg></div>
                    <div class="col">
                    <span>${feature.properties.CharValue4}
                    ${feature.properties.CharValue7 ? " (" + feature.properties.CharValue7 + ")" : ""}</span>
                    </div>
                </div>`;
            if (feature.properties.CharValue9)
                html += `<div class="row align-items-center">
                    <div class="col-auto features-icons"><svg class="features-icon" aria-labelledby="bookings-title" role="img"><title id="bookings-title">Bookings</title>
                        <use href="#mountain-biking"></use></svg></div>
                    <div class="col"><span>${feature.properties.CharValue9}
                    ${feature.properties.CharValue7 ? " (" + feature.properties.CharValue7 + ")" : ""}</span></div>
                </div>`;
            if (feature.properties.CharValue6 && feature.properties.CharValue6 !== 'Not Applicable')
                html += `<div class="row align-items-center">
                            <div class="col-auto features-icons">${this.features.icons([feature.properties.CharValue6], 'dogsAllowed')}</div>
                            <div class="col dog-info">${feature.properties.CharValue6}</div>
                        </div>`;
            feature.properties.staticLink = `https://www.doc.govt.nz/parks-and-recreation/know-before-you-go/alerts/`;
            html += `<p class="more-information">
                        <a href="${feature.properties.staticLink}" target="_blank">DOC Alerts by Region</a>
                        <svg><use href="#feature-open_external"></use></svg>
                    </p>`;
            html += `</div>`;
        } else if (feature.layer.id === 'doc-tracks-api-clickable') {
            // API tracks - more detailed information
            if (feature.properties.wheelchairsAndBuggies) {
                feature.properties.permittedActivities.push("Suitable for wheelchairs. Assistance my be required.")
                feature.properties.permittedActivities.push("Suitable for buggies.")
            }
            html += `<h4 class="feature-name">${feature.properties.name}</h4>`;
            html += `<button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>`;
            html += `<div>${feature.properties.region.join(', ')}</div>`;
            html += `</div><div class="offcanvas-body">`;
            if (feature.properties.introductionThumbnail && !feature.properties.introductionThumbnail.includes('no-photo'))
                html += `<p><img src="${feature.properties.introductionThumbnail.replace('large', 'hero')}" alt="${feature.properties.name}" onerror="this.parentElement.remove();"></p>`;
            html += `<p>${feature.properties.introduction}</p>`;
            html += `<div id="feature-alerts"></div>`;
            // Get feature alerts
            this.getFeatureAlerts(feature);
            if (feature.properties.permittedActivities.length)
                html += `<div class="row align-items-center">
                        <div class="col-auto features-icons"><span>Activities:</span></div>
                        <div class="col features-icons">${this.features.icons(feature.properties.permittedActivities, 'activities')}</div>
                        </div>`;
            if (feature.properties.distance)
                html += `<div><p><span>Length: ${feature.properties.distance}</span></p></div>`;
            if (feature.properties.walkTrackCategory.length) {
                html += `<div class="row align-items-center">
                        <div class="col-auto features-icons">${this.features.icons(['Walking and tramping'], 'activities')}</div>
                        <div class="col">
                        Grade: ${feature.properties.walkTrackCategory.join(', ')}`
                if (feature.properties.walkDuration)
                    html += `<br>Duration: ${feature.properties.walkDuration}`
                html += `</div></div>`;
            }
            if (feature.properties.mtbTrackCategory.length) {
                html += `<div class="row align-items-center">
                        <div class="col-auto features-icons">${this.features.icons(['Mountain biking'], 'activities')}</div>
                        <div class="col">
                        Grade: ${feature.properties.mtbTrackCategory.join(', ')}`
                if (feature.properties.mtbDuration)
                    html += `<br>Duration: ${feature.properties.mtbDuration}`
                html += `</div></div>`;
            }
            if (feature.properties.kayakingDuration)
                html += `<div class="row align-items-center">
                        <div class="col-auto features-icons">${this.features.icons(['Kayaking and canoeing'], 'activities')}</div>
                        <div class="col">
                        Duration: ${feature.properties.kayakingDuration}
                        </div>
                    </div>`;
            if (feature.properties.dogsAllowed)
                html += `<div class="row align-items-center">
                        <div class="col-auto features-icons">${this.features.icons([feature.properties.dogsAllowed], 'dogsAllowed')}</div>
                        <div class="col dog-info">${feature.properties.dogsAllowed}</div>
                    </div>`;
            html += `<p class="more-information">
                        <a href="${feature.properties.staticLink}" target="_blank">More Information</a>
                        <svg><use href="#feature-open_external"></use></svg>
                    </p>`;
            html += `</div>`;
        }

        html += `</div>`;
        this.offcanvasElement = document.createElement('div');
        this.offcanvasElement.classList.add('offcanvas', 'offcanvas-start', 'map-block-feature');
        this.offcanvasElement.tabIndex = -1;
        this.offcanvasElement.innerHTML = html;

        // Append to body
        this.map.getContainer().appendChild(this.offcanvasElement);

        // Initialize and show the offcanvas
        const bsOffcanvas = new bootstrap.Offcanvas(this.offcanvasElement);
        bsOffcanvas.show();

        // Event listener to remove the offcanvas element after hiding
        this.offcanvasElement.addEventListener('hidden.bs.offcanvas', () => {
            this.offcanvasElement.remove();
        });
    }

    warningAlert = (message) => {
        return `<div class="alert alert-warning" role="alert">
                <svg><use href="#warning-triangle"></use></svg>
                <p>
                    <span>${message}</span>
                </p>
            </div>`
    }

    getCoordinatesHTML = async (coordinates) => {
        const elevation = await this.map.queryTerrainElevation(coordinates, { exaggerated: false });
        let coordinatesString = coordinates instanceof mapboxgl.LngLat ? coordinates.toArray() : coordinates;
        coordinatesString = `${coordinatesString[1].toFixed(5)},${coordinatesString[0].toFixed(5)}`; // convert to lat,lng string
        let coordinateshtml = `<div class="map-block-coordinates">`;
        coordinateshtml += `<a href="https://www.google.com/maps?q=${coordinatesString}" title="Open in Google Maps"
                            target="_blank" class="map-block-waypoint-link">${coordinatesString.replace(',', ', ')}</a> `;
        coordinateshtml += `<a class="map-block-waypoint-link" title="Copy to Clipboard" onclick="navigator.clipboard.writeText('${coordinatesString}')">
                            <svg><use href="#feature-clipboard"></use></svg></a>`;
        if (elevation) coordinateshtml += `<br>${Math.round(elevation)}m a.s.l <i><small>(estimated)</small></i>`;
        coordinateshtml += `</div>`;
        return coordinateshtml;
    }


    async getFeatureAlerts(feature) {
        const xapiKey = "Cns0yYhKHZ1Zgq7Y8v4rw5mYWO3kwxJI1Q7dcuqR"
        let url, html = '';
        switch (feature.layer.id) {
            case 'doc-huts':
                url = `https://api.doc.govt.nz/v2/huts/${feature.properties.assetId}/alerts`;
                break;
            case 'doc-campsites':
                url = `https://api.doc.govt.nz/v2/campsites/${feature.properties.assetId}/alerts`;
                break;
        }
        if (url) {
            const response = await fetch(url, {
                headers: {
                    'x-api-key': xapiKey
                }
            });
            const responseJSON = await response.json();
            if (responseJSON.length) {
                const alertsContainer = this.offcanvasElement.querySelector('#feature-alerts');
                const alerts = responseJSON[0].alerts;
                html = `<div class="accordion mb-3" id="feature-alerts-accordion">`;
                alerts.forEach((alert, index) => {
                    html += `<div class="accordion-item">
                            <div class="accordion-header" id="heading-${index}">
                                <button class="accordion-button text-bg-danger collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${index}" aria-expanded="false" aria-controls="collapse-${index}">
                                    ${alert.heading}
                                </button>
                            </div>
                            <div id="collapse-${index}" class="accordion-collapse collapse" aria-labelledby="heading-${index}" data-bs-parent="#feature-alerts-accordion">
                                <div class="accordion-body">
                                    ${alert.detail}
                                </div>
                            </div>
                        </div>`;
                });
                html += `</div>`;
                alertsContainer.innerHTML = html;
            }
        }
    }
}

class Features {
    static mappings = {
        facilities: {
            'BBQ': 'bbq',
            'Boat launching': 'boat-launch',
            'Cookers/electric stove': 'cooking',
            'Cooking': 'cooking',
            'Dump station': 'dump-station',
            'Fire pit/place for campfires (except in fire bans)': 'fire-pit',
            'Heating': 'heating',
            'Jetty': 'jetty',
            'Lighting': 'lighting',
            'Mattresses': 'mattresses',
            'Phone': 'phone',
            'Shelter for cooking': 'cooking-shelter',
            'Shop': 'shop',
            'Shower - cold': 'shower-cold',
            'Shower - hot': 'shower-hot',
            'Toilets - flush': 'toilets-flush',
            'Toilets - non-flush': 'toilets-non-flush',
            'Water from stream': 'water-stream',
            'Water from tap - not treated': 'water-tap-untreated',
            'Water from tap - not treated: boil before use': 'water-tap-untreated',
            'Water from tap - treated': 'water-tap-treated',
            'Wheelchair accessible with assistance': 'accessible-assistance',
            'Wheelchair accessible': 'accessible'
        },
        landscape: {
            'Alpine': 'alpine',
            'Coastal': 'coastal',
            'Forest': 'forest',
            'Rivers and lakes': 'rivers-lakes'
        },
        access: {
            '4WD': 'four-wheel-driving',
            'Boat': 'boat',
            'Campervan': 'campervan',
            'Caravan': 'caravan',
            'Car': 'car',
            'Foot': 'hiking',
            'Mountain bike': 'mountain-biking'
        },
        activities: {
            'Bird and wildlife watching': 'binoculars',
            'Boating': 'boat',
            'Caving': 'caving',
            'Climbing': 'climbing',
            'Diving and snorkelling': 'diving',
            'Fishing': 'fishing',
            'Four wheel driving': 'four-wheel-driving',
            'Horse riding': 'horse-riding',
            'Hunting': 'hunting',
            'Kayaking and canoeing': 'kayaking',
            'Mountain biking': 'mountain-biking',
            'Picnicking': 'picnic',
            'Quad and trail biking': 'quading',
            'Rafting': 'rafting',
            'Scenic driving': 'scenic-driving',
            'Suitable for wheelchairs': 'accessible-assistance',
            'Suitable for buggies': 'buggy',
            'Skiing and ski touring': 'skiing',
            'Swimming': 'swimming',
            'Walking and tramping': 'hiking'
        },
        dogsAllowed: {
            'No dogs': 'no-dogs',
            'No Dogs': 'no-dogs',
            'Dogs on a leash only': 'dogs-on-leash',
            'Dogs on a leash only,Dogs allowed - under control': 'dogs-on-leash',
            'No Dogs,Dogs on a leash only': 'dogs-on-leash',
            'Dogs allowed': 'dogs-allowed',
            'Dogs allowed - under control': 'dogs-allowed',
            'Dogs with a DOC permit only': 'dogs-permit',
            'Dogs with DOC permit -hunting': 'dogs-permit',
            'No Dogs,Dogs with DOC permit -hunting': 'dogs-permit',
            'Dogs with a DOC permit for recreational hunting or management purposes only': 'dogs-permit'
        }
    }

    constructor() {
        this.loadSpriteSheet();
    }

    /**
     * Generates HTML for feature icons based on the features and type passed.
     * @returns {string} HTML string containing SVG icons for each feature.
     */
    icons(featureArray, type) {
        try {
            const featureMap = Features.mappings[type];
            const features = typeof featureArray === 'string' ?
                JSON.parse(featureArray) :
                featureArray;
            if (features.length && featureMap) {
                const iconHtml = features
                    .map(feature => {
                        const featureKey = Object.keys(featureMap).find(key => feature.split('.')[0].trim() === key);
                        const featureSlug = featureMap[featureKey];
                        return featureSlug ? `<svg class="features-icon" aria-labelledby="${featureSlug}-title">
                           <title id="${featureSlug}-title">${feature}</title>
                           <use href="#${featureSlug}"></use>
                           </svg>`
                            : '';
                    })
                    .filter(html => html) // Remove empty strings
                    .join('');
                return iconHtml ?? '';
            }
        } catch (error) { }
        return '';
    }

    loadSpriteSheet = async () => {
        if (!document.getElementById('features-icons')) {
            fetch('/static/icons/features.svg')
                .then(response => response.text())  // Get the SVG content as text
                .then(svg => {
                    const div = document.createElement('div');
                    div.style.display = 'none'; // Hide the SVG sprite sheet from the UI
                    div.id = 'features-icons';  // Set an ID for the sprite sheet
                    div.innerHTML = svg;  // Insert the SVG content into the div
                    document.body.appendChild(div);  // Append the div to the body (or any other element)
                })
                .catch(error => console.error('Error loading sprite sheet:', error));
        }
    }

}