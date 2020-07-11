window.onload=function(){
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
}
