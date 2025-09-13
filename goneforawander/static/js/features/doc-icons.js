export default class DocIcons {
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
    };

    static loadSpriteSheet = async () => {
        const spriteID = 'doc-feature-icons'
        if (!document.getElementById(spriteID)) {
            fetch('/static/icons/doc-features.svg')
                .then(response => response.text()) // Get the SVG content as text
                .then(svg => {
                    const div = document.createElement('div');
                    div.style.display = 'none'; // Hide the SVG sprite sheet from the UI
                    div.id = spriteID; // Set an ID for the sprite sheet
                    div.innerHTML = svg; // Insert the SVG content into the div
                    document.body.appendChild(div); // Append the div to the body (or any other element)
                })
                .catch(error => console.error('Error loading sprite sheet:', error));
        }
    };

    constructor() {
        DocIcons.loadSpriteSheet();
    }

    /**
     * Generates HTML for feature icons based on the features and type passed.
     * @returns {string} HTML string containing SVG icons for each feature.
     */
    icons(featureArray, type) {
        try {
            const featureMap = DocIcons.mappings[type];
            const features = typeof featureArray === 'string' ?
                JSON.parse(featureArray) :
                featureArray;
            if (features.length && featureMap) {
                const iconHtml = features
                    .map(feature => {
                        const featureKey = Object.keys(featureMap).find(key => feature.split('.')[0].trim() === key);
                        const featureSlug = featureMap[featureKey];
                        return featureSlug ? `<svg class="doc-icon" aria-labelledby="${featureSlug}-title">
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
}
