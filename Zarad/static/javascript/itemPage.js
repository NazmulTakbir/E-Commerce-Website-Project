var totalQuantity
var offers = [];
var netPayment;

window.onload=function(){

  document.getElementById("searchText").addEventListener("keydown", function(event) {
    if (event.keyCode == 13) {
      event.preventDefault();
      document.getElementById("searchIcon").click();
    }
  });

  discounts = document.getElementsByName('discountPercentage')
  minQuans = document.getElementsByName('minQuan')
  total = discounts.length
  for( var i=0; i<total; i++ ) {
    offers.push([parseInt(minQuans[i].innerText), parseFloat(discounts[i].innerText)])
  }

  totalQuantity = 0

  document.getElementById('orderQuantity').addEventListener("keyup", event => {
    tq = document.getElementById('orderQuantity').value
    if (tq.length == 0) {
      totalQuantity = 0
    }
    else {
      totalQuantity = parseInt(tq)
    }
    productPrice = parseFloat(document.getElementById('productPrice').innerText)
    totalPayment = totalQuantity * productPrice
    maxDiscount = 0
    for( var i=0; i<offers.length; i++ ) {
      if( totalQuantity >= offers[i][0] ) {
        if( offers[i][1] >= maxDiscount ) {
          maxDiscount = offers[i][1]
        }
      }
    }
    document.getElementById('totalPayment').value = totalPayment
    document.getElementById('maxDiscount').value = maxDiscount
    document.getElementById('netPayment').value = parseInt((1-maxDiscount/100) * totalPayment)
    
    netPayment = parseInt((1-maxDiscount/100) * totalPayment)

    if( maxDiscount > 0 ) {
      document.getElementById('maxDiscountDiv').style.display = 'block'
      document.getElementById('netPaymentDiv').style.display = 'block'
    }
    else {
      document.getElementById('maxDiscountDiv').style.display = 'none'
      document.getElementById('netPaymentDiv').style.display = 'none'
    }
  })
  $("#notEnoughBalance").toast('hide');
}

var formValidation = function() {
  if( totalQuantity <= 0 ) {
    return false;
  }
  if( document.getElementById('paymentMethod2').checked ) {
    walletBalance = parseFloat(document.getElementById('walletBalance').value)
    if( walletBalance >= netPayment ) {
      return true;
    }
    else {
      $('#notEnoughBalance').toast('show');
      return false;
    }
  }
  return true;
}
