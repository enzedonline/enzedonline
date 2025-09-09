import DocIcons from "./doc-icons.js";
import { renderFeatureAlerts } from './doc-alerts.js'
import { renderCoordinatesDetails } from './coordinates-details.js'


const renderHutDetails = (feature) => {
    const docIcons = new DocIcons();
    const facilityIcons = docIcons.icons(feature.properties.facilities, 'facilities');
    let html = `<div class="doc-icons facilities-icons">`;
    html += `<svg class="doc-icon" aria-labelledby="capacity-title" role="img"><title id="capacity-title">Capacity</title>
                <use href="#bunk-bed"></use></svg><span>${parseFloat(feature.properties.numberOfBunks)}</span>`;
    html += `${facilityIcons}</div>`;
    html += `<div class="detail-row${feature.properties.bookable ? " doc-alert" : ""}">
                <div class="col-icon doc-icons"><svg class="doc-icon" aria-labelledby="bookings-title" role="img"><title id="bookings-title">Bookings</title>
                    <use href="#bookings"></use></svg></div>
                <div class="col-description">
                    <span class="doc-bookable">Bookings ${feature.properties.bookable ? "" : "not "}required.</span>
                    ${feature.properties.bookable ? `<br><span class="doc-bookable-extra">Visit the DOC website for more information (link below)</span>` : ""}
                </div>
            </div>`;
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    tempDiv.querySelectorAll('a').forEach(link => link.setAttribute('target', '_blank'));
    const featureDetails = document.createDocumentFragment();
    featureDetails.appendChild(tempDiv);
    return featureDetails;
}

const renderCampsiteDetails = (feature) => {
    const docIcons = new DocIcons();
    const facilityIcons = docIcons.icons(feature.properties.facilities, 'facilities');
    let html = `<p class="subheading"><span class="semibold">Category:</span> ${feature.properties.campsiteCategory}</p>`;
    html += `<div class="doc-icons facilities-icons">`
    if (!!feature.properties.numberOfPoweredSites)
        html += `<svg class="doc-icon" aria-labelledby="powered-site-title" role="img"><title id="powered-site-title">Powered Sites</title>
                        <use href="#powered-site"></use></svg><span>${feature.properties.numberOfPoweredSites}</span>`;
    html += `<svg class="doc-icon" aria-labelledby="unpowered-site-title" role="img"><title id="unpowered-site-title">Unpowered Sites</title>
                        <use href="#unpowered-site"></use></svg><span>${feature.properties.numberOfUnpoweredSites}</span>`;
    html += `${facilityIcons}</div>`;
    html += `<table><tbody>`;
    const accessIcons = docIcons.icons(feature.properties.access, 'access');
    if (accessIcons)
        html += `<tr><th scope="row" >Access:</th><td class="doc-icons">${accessIcons}</td></tr>`;
    const landscapeIcons = docIcons.icons(feature.properties.landscape, 'landscape');
    if (landscapeIcons)
        html += `<tr><th scope="row">Landscape:</th><td class="doc-icons">${landscapeIcons}</td></tr>`;
    const activityIcons = docIcons.icons(feature.properties.activities, 'activities');
    if (activityIcons)
        html += `<tr><th scope="row">Activities:</th><td class="doc-icons">${activityIcons}</td></tr>`;
    console.log('activities', feature.properties.activities)
    html += `</tbody></table>`;
    html += `<div class="detail-row${feature.properties.bookable ? " doc-alert" : ""}">
                <div class="col-icon doc-icons"><svg class="doc-icon" aria-labelledby="bookings-title" role="img"><title id="bookings-title">Bookings</title>
                    <use href="#bookings"></use></svg></div>
                <div class="col-description">
                    <span class="doc-bookable">Bookings ${feature.properties.bookable ? "" : "not "}required.</span>
                    ${feature.properties.bookable ? `<br><span class="doc-bookable-extra">Visit the DOC website for more information (link below)</span>` : ""}
                </div>
            </div>`;
    if (feature.properties.dogsAllowed)
        html += `<div class="detail-row">
                    <div class="col-icon doc-icons">${docIcons.icons([feature.properties.dogsAllowed], 'dogsAllowed')}</div>
                    <div class="col-description font-compact">${feature.properties.dogsAllowed}</div>
                </div>`;
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    tempDiv.querySelectorAll('a').forEach(link => link.setAttribute('target', '_blank'));
    const featureDetails = document.createDocumentFragment();
    featureDetails.appendChild(tempDiv);
    return featureDetails;
}

export async function docSymbolsHandler(feature, map) {
    const externalLink = feature.properties.staticLink ?? `https://www.doc.govt.nz/search-results/?query=${encodeURIComponent(feature.properties.name)}`;
    const content = document.createDocumentFragment();
    const offCanvasHeader = document.createElement('div');
    offCanvasHeader.className = "mapbox-assist--offcanvas-header";
    let html = `${feature.properties.name}`;
    html += `<div class="offcanvas-compact">${feature.properties.locationString ?? feature.properties.place ?? ''}</div>`;
    offCanvasHeader.innerHTML = html;
    content.append(offCanvasHeader);
    const offCanvasBody = document.createElement('div');
    offCanvasBody.className = "mapbox-assist--offcanvas-body";
    if (feature.properties.region) {
        const introduction = document.createElement('div');
        if (feature.properties.introductionThumbnail && !feature.properties.introductionThumbnail.includes('no-photo'))
            html = `<p style="text-align: center; min-height: 180px; margin-bottom: 0;">
                    <img width="100%" height="auto" src="${feature.properties.introductionThumbnail.replace('large', 'hero')}" 
                    alt="${feature.properties.name}" onerror="this.parentElement.remove();"></p>`;
        html += `<p>${feature.properties.introduction}</p>`;
        introduction.innerHTML = html;
        offCanvasBody.append(introduction);

        const alertsContainer = document.createElement('div');
        offCanvasBody.appendChild(alertsContainer);

        switch (feature.layer.id) {
            case 'doc-huts':
                renderFeatureAlerts(alertsContainer, feature.properties.assetId, 'v2/huts');
                offCanvasBody.append(renderHutDetails(feature));
                break;
            case 'doc-campsites':
                renderFeatureAlerts(alertsContainer, feature.properties.assetId, 'v2/campsites');
                offCanvasBody.append(renderCampsiteDetails(feature));
                break;
        }
    } else {
        DocIcons.loadSpriteSheet();
        offCanvasBody.insertAdjacentHTML(
            'beforeend', 
            `<div class="detail-row no-details-warning">
                <div class="col-icon doc-icons"><svg class="doc-icon"><use href="#warning-triangle"></use></svg></div>
                <div class="col-description">DOC does not provide specific details for this facility.</div>
                <div class="font-compact">See DOC's website for more information.</div>
            </div>`
        );
    }
    offCanvasBody.append(await renderCoordinatesDetails(map, feature.geometry.coordinates));
    offCanvasBody.insertAdjacentHTML(
        'beforeend', 
        `<div class="more-information">
            <a class="btn btn-primary" href="${externalLink}" target="_blank">Visit DOC Site
            <svg class="inline-icon"><use href="#feature-open_external"></use></svg>
            </a>
        </div>`
    );
    content.append(offCanvasBody);
    return Promise.resolve(content);
}