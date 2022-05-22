window.myNamespace = Object.assign({}, window.myNamespace, {  
    mySubNamespace: {  
        color_polys: function(feature, context) {
            const {
                classes,
                colorscale,
                style,
                colorProp
            } = context.props.hideout; // get props from hideout
            const value = feature.properties[colorProp]; // get value the determines the color
            for (let i = 0; i < classes.length; ++i) {
                if (value > classes[i]) {
                    style.fillColor = colorscale[i]; // set the fill color according to the class
                    style.color = colorscale[i]; // set the border color according to the class
                }
            }
            return style;
        }
    }
});