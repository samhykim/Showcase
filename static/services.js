'use strict';

/* Services */

angular.module('showcase')

.factory('status', function ($rootScope) {
    var singleton = {
        alert: {},
        onLoadAlert: {},
    };

    singleton.clear = function () {
        singleton.alert = {};
        singleton.alert.forModal = false;
        singleton.onLoadAlert = {};
    }

    var setAlert = function (message, cssClass) {
        singleton.clear();
        singleton.alert.message = message;
        singleton.alert.class = cssClass;
    }

    var setAlertType = function (type, cssClass) {
        singleton.clear();
        singleton.alert.type = type;
        singleton.alert.class = cssClass;
    }

    $rootScope.$on("$routeChangeSuccess", function (event, current, previous) {
        var tempAlert = singleton.onLoadAlert;
        singleton.clear();
        singleton.alert = tempAlert;
    });

    singleton.onLoadSuccess = function (message) {
        singleton.onLoadAlert.message = message;
        singleton.onLoadAlert.class = "alert-success";
    }

    singleton.warn = function (message) {
        setAlert(message, "");
    }

    singleton.spinner = function (message) {
        singleton.warn(message);
        singleton.alert.spinner = true;
    }

    singleton.error = function (message) {
        setAlert(message, "alert-error");
    }

    singleton.success = function (message) {
        setAlert(message, "alert-success");
    }

    singleton.warningType = function (type) {
        setAlertType(type, "");
    }

    return singleton;
})

;