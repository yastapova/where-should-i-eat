var width = 1000;
var height = 1000;

var cuisines_file = "/static/data/test_cuisines.csv";
var dishes_file = "/static/data/test_links.csv";

var cuisine_id_map = {};

cuisines_temp = d3.csv(cuisines_file).then(function(cuisine_data) {
    for(var i = 0; i < cuisine_data.length; i++) {
        var cus_i = cuisine_data[i];

        cuisine_id_map[cus_i.name] = cus_i.id;
    }

    dishes_temp = d3.csv(dishes_file).then(function(dishes_data) {
        var inside = [];  // stuff in the center of the vis
        var outside = new Map();  // stuff on the outside of the vis
        var links = [];  // links between inside and outside

        // create necessary data representation
        dishes_data.forEach(function(d) {
            if (d == null)
                return;

            // create inside (cuisine) object
            i_cuisine = { id: cuisine_id_map[d.cuisine], name: d.cuisine, related_links: [] };
            i_cuisine.related_nodes = [i_cuisine.id];
            inside.push(i_cuisine);

            // convert string into array
            // TODO: find a better way than eval
            d_array = eval(d.dishes);

            if (!Array.isArray(d_array))
                d_array = [d_array];

            // create outside (dish) object from each element
            d_array.forEach(function(dish1) {
                o_dish = outside.get(dish1);

                if (o_dish == null)
                {
                    o_dish = { name: dish1,	id: 'dish_' + dish1.replace(" ", "_"), related_links: [] };
                    o_dish.related_nodes = [o_dish.id];

                    outside.set(dish1, o_dish);
                }

                // create the links
                l = { id: 'l-' + i_cuisine.id + '-' + o_dish.id, inner: i_cuisine, outer: o_dish }
                links.push(l);

                // backfill relationships btwn nodes and links
                i_cuisine.related_nodes.push(o_dish.id);
                i_cuisine.related_links.push(l.id);
                o_dish.related_nodes.push(i_cuisine.id);
                o_dish.related_links.push(l.id);
            });
        });

        data = {
            inside: inside,
            outside: Array.from(outside.values()),
            links: links
        }

        diameter = 960;
        rect_width = 140;
        rect_height = 14;

        var link_width = "1px";

        var il = data.inside.length;
        var ol = data.outside.length;

        var inner_y = d3.scaleLinear()
            .domain([0, il])
            .range([-(il * rect_height)/2, (il * rect_height)/2]);

        mid = (data.outside.length/2.0)
        var outer_x = d3.scaleLinear()
            .domain([0, mid, mid, data.outside.length])
            .range([15, 170, 190 ,355]);

        var outer_y = d3.scaleLinear()
            .domain([0, data.outside.length])
            .range([0, diameter / 2 - 120]);


        // setup positioning
        data.outside = data.outside.map(function(d, i) {
            d.x = outer_x(i);
            d.y = diameter/3;
            return d;
        });

        data.inside = data.inside.map(function(d, i) {
            d.x = -(rect_width / 2);
            d.y = inner_y(i);
            return d;
        });

        function projectR(x, y) {
            radius = Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2));
            return radius;
        }

        function projectTheta(x, y) {
            deg = Math.atan2(y, x) - Math.PI;
            return deg;
        }

        var link_generator = d3.linkRadial()
            .source(function(d) { return [projectTheta(d.inner.x, d.inner.y + rect_height/2),
                                          d.outer.x > 180 ? projectR(d.inner.x, d.inner.y) : projectR(d.inner.x + rect_width, d.inner.y)]; })
            .target(function(d) { return [projectTheta(d.outer.x, d.outer.y),
                                          projectR(d.outer.x, d.outer.y)]; });

        var svg = d3.select("svg")
            .attr("width", width)
            .attr("height", height)
          .append("g")
            .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");


        // links
        var link = svg.append('g').attr('class', 'links').selectAll(".link")
            .data(data.links)
          .enter().append('path')
            .attr('class', 'link')
            .attr('id', function(d) { return d.id })
            .attr("d", function(d) { return link_generator(d); })
            .attr('stroke', "black")
            .attr('stroke-width', link_width)
            .style("fill", "none");

        // outer nodes

        var onode = svg.append('g').selectAll(".outer_node")
            .data(data.outside)
          .enter().append("g")
            .attr("class", "outer_node")
            .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; })
            .on("mouseover", mouseover)
            .on("mouseout", mouseout);

        onode.append("circle")
            .attr('id', function(d) { return d.id })
            .attr("r", 4.5);

        onode.append("circle")
            .attr('r', 20)
            .attr('visibility', 'hidden');

        onode.append("text")
            .attr('id', function(d) { return d.id + '-txt'; })
            .attr("dy", ".31em")
            .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
            .attr("transform", function(d) { return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)"; })
            .text(function(d) { return d.name; });

        // inner nodes

        var inode = svg.append('g').selectAll(".inner_node")
            .data(data.inside)
          .enter().append("g")
            .attr("class", "inner_node")
            .attr("transform", function(d, i) { return "translate(" + d.x + "," + d.y + ")"})
            .on("mouseover", mouseover)
            .on("mouseout", mouseout);

        inode.append('rect')
            .attr('width', rect_width)
            .attr('height', rect_height)
            .attr('id', function(d) { return d.id; })
            .attr('fill', "limegreen");

        inode.append("text")
            .attr('id', function(d) { return d.id + '-txt'; })
            .attr('text-anchor', 'middle')
            .attr("transform", "translate(" + rect_width/2 + ", " + rect_height * .75 + ")")
            .text(function(d) { return d.name; });

        // need to specify x/y/etc

//        d3.select(self.frameElement).style("height", diameter - 150 + "px");

        function mouseover(d)
        {
            // bring to front
//            d3.selectAll('.links .link').sort(function(a, b){ return d.related_links.indexOf(a.id); });
//
//            for (var i = 0; i < d.related_nodes.length; i++)
//            {
//                d3.select('#' + d.related_nodes[i]).classed('highlight', true);
//                d3.select('#' + d.related_nodes[i] + '-txt').attr("font-weight", 'bold');
//            }
//
//            for (var i = 0; i < d.related_links.length; i++)
//                d3.select('#' + d.related_links[i]).attr('stroke-width', '5px');
            return;
        }

        function mouseout(d)
        {
//            for (var i = 0; i < d.related_nodes.length; i++)
//            {
//                d3.select('#' + d.related_nodes[i]).classed('highlight', false);
//                d3.select('#' + d.related_nodes[i] + '-txt').attr("font-weight", 'normal');
//            }
//
//            for (var i = 0; i < d.related_links.length; i++)
//                d3.select('#' + d.related_links[i]).attr('stroke-width', link_width);
            return;
        }



    });
});