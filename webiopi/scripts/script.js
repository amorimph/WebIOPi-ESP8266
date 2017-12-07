webiopi().ready(function() {
        		webiopi().setFunction(17,"out");
        		webiopi().setFunction(18,"out");
        		webiopi().setFunction(27,"out");
        		webiopi().setFunction(22,"out");
        		webiopi().setFunction(23,"out");
        		
        		var content, button;
        		content = $("#content");
        		
        		button = webiopi().createGPIOButton(17,"LED 1");
        		content.append(button);
        		
        		button = webiopi().createGPIOButton(18,"LED 2");
        		content.append(button);
        		
        		button = webiopi().createGPIOButton(27,"LED 3");
        		content.append(button);
        		
        		button = webiopi().createGPIOButton(22,"LED 4");
        		content.append(button);
        		
        		button = webiopi().createGPIOButton(23,"LED 5");
        		content.append(button);
				
				webiopi().refreshGPIO(true);
        		
        });