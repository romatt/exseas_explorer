window.myNamespace = Object.assign({}, window.myNamespace, {
    mySubNamespace: {
        color_polys: function (feature, context) {
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
        bindPopup: function (feature, layer, context) {
            const { parameter } = context.props.hideout;
            const props = feature.properties;
            delete props.cluster;
            const patch = JSON.stringify(props.Label);
            const year = JSON.stringify(props.Year);
            const area = parseFloat(JSON.stringify(props.area)).toFixed(2);
            const land_area = parseFloat(JSON.stringify(props.land_area)).toFixed(2);
            const mean_ano = parseFloat(JSON.stringify(props.mean_ano)).toFixed(2);
            const land_mean_ano = parseFloat(JSON.stringify(props.land_mean_ano)).toFixed(2);
            const integrated_ano = parseFloat(JSON.stringify(props.integrated_ano)).toFixed(2);
            const land_integrated_ano = parseFloat(JSON.stringify(props.land_integrated_ano)).toFixed(2);
            let units = 'K';
            let int_units = 'K';
            if (parameter == "T2M") {
                units = 'K';
                int_units = 'K';
            } else if (parameter == 'RTOT') {
                units = 'mm';
                int_units = 'm<sup>3</sup>';
            } else if (parameter == 'WG10') {
                units = 'm/s';
                int_units = 'm/s';
            }
            let authors = [];
            let urls = [];
            let titles = [];
            let lit_string = '';
            if (props.Text !== null) {
                for (const [key, value] of Object.entries(props.Text)) {
                    authors.push(value)
                  }
                for (const [key, value] of Object.entries(props.Link)) {
                    urls.push(value)
                  }
                for (const [key, value] of Object.entries(props.What)) {
                    titles.push(value)
                  }

                lit_string = "<hr>"
                for (var i = 0; i < authors.length; i++) {
                    lit_string = lit_string + "<b>" + authors[i] + ":</b> " + titles[i] + " <a target='_blank' href ='" + urls[i] + "'>MORE</a><br>"
                }
            }

            layer.bindPopup("<h6>Patch " + patch + "</h6>Year: " + year + "<br>\
                            Area: " + area + "km<sup>2</sup><br>\
                            Land Area: " + land_area + "km<sup>2</sup><br>\
                            Mean Anomaly: " + mean_ano + units + "<br>\
                            Mean Anomaly over Land: " + land_mean_ano + units + "<br>\
                            Integrated Anomaly: " + integrated_ano + int_units + "<br>\
                            Integrated Anomaly over Land: " + land_integrated_ano + int_units + lit_string);
        }
    }
});