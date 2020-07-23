var displayCount;
var nextPageFunction;
var prevPageFunction;
var sellerCount;

window.onload=function(){

  document.getElementById("searchText").addEventListener("keydown", function(event) {
    if (event.keyCode == 13) {
      event.preventDefault();
      document.getElementById("searchIcon").click();
    }
  });

  displayCount = document.getElementsByClassName('productItems').length
  displayUtil(true)

  var sellers = []
  var sellersElements = document.getElementsByClassName("sellerName")
  for( var i=0; i<sellersElements.length; i++ ) {
    if( ! sellers.includes( sellersElements[i].innerText ) ) {
      sellers.push( sellersElements[i].innerText )
    }
  }
  var sellersCount = []
  for( var i=0; i<sellers.length; i++ ) {
    sellersCount.push(0)
  }
  for( var i=0; i<sellersElements.length; i++ ) {
    sellersCount[sellers.indexOf( sellersElements[i].innerText )] += 1
  }
  var sellersDict = []
  for( var i=0; i<sellers.length; i++ ) {
    sellersDict.push( [ sellers[i], sellersCount[i] ])
  }
  sellersDict.sort(function(x, y) {
    if( x[1] < y[1] ) {
      return 1
    }
    else if( x[1] > y[1] ) {
      return -1;
    }
    else {
      return 0;
    }
  });
  sellerCount = sellersDict.length
  for( var i=0; i<sellersDict.length && i<5; i++ ) {
    document.getElementById( 'seller'+(i+1).toString()+'Div' ).style.display = 'block'
    document.getElementById( 'seller'+(i+1).toString() ).nextSibling.innerHTML = "&nbsp" + sellersDict[i][0]
    document.getElementById( 'seller'+(i+1).toString() ).onclick = selectSeller
  }
  document.getElementById( 'allSellers' ).onclick = selectSeller
}

var displayUtil = function (firstTime) {
  var productItems = document.getElementsByClassName('productItems')

  document.getElementById('p2').style.display = 'block';
  document.getElementById('p2').style.display = 'block';
  document.getElementById('p3').style.display = 'block';
  document.getElementById('p4').style.display = 'block';
  document.getElementById('p5').style.display = 'block';

  var i = 0;
  for( i=0; i<16 && i<displayCount; i++ ) {
    productItems[i].style.display = 'block'
  }

  var maxPage = 1;
   if( displayCount<=16 ) {
     document.getElementById('pageCount').textContent = 'Page 1 of 1'
     document.getElementById('p2').style.display = 'none';
     document.getElementById('p3').style.display = 'none';
     document.getElementById('p4').style.display = 'none';
     document.getElementById('p5').style.display = 'none';
   } else if ( displayCount<=32 ) {
     maxPage = 2;
     document.getElementById('pageCount').textContent = 'Page 1 of 2'
     document.getElementById('p3').style.display = 'none';
     document.getElementById('p4').style.display = 'none';
     document.getElementById('p5').style.display = 'none';
   } else if ( displayCount<=48 ) {
     maxPage = 3;
     document.getElementById('pageCount').textContent = 'Page 1 of 3'
     document.getElementById('p4').style.display = 'none';
     document.getElementById('p5').style.display = 'none';
   } else if ( displayCount<=64 ) {
     maxPage = 4;
     document.getElementById('pageCount').textContent = 'Page 1 of 4'
     document.getElementById('p5').style.display = 'none';
   } else if ( displayCount<=80 ) {
     maxPage = 5;
     document.getElementById('pageCount').textContent = 'Page 1 of 5'
   }

   document.getElementById('p1').addEventListener('click', () => {
     document.getElementById('pageCount').textContent = 'Page 1 of '+ maxPage.toString()
     var i = 0;
     for( i=0; i<displayCount; i++ ) {
       productItems[i].style.display = 'none'
     }
     for( i=0; i<16 && i<displayCount; i++ ) {
       productItems[i].style.display = 'block'
     }
   })

   document.getElementById('p2').addEventListener('click', () => {
     document.getElementById('pageCount').textContent = 'Page 2 of '+ maxPage.toString()
     var i = 16;
     for( i=0; i<displayCount; i++ ) {
       productItems[i].style.display = 'none'
     }
     for( i=16; i<32 && i<displayCount; i++ ) {
       productItems[i].style.display = 'block'
     }
   })

   document.getElementById('p3').addEventListener('click', () => {
     document.getElementById('pageCount').textContent = 'Page 3 of '+ maxPage.toString()
     var i = 32;
     for( i=0; i<displayCount; i++ ) {
       productItems[i].style.display = 'none'
     }
     for( i=32; i<48 && i<displayCount; i++ ) {
       productItems[i].style.display = 'block'
     }
   })

   document.getElementById('p4').addEventListener('click', () => {
     document.getElementById('pageCount').textContent = 'Page 4 of '+ maxPage.toString()
     var i = 48;
     for( i=0; i<displayCount; i++ ) {
       productItems[i].style.display = 'none'
     }
     for( i= 48; i<64 && i<displayCount; i++ ) {
       productItems[i].style.display = 'block'
     }
   })

   document.getElementById('p5').addEventListener('click', () => {
     document.getElementById('pageCount').textContent = 'Page 5 of '+ maxPage.toString()
     var i = 64;
     for( i=0; i<displayCount; i++ ) {
       productItems[i].style.display = 'none'
     }
     for( i=64; i<80 && i<displayCount; i++ ) {
       productItems[i].style.display = 'block'
     }
   })

   if( !firstTime ) {
     document.getElementById('pnext').removeEventListener('click', nextPageFunction)
     document.getElementById('pprevious').removeEventListener('click', prevPageFunction)
   }

   nextPageFunction = function()  {
     pageNo = parseInt(document.getElementById('pageCount').textContent[5])
     if( pageNo != 5 && pageNo != maxPage ) {
       document.getElementById('p'+(pageNo+1).toString()).click();
     }
   }

   prevPageFunction = function() {
     pageNo = parseInt(document.getElementById('pageCount').textContent[5])
     if( pageNo != 1 ) {
       document.getElementById('p'+(pageNo-1).toString()).click();
     }
   }

   document.getElementById('pnext').addEventListener('click', nextPageFunction)
   document.getElementById('pprevious').addEventListener('click', prevPageFunction)
}

var priceLH = function () {
  var items = []
  var productItems = document.getElementsByClassName('productItems');
  var productPrices = document.getElementsByClassName('productPrices');
  for( var i=0; i<displayCount; i++ ) {
    items.push( [ productItems[i].innerHTML, parseInt(productPrices[i].innerText) ] )
  }
  items.sort(function(x, y) {
    if( x[1] < y[1] ) {
      return -1
    }
    else if( x[1] > y[1] ) {
      return 1;
    }
    else {
      return 0;
    }
  });
  for( var i=0; i<displayCount; i++ ) {
    productItems[i].innerHTML = items[i][0]
  }
}

var priceHL = function () {
  var items = []
  var productItems = document.getElementsByClassName('productItems');
  var productPrices = document.getElementsByClassName('productPrices');
  for( var i=0; i<displayCount; i++ ) {
    items.push( [ productItems[i].innerHTML, parseInt(productPrices[i].innerText) ] )
  }
  items.sort(function(x, y) {
    if( x[1] < y[1] ) {
      return 1
    }
    else if( x[1] > y[1] ) {
      return -1;
    }
    else {
      return 0;
    }
  });
  for( var i=0; i<displayCount; i++ ) {
    productItems[i].innerHTML = items[i][0]
  }
}

var ratingHL = function () {
  var items = []
  var productItems = document.getElementsByClassName('productItems');
  var productRatings = document.getElementsByClassName('productRatings');
  for( var i=0; i<displayCount; i++ ) {
    items.push( [ productItems[i].innerHTML, parseFloat(productRatings[i].innerText) ] )
  }
  items.sort(function(x, y) {
    if( x[1] < y[1] ) {
      return 1
    }
    else if( x[1] > y[1] ) {
      return -1;
    }
    else {
      return 0;
    }
  });
  for( var i=0; i<displayCount; i++ ) {
    productItems[i].innerHTML = items[i][0]
  }
}

var selectSeller = function () {
  document.getElementById('offersNo').checked = true
  selectedSellerName = this.nextSibling.innerHTML.substring(6)
  if( selectedSellerName === 'All Sellers' ) {
    items = []
    var productItems = document.getElementsByClassName('productItems');
    var searchRanks = document.getElementsByClassName('searchRank');
    for( var i=0; i<productItems.length; i++ ) {
      productItems[i].style.display = 'none'
      items.push( [ productItems[i].innerHTML, parseInt(searchRanks[i].innerText) ] )
    }
    items.sort(function(x, y) {
      if( x[1]<y[1] ) {
        return -1
      }
      else if( x[1]>y[1] ) {
        return 1;
      }
      else {
        return 0;
      }
    });
    for( var i=0; i<productItems.length; i++ ) {
      productItems[i].innerHTML = items[i][0]
    }
    displayCount = productItems.length
    displayUtil(false)
  }
  else {
    items = []
    var productItems = document.getElementsByClassName('productItems');
    var sellers = document.getElementsByClassName("sellerName");
    displayCount = 0
    for( var i=0; i<productItems.length; i++ ) {
      productItems[i].style.display = 'none'
      if( sellers[i].innerText === selectedSellerName ) {
        displayCount += 1
      }
      items.push( [ productItems[i].innerHTML, sellers[i].innerText ] )
    }
    items.sort(function(x, y) {
      if( x[1] === selectedSellerName ) {
        return -1
      }
      else if( y[1] === selectedSellerName ) {
        return 1;
      }
    });
    for( var i=0; i<productItems.length; i++ ) {
      productItems[i].innerHTML = items[i][0]
    }
    displayUtil(false)
  }
}

var offersOnlyFunc = function () {
  items = []
  var productItems = document.getElementsByClassName('productItems');
  var hasOffer = document.getElementsByClassName("hasOffer");
  newdisplayCount = 0
  for( var i=0; i<displayCount; i++ ) {
    productItems[i].style.display = 'none'
    if( hasOffer[i].innerText === 'yes' ) {
      newdisplayCount += 1
    }
    items.push( [ productItems[i].innerHTML, hasOffer[i].innerText ] )
  }
  items.sort(function(x, y) {
    if( x[1] === 'yes' ) {
      return -1
    }
    else if( y[1] === 'yes' ) {
      return 1;
    }
  });
  for( var i=0; i<displayCount; i++ ) {
    productItems[i].innerHTML = items[i][0]
  }
  displayCount = newdisplayCount
  displayUtil(false)
}

var notOffersOnlyFunc = function () {
  var sellers = document.getElementsByName('sellerSelection');
  for( var i=0; i<=sellerCount; i++ ) {
    if( sellers[i].checked ) {
      sellers[i].click()
      break;
    }
  }
}
