window.onload=function(){

  document.getElementById("searchText").addEventListener("keydown", function(event) {
    if (event.keyCode == 13) {
      event.preventDefault();
      document.getElementById("searchIcon").click();
    }
  });
  
  document.getElementById('rechargeRadio').addEventListener('click', () => {
    document.getElementById('walletRechargeForm').style.display = 'block'
    document.getElementById('walletWithdrawForm').style.display = 'none'
  })

  document.getElementById('withdrawRadio').addEventListener('click', () => {
    document.getElementById('walletRechargeForm').style.display = 'none'
    document.getElementById('walletWithdrawForm').style.display = 'block'
  })

  document.getElementById('rechargeRadio').click()
}

window.onbeforeunload = function () {
   document.getElementById('rechargeRadio').click()
}
