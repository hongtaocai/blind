'use strict';

/**
 * @ngdoc overview
 * @name clientApp
 * @description
 * # clientApp
 *
 * Main module of the application.
 */
angular
  .module('clientApp', [
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch'
  ])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl'
      })
      .when('/about', {
        templateUrl: 'views/about.html',
        controller: 'AboutCtrl'
      })
      .when('/detail/:stockName', {
        templateUrl: 'views/detail.html',
        controller: 'DetailCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
  })
  .controller('AppCtrl', function($scope){
    $scope.tabs = ['Home', 'About'];
    $scope.tabsRoute = {
      Home: '#/home',
      About: '#/about'
    };
    $scope.activeTab = 'Home';
    $scope.setActiveTab = function(tabName) {
      $scope.activeTab = tabName;
    };
    $scope.getTabClass = function(tabName) {
      return tabName === $scope.activeTab ? 'active' : '';
    };
  });
