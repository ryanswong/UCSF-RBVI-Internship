$(document).ready(function() 
{ 
$("#viewdockx_table").tablesorter(); 
} 
);

$("#show_checkboxes").click(function(){

if($(this).is(":checked")){
$(".checkbox").show();
$(".link").hide();
}
else{
$(".checkbox").hide();
$(".link").show();
}

});

$(".struct").click(function(){

if($(this).is(":checked")){
window.location=$(this).attr('href')+"&display=1";
}
else{
window.location=$(this).attr('href')+"&display=0";
}

});

$("#check_all").click(function(){

if($(this).is(":checked")){
$(".struct").prop('checked', true);
window.location="viewdockx:?show_all=true";
}
else{
$(".struct").prop('checked', false);
window.location="viewdockx:?show_all=false";
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
alert($(`#viewdockx_table td:nth-child(${index + 1}`).map(function(){
return $(this).text();
}).get());
});

<style>

.highlight {
background-color: yellow;
} 
</style>


    var ctx = document.getElementById('myChart').getContext('2d');
    var myChart = new Chart(ctx, {
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

</body>
</html>