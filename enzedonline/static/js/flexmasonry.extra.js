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
