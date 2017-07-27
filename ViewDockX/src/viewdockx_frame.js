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
            window.location = "viewdockx:?show_all=true";
        } else {
            $(".struct").prop('checked', false);
            window.location = "viewdockx:?show_all=false";
        }
    });

    $("#viewdockx_table tr td").click(function() {
        //Reset
        $("#viewdockx_table td, th").removeClass("highlight");
        //Add highlight class to new column
        var index = $(this).index();
        $("#viewdockx_table tr").each(function(i, tr) {
            $(tr).find('td, th').eq(index).addClass("highlight");
        });
        // alert($(`#viewdockx_table td:nth-child(${index + 1}`).map(function() {
        //     return $(this).text();
        // }).get());
    });


    var ctx = document.getElementById("viewdockx_chart");
    var viewdockx_chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['M', 'T', 'W', 'T', 'F', 'S', 'S'],
            datasets: [{
                label: 'apples',
                data: [12, 19, 3, 17, 6, 3, 7],
                backgroundColor: "rgba(153,255,51,0.6)"
            }, {
                label: 'oranges',
                data: [2, 29, 5, 5, 2, 3, 10],
                backgroundColor: "rgba(255,153,0,0.6)"
            }]
        }
    });
    var years = [1500,1600,1700,1750,1800,1850,1900,1950,1999,2050];

    var africa = [86,114,106,106,107,111,133,221,783,2478];
    var asia = [282,350,411,502,635,809,947,1402,3700,5267];
    var europe = [168,170,178,190,203,276,408,547,675,734];
    var latinAmerica = [40,20,10,16,24,38,74,167,508,784];
    var northAmerica = [6,3,2,2,7,26,82,172,312,433];

    // alert("test")
    var ctx = document.getElementById("test_chart");
    var myChart = new Chart(ctx, {
      type: 'line',
      data: 
      {
        labels: years,
        datasets: 
        [
          { 
            data: africa
          }
        ]
      }
    });


}
