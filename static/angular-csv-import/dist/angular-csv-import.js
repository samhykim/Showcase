/*! angular-csv-import - v0.0.14 - 2015-02-10
* Copyright (c) 2015 ; Licensed  */
'use strict';

var csvImport = angular.module('ngCsvImport', ['ngRoute']);

csvImport.directive('ngCsvImport', function ($http, $log, status) {
	return {
		restrict: 'E',
		transclude: true,
		replace: true,
		scope:{
			content:'=',
			orientation: '=',
			headerVisible: '=',
			separator: '=',
			result: '='
		},
		templateUrl: '../static/partials/upload_csv.html',
		link: function(scope, element) {


			scope.teamOrder = {};

			scope.max_conflicts = 0;

			scope.upload = function () {
				scope.uploaded = true
				var content = {
						csv: scope.content,
						orientation: scope.orientation,
						separator: scope.separator
					};
				var result = csvToJSON(content, scope.orientation);
				scope.result = JSON.parse(result);
				scope.teams = scope.result['teams'];
				//for (var i = 0; i < scope.teams.length; i++) {
				//	scope.teamOrder[scope.teams[i]] = 0;
				//}
				console.log(scope.teams);
			};

			scope.updateOrder = function (team, index) {
				if (scope.teams.indexOf(team) > -1) {
					for (var i in scope.teamOrder) {
						if (scope.teamOrder[i] == team) {
							delete scope.teamOrder[i];
						}
					}
					scope.teamOrder[index] = team;
				} else if (team == '') {
					delete scope.teamOrder[index];
				}
			};

			scope.findOrder = function () {
				$http.post('/upload', {
						"result": scope.result, 
						"fixed_teams": scope.teamOrder,
						"max_conflicts": scope.max_conflicts
					}).
	    		success(function(results) {
	      	$log.log(results);
	      	status.success(results.length + " potential showcase lineups have been found."); 
	      	scope.showcaseOrders = results['orders'];
	    	}).
	    		error(function(error) {
	      	//$log.log(error);
	      	console.log(error)
	      	status.error(error.message);
	  		});
			}
			element.on('change', function(onChangeEvent) {
				var reader = new FileReader();
				reader.onload = function(onLoadEvent) {
					scope.$apply(function() {
						var content = {
							csv: onLoadEvent.target.result.replace(/\r\n|\r/g,'\n'),
							orientation: scope.orientation,
							separator: scope.separator
						};

						scope.content = content.csv;
						// scope.result = csvToJSON(content, scope.orientation);
					});
				};
				if ( (onChangeEvent.target.type === "file") && (onChangeEvent.target.files != null || onChangeEvent.srcElement.files != null) )  {
					reader.readAsText((onChangeEvent.srcElement || onChangeEvent.target).files[0]);
				} else {
					if ( scope.content != null ) {
						var content = {
							csv: scope.content,
							orientation: !scope.orientation,
							separator: scope.separator
						};
						// scope.result = csvToJSON(content, scope.orientation);
					}
				}
			});
		



			//var findOrder = function()

			var csvToJSON = function(content, orientation) {
				var lines=content.csv.split('\n');
				console.log(lines)
				var result = {};
				var start = 0;
				var columnCount = lines[0].split(content.separator).length;
				var teams = []
				//var orientation = true;
				if (orientation) {
					teams = lines[0].split(content.separator);
					for (var i=0; i < teams.length; i++) {
						result[teams[i]] = [];
					}
					for (var i=1; i < lines.length; i++) {
						var currentline=lines[i].split(new RegExp(content.separator+'(?![^"]*"(?:(?:[^"]*"){2})*[^"]*$)'));
						for (var k=0; k < currentline.length; k++) {
							result[teams[k]].push(currentline[k]);
						}
					}
				} else {
					for (var i=0; i < lines.length; i++) {
						var currentline=lines[i].split(new RegExp(content.separator+'(?![^"]*"(?:(?:[^"]*"){2})*[^"]*$)'));
						var team = currentline.shift();
						result[team] = currentline;
						teams.push(team);
					}
				}
				result['teams'] = teams;
				return JSON.stringify(result);
			};
		}
	};
});
