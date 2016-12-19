(document).ready(function(){
    $("#loginbutton").click(login)


})



function login(){
    var name=document.getElementById("loginname").value;
	var password=document.getElementById("loginpassword").value;
	$.post(
		"/login",{
			userName: name,
			password: password
		},
		function(result){
			$("body").html(result);

		}

	);

}