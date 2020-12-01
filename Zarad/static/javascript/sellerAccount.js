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

  document.getElementById("searchText").addEventListener("keydown", function(event) {
    if (event.keyCode == 13) {
      event.preventDefault();
      document.getElementById("searchIcon").click();
    }
  });

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

  if( document.getElementById('firstPage').innerText == 'products' ) {
    document.getElementById('myProducts').click()
  }
  else if( document.getElementById('firstPage').innerText == 'offers' ) {
    document.getElementById('myOffers').click()
  }
  else if( document.getElementById('firstPage').innerText == 'advertisements' ) {
    document.getElementById('myAdverts').click()
  }
  else if( document.getElementById('firstPage').innerText == 'transactions' ) {
    document.getElementById('myWallet').click()
  }
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

var allowPasswordChange = function(){
  document.getElementById('passwordChangeButton').style.display = 'none'
  document.getElementById('sellerNewPasswordDiv').style.display = 'block'
  document.getElementById('sellerPassword2Div').style.display = 'block'
  document.getElementById('sellerNewPassword').required = true
  document.getElementById('sellerPassword2').required = true
  document.getElementById('keepOldPassowordDiv').style.display = 'block'
}

var disallowPasswordChange = function(){
  document.getElementById('passwordChangeButton').style.display = 'block'
  document.getElementById('sellerNewPasswordDiv').style.display = 'none'
  document.getElementById('sellerPassword2Div').style.display = 'none'
  document.getElementById('sellerNewPassword').required = false
  document.getElementById('sellerPassword2').required = false
  document.getElementById('sellerNewPassword').value = ''
  document.getElementById('sellerPassword2').value = ''
  document.getElementById('keepOldPassowordDiv').style.display = 'none'
}

var checkPassword = function() {
  if (document.getElementById('sellerNewPassword').value ==
    document.getElementById('sellerPassword2').value ||
    document.getElementById('sellerPassword2').value === '') {
    document.getElementById('cPassCheck').style.display = 'none';
  } else {
    document.getElementById('cPassCheck').style.display = 'block';;
  }
}

var basicInfoFormValidation = function() {
  var ok = false
  if( document.getElementById('sellerNewPassword').value ==
    document.getElementById('sellerPassword2').value ) {
      ok = true
  }
  if( ok===false ) {
    $('html, body').animate({ scrollTop: 0 }, 'fast');
  }
  return ok
}
