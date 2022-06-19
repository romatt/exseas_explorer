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
                if (value == classes[i]) {
                    style.fillColor = colorscale[i]; // set the fill color according to the class
                    style.color = colorscale[i]; // set the border color according to the class     
                }
            }
            return style;
        },
        bindPopup: function(feature, layer) {
            const props = feature.properties;
            delete props.cluster;
            const patch = JSON.stringify(props.Label);
            const year = JSON.stringify(props.Year);
            const area = parseFloat(JSON.stringify(props.area)).toFixed(2);
            const land_area = parseFloat(JSON.stringify(props.land_area)).toFixed(2);
            layer.bindPopup("Patch "+patch+"<br>Year: "+year+"<br>"+"Area: "+area+"km^2<br>"+"Land Area: "+land_area+"km^2");
        }
    }
});