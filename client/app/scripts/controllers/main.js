'use strict';

/**
 * @ngdoc function
 * @name clientApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the clientApp
 */
angular.module('clientApp')
  .factory('stocks', function(){
    function randomString(length) {
      var result = '';
      var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
      for (var i = length; i > 0; --i) {
        result += chars[Math.round(Math.random() * (chars.length - 1))];
      }
      return result;
    }
    var stocks = [];
    for (var i = 0; i < 52 ; i++ ) {
      stocks.push({
        'name': randomString(4),
        'lastMinPredictedGrowth': Math.random()*2 -1,
        'nextMinPredictedGrowth': Math.random()*2 -1,
        'lastMinActualGrowth': Math.random()*2 -1,
        'errorRate': Math.random()*100
      });
    }
    return stocks;
  })
  .controller('MainCtrl', function ($scope, stocks) {
    $scope.searchText = '';
    $scope.stocks = stocks;
    $scope.formatGrowth = function(growth) {
      var prefix = growth >= 0 ? '+' : '';
      return prefix + growth.toFixed(4);
    };
    $scope.formatErrorRate = function(errorRate) {
      return Math.floor(errorRate);
    };
  });

