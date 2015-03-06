'use strict';

/* App Module */

angular.module('showcase', ['ngRoute', 'angularFileUpload', 'ngCsvImport'])

.controller('ShowcaseController', function ($scope, $http, $log, FileUploader) {
  console.log('sam')
  //$scope.data = {'sam', 'sdf'}
  //$scope.sam = 'sadf'
  $scope.uploader = new FileUploader();
  $scope.getResults = function () {
	   // get the URL from the input
	  var userInput = $scope.input_url;
	  // fire the API request
	  console.log(userInput)
	  $http.post('/start', {"url": userInput}).
	    success(function(results) {
	      $log.log(results);
	    }).
	    error(function(error) {
	      $log.log(error);
	  });
	};

	$scope.upload = function (file) {
		$http.post('/upload', {"file": file}).
	    success(function(results) {
	      $log.log(results);
	    }).
	    error(function(error) {
	      $log.log(error);
	  });
	};

})

;
