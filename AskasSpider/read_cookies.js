var page       = require('webpage').create(),
    system     = require('system');

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

	page.onLoadFinished = function(status){

	}

	page.open(address, function(status) 
	{
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

			console.log(JSON.stringify(phantom.cookies, null, 2));

			phantom.clearCookies();
			phantom.exit();
			//----------------------------
			//KANSKE BEHÖVER RENSA COOKIES HÄR, KAN LIGGA KVAR GAMLA!
			//----------------------------


		}, 600);
	}
	}


			 );
}





