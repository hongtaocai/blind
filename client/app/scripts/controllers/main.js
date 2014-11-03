'use strict';

/**
 * @ngdoc function
 * @name clientApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the clientApp
 */
angular.module('clientApp')
  .constant('config', {
    'darkGreen' : '#0AA344',
    'lightGreen': '#BDDD22',
    'darkRed' : '#FF2121',
    'lightRed' : '#FFB3A7'
  })
  .service('stocks', function(){
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
      });}
    return {
      stocks: stocks
    };
  })
  .controller('MainCtrl', function ($scope, stocks, config) {

    (function(){
      $scope.searchText = '';
      $scope.stocks = stocks.stocks;
      $scope.maxNextMinPredictedGrowth = - Infinity;
      $scope.minNextMinPredictedGrowth = Infinity;
      for (var stockIndex in $scope.stocks) {
        if ($scope.maxNextMinPredictedGrowth <  $scope.stocks[stockIndex].nextMinPredictedGrowth) {
          $scope.maxNextMinPredictedGrowth =   $scope.stocks[stockIndex].nextMinPredictedGrowth;
        }
        if ($scope.minNextMinPredictedGrowth >  $scope.stocks[stockIndex].nextMinPredictedGrowth) {
          $scope.minNextMinPredictedGrowth =  $scope.stocks[stockIndex].nextMinPredictedGrowth;
        }
      }
    })();

    $scope.formatGrowth = function(growth) {
      var prefix = growth >= 0 ? '+' : '';
      return prefix + growth.toFixed(4);
    };

    $scope.formatErrorRate = function(errorRate) {
      return Math.floor(errorRate);
    };

    $scope.getColorFromGrowth = function(growth, maxGrowth, minGrowth) {
      var scale = null;
      if (growth >= 0) {
        scale = chroma.scale([config.lightGreen, config.darkGreen]);
        return scale(growth/maxGrowth).hex();
      } else {
        scale = chroma.scale([config.lightRed, config.darkRed]);
        return scale(growth/minGrowth).hex();
      }
    };

    $scope.redirectToStock = function(stockName) {
      window.location = '/#/detail/'+stockName;
    };
  });

