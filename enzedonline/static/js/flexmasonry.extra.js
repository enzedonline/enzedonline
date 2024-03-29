// code for the blog post masonry walls
const flexMasonryInit = () => {
    FlexMasonry.init(
        '.grid',
        {
            breakpointCols: {
                'min-width: 2000px': 5,
                'min-width: 1500px': 4,
                'min-width: 1000px': 3,
                'min-width: 500px': 2,
            }
        }
    );
}

// code for the masonry blocks called by blocks/simple_card_grid_block.html
// gridID - class used to call flexmasonry from the block - must be unique on the page
// optionsID - id from JSON script used to store options for the block
const initFlexMasonryBlock = (gridID, optionsID) => {
    const el = document.getElementsByClassName(gridID)[0];

    // Stop full container width element while flexmasonry loading
    el.style.display = "flex";

    resizeFlexMasonryBlock(gridID, optionsID);

    // Forced overflow error on hard refresh - call again 600ms after DOMContentLoaded
    window.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            resizeFlexMasonryBlock(gridID, optionsID);
        }, 600);
    });

    // Multiple classes on the same page not supported with flexmasonry.refresh() - call init on resize
    window.addEventListener('resize', () => {
        resizeFlexMasonryBlock(gridID, optionsID);
    });

    el.style.removeProperty("display");
}


const resizeFlexMasonryBlock = (gridID, optionsID) => {
    const options = JSON.parse(document.getElementById(optionsID).textContent);
    FlexMasonry.init(
        '.' + gridID,
        {
            responsive: true,
            breakpointCols: options.breakpointCols,
        }
    );
}