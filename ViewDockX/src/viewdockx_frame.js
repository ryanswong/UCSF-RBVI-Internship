function init() {
    $(document).ready(function() {
        $("#viewdockx_table").tablesorter();
    });

    $("#show_checkboxes").click(function() {

        if ($(this).is(":checked")) {
            $(".checkbox").show();
            $(".link").hide();
        } else {
            $(".checkbox").hide();
            $(".link").show();
        }

    });

    $(".struct").click(function() {

        if ($(this).is(":checked")) {
            window.location = $(this).attr('href') + "&display=1";
        } else {
            window.location = $(this).attr('href') + "&display=0";
        }

    });

    $("#check_all").click(function() {

        if ($(this).is(":checked")) {
            $(".struct").prop('checked', true);
            window.location = "viewdockx:check_all?show_all=true";
        } else {
            $(".struct").prop('checked', false);
            window.location = "viewdockx:check_all?show_all=false";
        }
    });


    var data_array = [];
    var label_array = [];
    var property;

    $('#viewdockx_table tr td').on('click', function() {
        var $currentTable = $(this).closest('table');
        var index = $(this).index();
        $currentTable.find('td').removeClass('selected');
        $currentTable.find('tr').each(function() {
            $(this).find('td').eq(index).addClass('selected');
        });
        data_array = $(`#viewdockx_table td:nth-child(${index + 1}`).map(function() {
            return $(this).text();
        }).get();

        // ASSUMING NAME COLUMNS STAYS AS 2ND COLUMN. MAY NEED CHANGES LATER
        label_array = $(`#viewdockx_table td:nth-child(${2}`).map(function() {
            return $(this).text();
        }).get();

        property = $('#viewdockx_table th').eq($(this).index()).text();

    });


    // var vdx_chart=null; 
    $('#graph_btn').on('click', function() {
        if (typeof vdx_chart != 'undefined') {
            vdx_chart.destroy();
        }
        var context = document.getElementById("viewdockx_chart").getContext('2d');
        vdx_chart = new Chart(context, {
            type: 'line',
            data: {
                labels: label_array, //x - axis
                datasets: [{
                    label: property,
                    data: data_array //y - axis
                }]
            }
        });
    });

    
    var data = d3.range(1000).map(d3.randomBates(10));

    var formatCount = d3.format(",.0f");

    var svg = d3.select("svg"),
        margin = {top: 10, right: 30, bottom: 30, left: 30},
        width = +svg.attr("width") - margin.left - margin.right,
        height = +svg.attr("height") - margin.top - margin.bottom,
        g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var x = d3.scaleLinear()
        .rangeRound([0, width]);

    var bins = d3.histogram()
        .domain(x.domain())
        .thresholds(x.ticks(20))
        (data);

    var y = d3.scaleLinear()
        .domain([0, d3.max(bins, function(d) { return d.length; })])
        .range([height, 0]);

    var bar = g.selectAll(".bar")
      .data(bins)
      .enter().append("g")
        .attr("class", "bar")
        .attr("transform", function(d) { return "translate(" + x(d.x0) + "," + y(d.length) + ")"; });

    bar.append("rect")
        .attr("x", 1)
        .attr("width", x(bins[0].x1) - x(bins[0].x0) - 1)
        .attr("height", function(d) { return height - y(d.length); });

    bar.append("text")
        .attr("dy", ".75em")
        .attr("y", 6)
        .attr("x", (x(bins[0].x1) - x(bins[0].x0)) / 2)
        .attr("text-anchor", "middle")
        .text(function(d) { return formatCount(d.length); });

    g.append("g")
        .attr("class", "axis axis--x")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

    // alert(data_array);

    // OLD SCRIPT
    // $("#viewdockx_table tr td").click(function() {
    //     //Reset
    //     $("#viewdockx_table td").removeClass("highlight");
    //     //Add highlight class to new column
    //     var index = $(this).index();
    //     $("#viewdockx_table tr").each(function(i, tr) {
    //         $(tr).find('td, th').eq(index).addClass("highlight");
    //     });
    //     alert($(`#viewdockx_table td:nth-child(${index + 1}`).map(function() {
    //         return $(this).text();

    //     }).get());
    // });


}

// chart.options.data.push({object}); // Add a new dataSeries

// https://canvasjs.com/docs/charts/basics-of-creating-html5-chart/updating-chart-options/