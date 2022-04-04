var myApp = angular.module('SSS', [])
    .config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('[[').endSymbol(']]');
    });

var addImageToRelayObjects = function(relayObjects) {
	for (var i=0; i < relayObjects.length; i++) {
  		var relay = relayObjects[i];
		if (relay.state == 'on') {
			relay.image = '../static/images/flash_on.png';
		}
		else {
			relay.image = '../static/images/flash_off.png';		
		}
  	}	
	return relayObjects;
};

myApp.controller('RelaysController', ['$scope', '$http', function($scope, $http) {
  
  var getRelayInfo = function() {
    $http.get("api/relays").then(function(response) {
      var relays = response.data.relays;
      addImageToRelayObjects(relays)
      $scope.relays = relays;
    }, function(error) {}
    );
  };
  
  $scope.toggleRelay = function(relay) {
    var newState = 'off';
    if (relay.state == 'off') {
    	newState = 'on';
    }
    
    $http.put("/api/relays/"+relay.id, { state : newState}).then(function(response) {
    	relay = response.data.relay;
        if (relay.state == 'on') {
            relay.image = '../static/images/flash_on.png';
        }
        else {
            relay.image = '../static/images/flash_off.png';		
        }
        for (var i=0; i < $scope.relays.length; i++) {
            if ($scope.relays[i].id == relay.id) {
                $scope.relays[i] = relay;
                break;
            }
        }    	
    }, function(error) {}
    );
  }
  getRelayInfo();
  
}]);
