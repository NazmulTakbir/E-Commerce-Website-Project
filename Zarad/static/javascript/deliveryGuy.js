window.onload=function(){
  window.scrollTo({ top: 0, behavior: 'smooth' })
  const basicInfoForm = document.getElementById('basicInfoForm');
  const deliveredForm = document.getElementById('deliveredForm');
  const pendingDeliveriesForm = document.getElementById('pendingDeliveriesForm');
  const basicInfo = document.getElementById('basicInfo');
  const deliveredOrders = document.getElementById('deliveredOrders');
  const pendingDeliveries = document.getElementById('pendingDeliveries');

  document.getElementById("searchText").addEventListener("keydown", function(event) {
    if (event.keyCode == 13) {
      event.preventDefault();
      document.getElementById("searchIcon").click();
    }
  });

  basicInfoForm.style.display = 'block'
  deliveredForm.style.display = 'none'
  pendingDeliveriesForm.style.display = 'none'

  basicInfo.addEventListener('click', () => {
    basicInfoForm.style.display = 'block'
    deliveredForm.style.display = 'none'
    pendingDeliveriesForm.style.display = 'none'
  })

  deliveredOrders.addEventListener('click', () => {
    basicInfoForm.style.display = 'none'
    deliveredForm.style.display = 'block'
    pendingDeliveriesForm.style.display = 'none'
  })

  pendingDeliveries.addEventListener('click', () => {
    basicInfoForm.style.display = 'none'
    deliveredForm.style.display = 'none'
    pendingDeliveriesForm.style.display = 'block'
  })

  if( document.getElementById('firstPage').innerText == 'delivered' ) {
    document.getElementById('deliveredOrders').click()
  }
  else if( document.getElementById('firstPage').innerText == 'pending' ) {
    document.getElementById('pendingDeliveries').click()
  }

}

var fetchData = function(event) {
  var numbers = event.target.parentElement.previousElementSibling.innerText.split('+')
  var name = event.target.parentElement.previousElementSibling.previousElementSibling.innerText
  var sellerID = event.target.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.innerText
  var productID = event.target.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.innerText
  var productURL = event.target.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.innerText
  var orderID = event.target.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.innerText
  var deliveryCharge = event.target.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.innerText
  var totalPrice = event.target.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.innerText

  document.getElementById('orderID').innerText = orderID
  document.getElementById('productID').innerText = productID
  document.getElementById('sellerID').innerText = sellerID
  document.getElementById('productName').innerText = name
  document.getElementById('productName').href = productURL
  document.getElementById('itemNumbers').innerHTML = numbers.join("&nbsp;&nbsp;")
  document.getElementById('deliveryCharge').innerText = deliveryCharge+' Tk'
  document.getElementById('totalPrice').innerText = totalPrice+' Tk'
}

var allowPasswordChange = function(){
  document.getElementById('passwordChangeButton').style.display = 'none'
  document.getElementById('newPasswordDiv').style.display = 'block'
  document.getElementById('password2Div').style.display = 'block'
  document.getElementById('newPassword').required = true
  document.getElementById('password2').required = true
  document.getElementById('keepOldPassowordDiv').style.display = 'block'
}

var disallowPasswordChange = function(){
  document.getElementById('passwordChangeButton').style.display = 'block'
  document.getElementById('newPasswordDiv').style.display = 'none'
  document.getElementById('password2Div').style.display = 'none'
  document.getElementById('newPassword').required = false
  document.getElementById('password2').required = false
  document.getElementById('newPassword').value = ''
  document.getElementById('password2').value = ''
  document.getElementById('keepOldPassowordDiv').style.display = 'none'
}

var checkPassword = function() {
  if (document.getElementById('newPassword').value ==
    document.getElementById('password2').value ||
    document.getElementById('password2').value === '') {
    document.getElementById('cPassCheck').style.display = 'none';
  } else {
    document.getElementById('cPassCheck').style.display = 'block';;
  }
}

var basicInfoFormValidation = function() {
  var ok = false
  if( document.getElementById('newPassword').value ==
    document.getElementById('password2').value ) {
      ok = true
  }
  if( ok===false ) {
    $('html, body').animate({ scrollTop: 0 }, 'fast');
  }
  return ok
}
