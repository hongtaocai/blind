'use strict';

/**
 * @ngdoc function
 * @name clientApp.controller:AboutCtrl
 * @description
 * # AboutCtrl
 * Controller of the clientApp
 */
angular.module('clientApp')
  .controller('DetailCtrl', function ($scope) {
    /* Chart options */
    $scope.growthChartOptions = {
      chart: {
        type: 'multiBarChart',
        height: 450,
        margin: {
          top: 20,
          right: 20,
          bottom: 60,
          left: 45
        },
        clipEdge: true,
        staggerLabels: false,
        transitionDuration: 1,
        stacked: false,
        xAxis: {
          axisLabel: 'Time (ms)',
          showMaxMin: true,
          tickFormat: function (d) {
            return d3.time.format('%H:%M:%S')(d);
          }
        },
        yAxis: {
          axisLabel: 'Y Axis',
          axisLabelDistance: 40,
          showMaxMin: false,
          tickFormat: function (d) {
            return d3.format(',.1f')(d);
          }
        },
        showControls: false
      }
    };

    /* Chart data */
    $scope.growthChartData = [{ values: [], key: 'Predicted Min Growth' }, {values:[], key:'Actual Min Growth'}];

    $scope.priceChartData = {};

    $scope.priceChartOptions = {};

    var time = new Date();
    setInterval(function(){
      var t, t1;
      time = new Date();
      t = Math.random() - 0.5;
      t1 = t + (Math.random() - 0.5) * 0.1;
      $scope.growthChartData[0].values.push({ x: time, y: t});
      $scope.growthChartData[1].values.push({ x: time, y: t1});
      if ($scope.growthChartData[0].values.length > 30) {
        $scope.growthChartData[0].values.shift();
        $scope.growthChartData[1].values.shift();
      }
      $scope.$apply();
    }, 5000);
  });
