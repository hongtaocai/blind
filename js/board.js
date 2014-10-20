angular.module('me.hcai.blind.board', ['ui.bootstrap'])
  .factory("stocks", function(){
    function randomString(length) {
      var result = '';
      var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
      for (var i = length; i > 0; --i) {
        result += chars[Math.round(Math.random() * (chars.length - 1))];
      }
      return result;
    }
    var stocks = [];
    for (var i = 0; i < 50 ; i++ ) {
      stocks.push({
        'name': randomString(4),
        'minGrowth': Math.random().toFixed(4),
        'dayGrowth': Math.random().toFixed(4)
      })
    }
    return stocks;
  })
  .factory("figures", function(){
    var figures = {
      'minGrowth': true,
      'dayGrowth': true
    }
    return figures;
  })
  .factory("key2Label", function(){
    return {
      'name' : 'Name',
      'minGrowth': 'Minute Growth',
      'dayGrowth': 'Day Growth'
    }
  })
  .controller('boardController', function($scope, stocks, figures, key2Label) {
    $scope.stocks = stocks;
    $scope.figures = figures;
    $scope.searchText = '';
    $scope.key2Label = key2Label;
    $scope.sortBy = 'name';
  });