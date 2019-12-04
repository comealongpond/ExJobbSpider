
address = system.args[1];
var page = require('webpage').create();
page.open(address, function() {
  page.render('github.png');
  phantom.exit();
});