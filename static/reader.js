$(document).ready(function(){

	var subButt = $(".main-sub-butt");
	var submission = $("#redditURL");
	var downButt = $("#download-nested-butt");

	subButt.on("click", function(e){
		e.preventDefault();
		$('#loading-modal').modal({show: true});
		subButt.prop('disabled', true);
		downButt.prop('disabled', true);
		$.post("/api/submit",
		{
			"submission": submission.val()
		},
		function(data, status){
			var code = JSON.parse(data)["code"];
			$("#download-butt").attr('href', '/api/download/' + code);
			subButt.prop('disabled', false);
			downButt.prop('disabled', false);
		}

		)
	})


})