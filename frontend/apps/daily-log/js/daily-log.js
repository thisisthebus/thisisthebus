
// Slightly more concise and improved version based on http://www.jquery4u.com/snippets/url-parameters-jquery/
function getUrlVar(key){
	var result = new RegExp(key + "=([^&]*)", "i").exec(window.location.search);
	return result && unescape(result[1]) || "";
}


$( document ).ready(function() {
  var day = getUrlVar("day");
  $('#main .bigDate').first().append(day);
  fill_location_for_day(day, $('#main .locationContainer').first());

  $.getJSON( "/apps/daily-log/json/" + day, function( daily_log ) {
        $('#main .daySummary').append(daily_log['text']);
        $('#main .previous').append(daily_log['previous']);
        $('#main .subsequent').append(daily_log['subsequent']);
      });

});
