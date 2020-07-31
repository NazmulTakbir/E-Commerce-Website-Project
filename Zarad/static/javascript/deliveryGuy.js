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
}

var fetchData = function(event) {
  var numbers = event.target.parentElement.previousElementSibling.innerText.split('+')
  var name = event.target.parentElement.previousElementSibling.previousElementSibling.innerText
  var sellerID = event.target.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.innerText
  var productID = event.target.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.innerText
  var productURL = event.target.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.innerText
  var orderID = event.target.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.innerText

  document.getElementById('orderID').innerText = orderID
  document.getElementById('productID').innerText = productID
  document.getElementById('sellerID').innerText = sellerID
  document.getElementById('productName').innerText = name
  document.getElementById('productName').href = productURL
  document.getElementById('itemNumbers').innerHTML = numbers.join("&nbsp;&nbsp;")
}
