var searchClick = function() {
  var searchText = document.getElementById('searchText').value
  if( searchText.length == 0 ) {
    searchText = '_'
  }
  var nospacesSearchText = searchText.split(' ').join("_")
  searchString = nospacesSearchText.replace(/[\W_]+/g,"_");
  var searchButton = document.getElementById('searchButton')
  document.getElementById('searchButton').href = searchButton.href.replace('searchValue', searchString)
}
