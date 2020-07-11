window.onload=function(){
  const basicInfoForm = document.getElementById('basicInfoForm');
  const deliveredForm = document.getElementById('deliveredForm');
  const pendingDeliveriesForm = document.getElementById('pendingDeliveriesForm');
  const basicInfo = document.getElementById('basicInfo');
  const deliveredOrders = document.getElementById('deliveredOrders');
  const pendingDeliveries = document.getElementById('pendingDeliveries');

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
