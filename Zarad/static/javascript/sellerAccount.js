window.onload=function(){
  const basicInfoForm = document.getElementById('basicInfoForm');
  const productsForm = document.getElementById('productsForm');
  const offersForm = document.getElementById('offersForm');
  const advertForm = document.getElementById('advertForm');
  const walletForm = document.getElementById('walletForm');
  const basicInfo = document.getElementById('basicInfo');
  const myProducts = document.getElementById('myProducts');
  const myOffers = document.getElementById('myOffers');
  const myAdverts = document.getElementById('myAdverts');
  const myWallet = document.getElementById('myWallet');

  basicInfoForm.style.display = 'block'
  productsForm.style.display = 'none'
  offersForm.style.display = 'none'
  advertForm.style.display = 'none'
  walletForm.style.display = 'none'
  var temp = document.getElementById('advertImage')
  if( temp ) {
    temp.style.display = 'none'
  }

  basicInfo.addEventListener('click', () => {
    basicInfoForm.style.display = 'block'
    productsForm.style.display = 'none'
    offersForm.style.display = 'none'
    advertForm.style.display = 'none'
    walletForm.style.display = 'none'
  })

  myProducts.addEventListener('click', () => {
    basicInfoForm.style.display = 'none'
    productsForm.style.display = 'block'
    offersForm.style.display = 'none'
    advertForm.style.display = 'none'
    walletForm.style.display = 'none'
  })

  myOffers.addEventListener('click', () => {
    basicInfoForm.style.display = 'none'
    productsForm.style.display = 'none'
    offersForm.style.display = 'block'
    advertForm.style.display = 'none'
    walletForm.style.display = 'none'
  })

  myAdverts.addEventListener('click', () => {
    basicInfoForm.style.display = 'none'
    productsForm.style.display = 'none'
    offersForm.style.display = 'none'
    advertForm.style.display = 'block'
    walletForm.style.display = 'none'
  })

  myWallet.addEventListener('click', () => {
    basicInfoForm.style.display = 'none'
    productsForm.style.display = 'none'
    offersForm.style.display = 'none'
    advertForm.style.display = 'none'
    walletForm.style.display = 'block'
  })
}

function uploadPicture(event) {
  var image = document.getElementById('advertImage');
	if (event.target.files && event.target.files[0]) {
		image.src = URL.createObjectURL(event.target.files[0]);
		image.onload = function() {
			image.style.width = '150px';
			image.style.height = 'auto';
			URL.revokeObjectURL(image.src) // free memory
		}
		document.getElementById('advertImage').style.display = 'block'
	} else {
		image.src = "#"
		document.getElementById('advertImage').style.display = 'none'
	}
}
