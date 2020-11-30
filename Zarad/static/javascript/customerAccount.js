var walletBalance;
var afterDiscountPayment;
var deliveryCharge;

window.onload=function(){
  window.scrollTo({ top: 0, behavior: 'smooth' })

  deliveryCharge = parseFloat(document.getElementById('deliveryChargeInfo').innerText)

  const basicInfoForm = document.getElementById('basicInfoForm');
  const cartForm = document.getElementById('cartForm');
  const ordersForm = document.getElementById('ordersForm');
  const walletForm = document.getElementById('walletForm');
  const reviewsForm = document.getElementById('reviewsForm');
  const basicInfo = document.getElementById('basicInfo');
  const myCart = document.getElementById('myCart');
  const myOrders = document.getElementById('myOrders');
  const myWallet = document.getElementById('myWallet');
  const myReviews = document.getElementById('myReviews');

  document.getElementById("searchText").addEventListener("keydown", function(event) {
    if (event.keyCode == 13) {
      event.preventDefault();
      document.getElementById("searchIcon").click();
    }
  });

  basicInfoForm.style.display = 'block'
  cartForm.style.display = 'none'
  ordersForm.style.display = 'none'
  walletForm.style.display = 'none'
  reviewsForm.style.display = 'none'

  basicInfo.addEventListener('click', () => {
    basicInfoForm.style.display = 'block'
    cartForm.style.display = 'none'
    ordersForm.style.display = 'none'
    walletForm.style.display = 'none'
    reviewsForm.style.display = 'none'
  })

  myCart.addEventListener('click', () => {
    basicInfoForm.style.display = 'none'
    cartForm.style.display = 'block'
    ordersForm.style.display = 'none'
    walletForm.style.display = 'none'
    reviewsForm.style.display = 'none'
  })

  myOrders.addEventListener('click', () => {
    basicInfoForm.style.display = 'none'
    cartForm.style.display = 'none'
    ordersForm.style.display = 'block'
    walletForm.style.display = 'none'
    reviewsForm.style.display = 'none'
  })

  myWallet.addEventListener('click', () => {
    basicInfoForm.style.display = 'none'
    cartForm.style.display = 'none'
    ordersForm.style.display = 'none'
    walletForm.style.display = 'block'
    reviewsForm.style.display = 'none'
  })

  myReviews.addEventListener('click', () => {
    basicInfoForm.style.display = 'none'
    cartForm.style.display = 'none'
    ordersForm.style.display = 'none'
    walletForm.style.display = 'none'
    reviewsForm.style.display = 'block'
  })

  if( document.getElementById('firstPage').innerText == 'cart' ) {
    document.getElementById('myCart').click()
  }
  else if( document.getElementById('firstPage').innerText == 'reviews' ) {
    document.getElementById('myReviews').click()
  }
  else if( document.getElementById('firstPage').innerText == 'orders' ) {
    document.getElementById('myOrders').click()
  }
  else if( document.getElementById('firstPage').innerText == 'wallet' ) {
    document.getElementById('myWallet').click()
  }

  walletBalance = parseFloat( document.getElementById('walletBalance').innerText )

  $("#notEnoughBalance").toast('hide');
}

var displayOrder = function(event) {
  var netPayment = event.target.parentNode.previousElementSibling ;
  var discount = netPayment.previousElementSibling;
  var quantity = discount.previousElementSibling;
  var unitPrice = quantity.previousElementSibling;

  var productURL = unitPrice.previousElementSibling.previousElementSibling.firstChild.href;
  var productID = productURL.substring(productURL.length-32, productURL.length-17)
  var sellerID = productURL.substring(productURL.length-16, productURL.length-1)
  document.getElementById('productID').value = productID
  document.getElementById('sellerID').value = sellerID

  netPayment = parseInt(netPayment.innerText)
  discount = parseFloat(discount.innerText)
  quantity = parseInt(quantity.innerText)
  unitPrice = parseFloat(unitPrice.innerText)

  document.getElementById('quantity').value = quantity

  document.getElementById('totalPayment').value = unitPrice * quantity
  document.getElementById('maxDiscount').value = discount
  document.getElementById('paymentAfterDiscount').value = netPayment
  afterDiscountPayment = netPayment;
  document.getElementById('deliveryCharge').value = afterDiscountPayment * deliveryCharge
  document.getElementById('netPayment').value = parseInt( afterDiscountPayment * (1+deliveryCharge) )

  if( discount > 0 ) {
    document.getElementById('maxDiscountDiv').style.display = 'block'
    document.getElementById('paymentAfterDiscountDiv').style.display = 'block'
  }
  else {
    document.getElementById('maxDiscountDiv').style.display = 'none'
    document.getElementById('paymentAfterDiscountDiv').style.display = 'none'
  }

  document.getElementById('paymentMethod1').click()
}

var determineDeliveryCharge = function(){
  if( document.getElementById('paymentMethod2').checked ) {
    document.getElementById('deliveryChargeDiv').style.display = 'none'
    document.getElementById('netPaymentDiv').style.display = 'none'
    document.getElementById('finalPayment').value = afterDiscountPayment;
  }
  else {
    $("#notEnoughBalance").toast('hide');
    document.getElementById('deliveryChargeDiv').style.display = 'block'
    document.getElementById('netPaymentDiv').style.display = 'block'
    document.getElementById('deliveryCharge').value = afterDiscountPayment * deliveryCharge
    document.getElementById('netPayment').value = parseInt( afterDiscountPayment * (1+deliveryCharge) )
    document.getElementById('finalPayment').value = parseInt( afterDiscountPayment * (1+deliveryCharge) )
  }
}

var orderFormValidation = function(){
  if( document.getElementById('paymentMethod2').checked ) {
    walletBalance = parseFloat(document.getElementById('walletBalance').innerText)
    if( walletBalance >= afterDiscountPayment ) {
      return true;
    }
    else {
      $('#notEnoughBalance').toast('show');
      return false;
    }
  }
  return true;
}
