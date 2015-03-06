'use strict';

/* Directives */

angular.module('showcase')

.directive('zeStatus', ['status', function (status) {
    return {
        restrict: 'E',
        replace: true,
        templateUrl: '/static/partials/status.html',
        link: function (scope, elm, $attrs, ctrl) {
            scope.status = status;
        }
    }
}])

;