import { BaseAccordion } from '../components/accordion.js';

const fetchFeatureAlerts = async (assetId, type) => {
    try {
        const xapiKey = window.env?.DOC_API_KEY;
        const response = await fetch(`https://api.doc.govt.nz/${type}/${assetId}/alerts`, {
            headers: {
                'x-api-key': xapiKey
            }
        });
        if (!response.ok) {
            throw new Error(`Failed to fetch alerts: ${response.statusText}`);
        }
        const responseJSON = await response.json();
        return Promise.resolve(responseJSON);
    } catch (error) {
        return Promise.reject(error);
    }
};

function wrapPublishedReviewedNote(alertBody) {
    const alertDetails = alertBody.querySelectorAll('div.base-accordion-body');
    if (!alertDetails) return;

    alertDetails.forEach(alertDetail => {
        const nodes = Array.from(alertDetail.childNodes);

        for (const node of nodes) {
            if (node.nodeType === Node.TEXT_NODE && node.textContent?.trim()) {
                const text = node.textContent.trim();
                const sentences = text.split('. ').map(s => s.trim()).filter(Boolean);

                const wrapper = document.createElement("div");
                wrapper.className = "doc-alert-dates";
                sentences.forEach((sentence, index) => {
                    wrapper.appendChild(document.createTextNode(sentence + (sentence.endsWith('.') ? '' : '.')));
                    if (index < sentences.length - 1) {
                        wrapper.appendChild(document.createElement("br"));
                    }
                });

                alertDetail.replaceChild(wrapper, node);
            }
        }
    });
};

export const renderFeatureAlerts = (alertsContainer, assetId, type) => {
    queueMicrotask(() => {
        fetchFeatureAlerts(assetId, type).then(responseJSON => {
            if (responseJSON.length) {
                const alerts = responseJSON[0].alerts;
                const alertBody = new BaseAccordion(alerts, 'doc-alert').element;
                wrapPublishedReviewedNote(alertBody);
                alertsContainer.appendChild(alertBody);
            }
        }).catch(error => {
            console.error('Error fetching alerts:', error);
        });
    });
};
