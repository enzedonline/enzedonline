import DocIcons from "./doc-icons.js";
import { renderFeatureAlerts } from './doc-alerts.js'

const renderEAMTrackDetails = (feature) => {
    // EAM tracks - limited information
    const docIcons = new DocIcons();
    const content = document.createDocumentFragment();
    const offCanvasHeader = document.createElement('div');
    offCanvasHeader.className = "mapbox-assist--offcanvas-header";
    offCanvasHeader.textContent = feature.properties.name;
    content.append(offCanvasHeader);
    const offCanvasBody = document.createElement('div');
    offCanvasBody.className = "mapbox-assist--offcanvas-body";
    let html = "";
    if (feature.properties.SubObjectType)
        html += `<div class="subheading"><span class="semibold">Track Grade:</span> ${feature.properties.SubObjectType}</div>`;
    html += `<div class="detail-row no-details-warning">
                <div class="col-icon doc-icons"><svg class="doc-icon"><use href="#warning-triangle"></use></svg></div>
                <div class="col-description">DOC does not provide specific details for this track.</div>
                <div class="font-compact">See DOC's website for more information.</div>
            </div>`
    if (feature.properties.CharValue4)
        // CharValue4: "WEB_WALKING_DURATION"
        // CharValue7: "WEB_TRACK_TYPE" (one way, loop etc)
        html += `<div class="detail-row">
                    <div class="col-icon doc-icons"><svg class="doc-icon" aria-labelledby="duration-title" role="img"><title id="duration-title">Duration</title>
                        <use href="#hiking"></use></svg></div>
                    <div class="col-description">
                    ${feature.properties.CharValue4}
                    ${feature.properties.CharValue7 ? " (" + feature.properties.CharValue7 + ")" : ""}
                    </div>
                </div>`;
    if (feature.properties.CharValue9)
        // CharValue9: "WEB_MTB_CATEGORY"
        html += `<div class="detail-row">
                    <div class="col-icon doc-icons"><svg class="doc-icon" aria-labelledby="mtb-category-title" role="img"><title id=""mtb-category-title">Mountain Bike Category</title>
                        <use href="#mountain-biking"></use></svg></div>
                    <div class="col-description">
                    ${feature.properties.CharValue9}
                    ${feature.properties.CharValue7 ? " (" + feature.properties.CharValue7 + ")" : ""}
                    </div>
                </div>`;
    if (feature.properties.CharValue6 && feature.properties.CharValue6 !== 'Not Applicable')
        // CharValue6: "WEB_DOGS_ALLOWED"
        html += `<div class="detail-row">
                    <div class="col-icon doc-icons">${docIcons.icons([feature.properties.CharValue6], 'dogsAllowed')}</div>
                    <div class="col-description">${feature.properties.CharValue6}</div>
                </div>`;
    const { link, description} = feature.properties.staticLink ?
            {
                link: feature.properties.staticLink,
                description: 'Visit DOC Site'
            } :
            {
                link: `https://www.doc.govt.nz/parks-and-recreation/know-before-you-go/alerts/`,
                description: 'DOC Alerts by Region'
            };
    html += `<div class="more-information">
                <a class="btn btn-primary" href="${link}">${description}
                <svg class="inline-icon"><use href="#feature-open_external"></use></svg>
                </a>
            </div>`;
    offCanvasBody.innerHTML = html;
    offCanvasBody.querySelectorAll('a').forEach(link => link.setAttribute('target', '_blank'));
    content.append(offCanvasBody);
    return content;
}

const renderAPITrackDetails = (feature) => {
    const docIcons = new DocIcons();
    const content = document.createDocumentFragment();
    const offCanvasHeader = document.createElement('div');
    offCanvasHeader.className = "mapbox-assist--offcanvas-header";
    offCanvasHeader.textContent = feature.properties.name;
    offCanvasHeader.insertAdjacentHTML(
        'beforeend', 
        `<div class="offcanvas-compact">${feature.properties.region.join(', ')}</div>`
    );
    content.append(offCanvasHeader);
    const offCanvasBody = document.createElement('div');
    offCanvasBody.className = "mapbox-assist--offcanvas-body";
    const introduction = document.createElement('div');
    let html = "";
    if (feature.properties.introductionThumbnail && !feature.properties.introductionThumbnail.includes('no-photo'))
        html = `<p style="text-align: center; min-height: 180px; margin-bottom: 0;">
                <img width="100%" height="auto" src="${feature.properties.introductionThumbnail.replace('large', 'hero')}" 
                alt="${feature.properties.name}" onerror="this.parentElement.remove();"></p>`;
    html += `<p>${feature.properties.introduction}</p>`;
    introduction.innerHTML = html;
    offCanvasBody.append(introduction);
    const alertsContainer = document.createElement('div');
    offCanvasBody.appendChild(alertsContainer);
    // renderFeatureAlerts(alertsContainer, feature.properties.assetId, 'v1/tracks');
    if (feature.properties.wheelchairsAndBuggies) {
        feature.properties.permittedActivities.push("Suitable for wheelchairs. Assistance my be required.")
        feature.properties.permittedActivities.push("Suitable for buggies.")
    }
    html = "";
    if (feature.properties.permittedActivities?.length)
        html += `<div class="detail-row">
                <div class="col-icon doc-icons subheading semibold">Activities:</div>
                <div class="col doc-icons">${docIcons.icons(feature.properties.permittedActivities, 'activities')}</div>
            </div>`;
    if (feature.properties.distance)
        html += `<div class="track-distance"><span class="semibold">Length:</span> ${feature.properties.distance}</div>`;
    if (feature.properties.walkTrackCategory?.length) {
        html += `<div class="detail-row">
            <div class="col-icon doc-icons">${docIcons.icons(['Walking and tramping'], 'activities')}</div>
            <div class="col-description">
            <span class="semibold">Grade:</span> ${feature.properties.walkTrackCategory.join(', ')}`
        if (feature.properties.walkDuration)
            html += `<br><span class="semibold">Duration:</span> ${feature.properties.walkDuration}`
        html += `</div></div>`;
    }
    if (feature.properties.mtbTrackCategory?.length) {
        html += `<div class="detail-row">
                <div class="col-icon doc-icons">${docIcons.icons(['Mountain biking'], 'activities')}</div>
                <div class="col-description">
                <span class="semibold">Grade:</span> ${feature.properties.mtbTrackCategory.join(', ')}`
        if (feature.properties.mtbDuration)
            html += `<br><span class="semibold">Duration:</span> ${feature.properties.mtbDuration}`
        html += `</div></div>`;
    }
    if (feature.properties.kayakingDuration)
        html += `<div class="detail-row">
                    <div class="col-icon doc-icons">${docIcons.icons(['Kayaking and canoeing'], 'activities')}</div>
                    <div class="col-description">
                    <span class="semibold">Duration:</span> ${feature.properties.kayakingDuration}
                    </div>
                </div>`;
    if (feature.properties.dogsAllowed)
        html += `<div class="detail-row">
                    <div class="col-icon doc-icons">${docIcons.icons([feature.properties.dogsAllowed], 'dogsAllowed')}</div>
                    <div class="col-description font-compact">${feature.properties.dogsAllowed}</div>
                </div>`;
    if (feature.properties.staticLink)
        html += `<div class="more-information">
                    <a class="btn btn-primary" href="${feature.properties.staticLink}">Visit DOC Site
                    <svg class="inline-icon"><use href="#feature-open_external"></use></svg>
                    </a>
                </div>`
    offCanvasBody.insertAdjacentHTML('beforeend', html);
    offCanvasBody.querySelectorAll('a').forEach(link => link.setAttribute('target', '_blank'));
    content.append(offCanvasBody);
    return content;
}

export async function docTracksHandler(feature, map) {
    switch (feature.layer.id) {
        case 'doc-tracks-eam-clickable':
            return renderEAMTrackDetails(feature);
        case 'doc-tracks-api-clickable':
            return renderAPITrackDetails(feature);
    }
}
