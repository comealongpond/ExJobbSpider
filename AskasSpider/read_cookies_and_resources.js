try {
	var page       = require('webpage').create(),
	    system     = require('system');

	console.log('[');
	page.onResourceRequested = function(request) {
		console.log(JSON.stringify(request, null, 2) + ',');
	};
	page.onResourceReceived = function(response){
		console.log(JSON.stringify(response, null, 2) + ',');
	};

	if (system.args.length === 1) 
		{
	    console.log('Usage: read_ccokies.js <some URL>');
	    phantom.exit(1);
		} 


	else 
	{
		address = system.args[1];
		//if(system.args[2] != null && system.args[3] != null){
		page.settings.userName = system.args[2];
		page.settings.password = system.args[3];
		page.settings.resourceTimeout = 3000;

		page.open(address, function(status) 
		{	try {
				if(status !== 'success')
				{
					console.log('FAIL to load the address');
				}
				else{
				window.setTimeout( function(){
					//console.log('Found cookies : ' + page.evaluate(function () {
					//	return;
						 //return document.cookie;
					//}));
					//for(var i in phantom.cookies){
					//	console.log('Cookie: ', phantom.cookies[i])
					//}
					console.log('{"failsafe" : "hah"}]');
					console.log('---END_RESOURCES---');

					console.log(JSON.stringify(phantom.cookies, null, 2));

					phantom.clearCookies();
					phantom.exit(0);
					//----------------------------
					//KANSKE BEHÖVER RENSA COOKIES HÄR, KAN LIGGA KVAR GAMLA!
					//----------------------------


				}, 200);
			}
		} catch(ex){
			phantom.exit(1);
		}
		}


				 );
	}
}
catch(e) {
	phantom.exit(1);
}

phantom.onError = function(msg, trace) { phantom.exit(1); };




