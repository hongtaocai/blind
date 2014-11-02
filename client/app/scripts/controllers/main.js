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
    function formatGrowth(growth) {
      var prefix = growth >= 0 ? '+' : '-';
      return prefix + growth;
    }
    var stocks = [];
    for (var i = 0; i < 50 ; i++ ) {
      stocks.push({
        'name': randomString(4),
        'lastMinRealGrowth': formatGrowth(Math.random().toFixed(4)*2 -1),
        'nextMinPredictedGrowth': formatGrowth(Math.random().toFixed(4)),
        'lastMinPredictedGrowth': formatGrowth(Math.random().toFixed(4)),
        'errorRate': Math.floor(Math.random()*100)
      });
    }
    return stocks;
  })
  .controller('MainCtrl', function ($scope, stocks) {
    $scope.searchText = '';
    $scope.stocks = stocks;
  });

