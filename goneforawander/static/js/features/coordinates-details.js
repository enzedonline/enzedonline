import mapboxgl from 'mapbox-gl';

export const renderCoordinatesDetails = async (map, coordinates) => {
    let elevation;
    try {
        elevation = await map.queryTerrainElevation(coordinates, { exaggerated: false });
    } catch { }
    let coordinatesString = coordinates instanceof mapboxgl.LngLat ? coordinates.toArray() : coordinates;
    coordinatesString = `${coordinatesString[1].toFixed(5)},${coordinatesString[0].toFixed(5)}`; // convert to lat,lng string
    let details = `<a href="https://www.google.com/maps?q=${coordinatesString}" title="Open in Google Maps"
                        target="_blank">${coordinatesString.replace(',', ', ')}</a> `;
    details += `<a class="clipboard-link" title="Copy to Clipboard" onclick="navigator.clipboard.writeText('${coordinatesString}')">
                        <svg class="inline-icon"><use href="#feature-clipboard"></use></svg></a>`;
    if (elevation) details += `<br><span class="offcanvas-compact">${elevation.toFixed(0)}m a.s.l <i>(estimated)</i></span>`;
    const html = `<div class="detail-row">
                    <div class="col-icon doc-icons"><svg class="doc-icon" aria-labelledby="coordinates-title" role="img"><title id="coordinates-title">Coordinates</title>
                        <use href="#gps"></use></svg></div>
                    <div class="col-description">${details}</div>
                </div>`;
    const coordinatesFragment = document.createDocumentFragment();
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    coordinatesFragment.appendChild(tempDiv.firstChild);
    return coordinatesFragment;
}