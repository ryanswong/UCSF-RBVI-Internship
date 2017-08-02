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

    $('#histogram_btn').on('click', function() {
        if (typeof vdx_chart != 'undefined') {
            vdx_chart.destroy();
        }
        var ctx = document.getElementById("viewdock_histogram").getContext('2d');
        var myChart = new Chart(ctx, {
            type: 'bar',
               data: {
                labels: data_array, //bar labels (score) ex. 1-10
                datasets: [{
                    label: property,
                    data: [123, 123, 2, 123, 23, 23], // count
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255,99,132,1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero:true
                        }
                    }]
                }
            }
        });
    });






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