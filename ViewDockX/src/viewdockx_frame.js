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